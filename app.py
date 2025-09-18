import streamlit as st
import openai
import os
import requests
import json
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Custom GPT Assistant", layout="centered")
st.title("🎯 Build Your Custom GPT")
st.markdown("""
This assistant helps you design your own custom GPT by walking through key setup questions. 
Answer naturally and revise at the end before copying your instructions into the custom GPT builder.
""")

# Feature toggles
ENABLE_FILE_UPLOAD = True
ENABLE_WEB_SEARCH = True
ENABLE_IMAGE_GEN = True

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

# Optional tools section
st.subheader("🧰 Optional Tools")

uploaded_file = None
search_query = None
image_prompt = None

tool_inputs = []

if ENABLE_FILE_UPLOAD:
    uploaded_file = st.file_uploader("📄 Upload a file (PDF, DOCX, TXT)")
    if uploaded_file is not None:
        content = uploaded_file.read().decode(errors="ignore")
        tool_inputs.append(f"The user uploaded a file with content:\n{content[:1000]}")

if ENABLE_WEB_SEARCH:
    search_query = st.text_input("🌐 Enter a web search query (optional)")
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

if ENABLE_IMAGE_GEN:
    image_prompt = st.text_input("🎨 Image prompt (optional)")
    if image_prompt:
        try:
            image_response = openai.Image.create(prompt=image_prompt, n=1, size="512x512")
            image_url = image_response['data'][0]['url']
            image = Image.open(BytesIO(requests.get(image_url).content))
            st.image(image, caption="Generated Image")
            tool_inputs.append(f"Generated image from prompt: {image_prompt}")
        except:
            st.error("Image generation failed.")

# Load system instructions from external file
@st.cache_data
def load_instructions():
    with open("instructions.txt", "r") as f:
        return f.read()

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": load_instructions()}
    ]

# Chat interface
user_input = st.chat_input("What kind of custom GPT do you want to build?")
if user_input:
    user_identity = f"User: {user_name}, Email: {user_email}"
    full_input = user_identity + "\n\n" + user_input
    if tool_inputs:
        full_input += "\n\n" + "\n\n".join(tool_inputs)
    st.session_state.messages.append({"role": "user", "content": full_input})

    with st.spinner("Thinking through your assistant design..."):
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
