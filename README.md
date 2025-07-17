# Should This Be AI? – MESD AI Tool Advisor

This Streamlit app helps Multnomah Education Service District (MESD) staff evaluate whether and how artificial intelligence (AI) might support a specific project or situation. It asks clarifying questions, surfaces tradeoffs, and offers grounded recommendations—sometimes suggesting *no AI at all*.

## 👥 Who It’s For
District support staff, central office teams, and others exploring how AI can (or can’t) help with a work-related challenge or idea.

## 🤖 What It Does
- Simulates a thoughtful AI advisor built for MESD’s context
- Collects name and email for light internal usage tracking
- Uses OpenAI’s GPT-4 model to:
  - Ask clarifying questions
  - Recommend or rule out AI use
  - Suggest tools like summarization, web search, or image generation

## 🛠️ Tech Stack
- [Streamlit](https://streamlit.io/) for the front-end interface
- [OpenAI GPT-4 API](https://platform.openai.com/docs/models/gpt-4) for conversation logic

## 🔒 Data & Privacy
- No personally identifiable information (PII) is stored or shared
- All responses are generated in real-time, not logged externally

## 🚀 How to Run Locally
1. Clone the repo
2. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=your-key-here
Run the app:

bash
Copy
Edit
streamlit run app.py
📫 Contact
Questions? Contact Ben Baldizon, Program Manager for AI Innovation & Capacity Building.
