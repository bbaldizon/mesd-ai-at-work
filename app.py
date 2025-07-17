import streamlit as st
import openai
import os

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
    st.session_state.messages.append({"role": "user", "content": user_identity + "\n\n" + user_input})

    with st.spinner("Thinking through your AI options..."):
        response = openai.ChatCompletion.create(
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
