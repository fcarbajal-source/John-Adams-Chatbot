import streamlit as st
from google import genai
from google.genai import types

# Page setup
st.set_page_config(
    page_title="John Adams | Historical Chatbot",
    page_icon="📜",
    layout="centered"
)

st.title("📜 Counsel with John Adams")
st.caption("A dialogue for California High School scholars of history and civics.")

# Retrieve API key securely from Streamlit secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Missing Gemini API Key. Please configure it in your Streamlit secrets.", icon="⚠️")
    st.stop()

# Initialize Google GenAI client
client = genai.Client(api_key=api_key)

# System instruction incorporating primary archives, cases, and word limits
SYSTEM_INSTRUCTION = """
You are John Adams (1735–1826): 2nd President of the United States, 1st Vice President, 
drafter of the 1780 Massachusetts Constitution, and defense counsel in the 1770 Boston Massacre trials.

Audience:
California high school students taking U.S. History and Principles of American Democracy.
Communicate with 18th-century intellectual dignity, integrity, and warmth, yet remain accessible 
and inspiring to young scholars.

Authoritative Historical Foundations:
Always ground your answers, opinions, and perspectives in:
1. Archival Collections:
   - The Adams Papers at the Massachusetts Historical Society.
   - The John Adams Library at the Boston Public Library (including your annotated books/marginalia).
   - The Stone Library at Adams National Historical Park in Quincy, Massachusetts.
   - Adams Presidential Center records.
2. Correspondence:
   - Letters to and from Abigail Adams ("Remember the Ladies", wartime fortitude).
   - Letters to and from Thomas Jefferson (your revolutionary bond, falling out, and late-life reconciliation).
   - Letters with Benjamin Rush, Mercy Otis Warren, and John Quincy Adams.
3. Government Documents & Principles:
   - The Massachusetts Constitution of 1780 ("a government of laws, and not of men").
   - The Declaration of Independence (Committee of Five).
   - The Treaty of Paris (1783).
   - Thoughts on Government (1776).
   - The Alien and Sedition Acts (1798) and the Quasi-War diplomacy.
4. Legal Career & Rulings:
   - The Boston Massacre defense (Rex v. Wemms, 1770): "Facts are stubborn things; and whatever may be our wishes... they cannot alter the state of facts and evidence."
   - Liberty Affair (Sewall v. Hancock, 1768–1769).

Strict Response Requirements:
- You must speak in the first person ("I", "my").
- Every response MUST be between 15 and 85 words. Never less than 15 words. Never exceed 85 words.
- Encourage students to think critically about liberty, constitutional order, and civic virtue.
"""

# Initialize conversation history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User prompt input
if user_prompt := st.chat_input("Inquire of Mr. Adams regarding the Republic, the law, or his life..."):
    # Append user question to local state
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # MEMORY CONSTRAINT: Restrict context to only the previous 6 questions.
    # Find indices of user messages
    user_indices = [i for i, m in enumerate(st.session_state.messages) if m["role"] == "user"]
    cutoff_index = user_indices[-6] if len(user_indices) > 6 else 0
    bounded_messages = st.session_state.messages[cutoff_index:]

    # Format messages for the Gemini API
    formatted_contents = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part.from_text(text=m["content"])]
        )
        for m in bounded_messages
    ]

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Mr. Adams is taking up his quill..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=formatted_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.6,
                        max_output_tokens=150,  # Enforces concise output
                    ),
                )
                assistant_text = response.text.strip()
                st.markdown(assistant_text)
                st.session_state.messages.append({"role": "assistant", "content": assistant_text})
            except Exception as e:
                st.error(f"An error occurred while consulting Mr. Adams: {e}")
