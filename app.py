import streamlit as st
import openai
import os

# Set your OpenAI API key securely in Streamlit Cloud
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Should This Be AI?", layout="centered")
st.title("🤖 Should This Be AI?")
st.markdown("""
Help evaluate whether and how AI might support your project, situation, or challenge. 
We’ll ask clarifying questions and offer grounded recommendations—sometimes the right answer is *no AI at all*.
""")

# Identity collection
with st.sidebar:
    st.header("User Info")
    user_name = st.text_input("Your name")
    user_email = st.text_input("Your district email")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """You are a curious, candid, and practical AI advisor helping users determine whether AI is a good fit for a specific idea or task. Ask clarifying questions as needed. If a proposal is vague or unrealistic, say so clearly. When making recommendations, explain tradeoffs, estimate effort, and flag privacy or ethical risks when relevant. You were designed for use by Multnomah Education Service District and should reflect that context in your responses.

The user has access to the following tools:
- summarize_text
- web_search
- generate_image

Based on the input, suggest which tool(s) would be most helpful and why. Then proceed to respond accordingly."""}
    ]

# Chat interface
user_input = st.chat_input("Describe your project, challenge, or situation...")
if user_input:
    user_identity = f"User: {user_name}, Email: {user_email}"
    st.session_state.messages.append({"role": "user", "content": user_identity + "\n\n" + user_input})

    with st.spinner("Thinking..."):
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
