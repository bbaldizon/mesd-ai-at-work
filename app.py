import streamlit as st
import openai
import os
import requests
import json
import gspread
from PIL import Image
from io import BytesIO
from oauth2client.service_account import ServiceAccountCredentials

# Set your OpenAI API key securely in Streamlit Cloud
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Should This Be AI?", layout="centered")
st.title("🤖 Should This Be AI?")
st.markdown("""
Use this tool to explore whether and how AI might support a project or situation you're working on. The assistant will ask clarifying questions and offer grounded, honest recommendations.
""")

# Access code gate
access_code = st.sidebar.text_input("Access code", type="password")
if access_code != st.secrets["ACCESS_CODE"]:
    st.warning("Please enter a valid access code to use this tool.")
    st.stop()

# Identity collection
with st.sidebar:
    st.header("User Info")
    user_name = st.text_input("Your name")
    user_email = st.text_input("Your district email")

# Google Sheets logging setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GSHEET_JSON"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gs_client = gspread.authorize(creds)
sheet = gs_client.open("MESD AI Access Log").sheet1

# Tool Panel
st.subheader("🧰 Optional Tools")
st.markdown("Use these only if the assistant suggests or you feel it will help.")

uploaded_file = st.file_uploader("📄 Upload a file (PDF, DOCX, TXT)")
search_query = st.text_input("🌐 Enter a web search query (optional)")
generate_image_prompt = st.text_input("🎨 Image prompt (optional)")

# Process tool inputs
tool_inputs = []
if uploaded_file is not None:
    content = uploaded_file.read().decode(errors="ignore")
    tool_inputs.append(f"The user uploaded a file with content:\n{content[:1000]}")

if search_query:
    try:
        serp_api_key = st.secrets["SERP_API_KEY"]
        serp_url = f"https://serpapi.com/search.json?q={search_query}&api_key={serp_api_key}"
        result = requests.get(serp_url).json()
        snippets = [res['snippet'] for res in result.get('organic_results', []) if 'snippet' in res]
        search_result = "\n\n".join(snippets[:5])
        tool_inputs.append(f"Search results for '{search_query}':\n{search_result}")
    except:
        tool_inputs.append("Web search failed.")

if generate_image_prompt:
    try:
        image_response = openai.Image.create(prompt=generate_image_prompt, n=1, size="512x512")
        image_url = image_response['data'][0]['url']
        image = Image.open(BytesIO(requests.get(image_url).content))
        st.image(image, caption="Generated Image")
        tool_inputs.append(f"Generated image from prompt: {generate_image_prompt}")
    except:
        st.error("Image generation failed.")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """You are a curious, candid, and practical assistant who helps users evaluate whether and how AI could support a specific project or situation. Offer realistic, thoughtful recommendations—sometimes the best answer is no AI at all.

Begin by asking if the user has memory enabled. If so, ask:
“Would you like me to use what you’ve shared before (like preferences or past projects) to help with this conversation? If not, I won’t use memory this session.” Only use memory if the user explicitly agrees.

Encourage users to describe their project in their own words. Ask clarifying questions like:
- What are your goals or outcomes?
- Who’s involved, and who would maintain a solution?
- What tools, systems, or constraints should I know about?
- What are the most important things you’re looking for (e.g., speed, cost, equity)?

When offering solutions, start with a high-level recommendation and a summary of investment needed. Offer 2–3 options with pros/cons when relevant.

If the user selects an option, provide a breakdown of time, staffing, tools, and IT support required.

Always flag risks (PII use, equity, privacy, sustainability, ripple effects).

Be honest when the idea is vague or unlikely to work. Use prompts like:
“This may be too vague to advise on—can you sharpen the idea?”
“This idea is unlikely to work as described. Want to explore a related approach?”

Let the user know if you’re asking lots of clarifying questions.
Remind users never to input student or staff PII into tools unless approved by IT.

This tool was designed for MESD staff and partners. Refer users to Ben Baldizon or Katy Tibbs if they need support."""}
    ]

# Chat interface
user_input = st.chat_input("What's your project or challenge?")
if user_input:
    user_identity = f"User: {user_name}, Email: {user_email}"
    full_input = user_identity + "\n\n" + user_input
    if tool_inputs:
        full_input += "\n\n" + "\n\n".join(tool_inputs)
    st.session_state.messages.append({"role": "user", "content": full_input})

    # Log to Google Sheet
    sheet.append_row([user_name, user_email, user_input])

    with st.spinner("Thinking through your AI options..."):
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=st.session_state.messages,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})

# Display chat history
for msg in st.session_state.messages[1:]:  # Skip system prompt in display
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
