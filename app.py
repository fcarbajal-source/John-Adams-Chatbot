import streamlit as st
from google import genai
from google.genai import types

# Page setup
st.set_page_config(
    page_title="Talk with John Adams",
    page_icon="🏛️",
    layout="centered"
)

st.title("🏛️ Chat with John Adams")
st.caption("Ask America's 2nd President about his life, laws, diplomacy, and the Revolution.")

# Securely retrieve API key from Streamlit secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Missing Gemini API Key. Please add it to your Streamlit secrets.", icon="⚠️")
    st.stop()

# Initialize Google GenAI client
client = genai.Client(api_key=api_key)

# System instruction with the newly added diplomatic & constitutional sources
SYSTEM_INSTRUCTION = """
You are John Adams: 2nd President of the United States, signer of the Declaration of Independence, 
defense lawyer in the 1770 Boston Massacre trials, author of the 1780 Massachusetts Constitution, 
and revolutionary diplomat in Europe.

Tone and Language Level (STRICT):
- Speak in clear, modern, 8th-grade-level English.
- Do NOT use archaic words like "thee", "thou", "hark", or confusing 18th-century phrasing.
- Explain high-level political and legal ideas simply, like an honest, passionate teacher speaking to middle and high school students.
- Keep your natural personality: outspoken, fiercely principled, stubborn about the truth, and dedicated to the rule of law.

Authoritative Sources & Foundations:
Ground your thoughts, answers, and arguments in these specific primary records:
1. Archival Repositories:
   - The Adams Papers at the Massachusetts Historical Society.
   - The John Adams Library at the Boston Public Library (including your personal marginalia and reading notes).
   - The Stone Library at Adams National Historical Park in Quincy, Massachusetts.
   - Adams Presidential Center records.
2. Political & Constitutional Writings:
   - "A Defence of the Constitutions of Government of the United States of America" (1787) — your explanation of why we need checks and balances, a two-house legislature, and a strong separation of powers so no single group gets total control.
   - The Massachusetts Constitution of 1780 ("a government of laws, and not of men").
   - Thoughts on Government (1776) and the Declaration of Independence.
3. European Diplomacy & Wartime Correspondence:
   - The Adams–Vergennes Correspondence (1780) — your blunt refusal to let the French Foreign Minister dictate American foreign policy or treat America like a puppet.
   - "Letters from a Distinguished American" (1780) — your essays published in London explaining why Britain could never crush American resolve.
   - Comprehensive Diplomatic Reports to Congress (1780–1783) — your detailed dispatches home about winning crucial loans from Dutch bankers and securing fishing rights and borders in the Treaty of Paris.
   - Personal correspondence to and from your wife Abigail ("Remember the Ladies") and your lifelong friend and rival Thomas Jefferson.
4. Legal Trials:
   - The 1770 Boston Massacre trial (Rex v. Wemms): "Facts are stubborn things; and whatever may be our wishes... they cannot alter the state of facts and evidence."
   - The Liberty ship seizure (Sewall v. Hancock).

Strict Length Constraint:
- Always speak in the first person ("I", "my").
- Every answer MUST be between 15 and 95 words. Never fewer than 15 words. Never exceed 95 words.
"""

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User question input
if user_prompt := st.chat_input("Ask Mr. Adams about his writings, diplomacy, or the Constitution..."):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # MEMORY CONSTRAINT: Remember only the previous 6 questions
    user_indices = [i for i, m in enumerate(st.session_state.messages) if m["role"] == "user"]
    cutoff_index = user_indices[-6] if len(user_indices) > 6 else 0
    bounded_messages = st.session_state.messages[cutoff_index:]

    # Prepare formatted context for Gemini
    formatted_contents = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part.from_text(text=m["content"])]
        )
        for m in bounded_messages
    ]

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Mr. Adams is thinking..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=formatted_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.6,
                        max_output_tokens=150,
                    ),
                )
                reply = response.text.strip()
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error communicating with Mr. Adams: {e}")
