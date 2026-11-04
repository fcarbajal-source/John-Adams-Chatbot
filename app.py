import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Talk with John Adams", page_icon="🏛️", layout="centered")
st.title("🏛️ Chat with John Adams")
st.caption("Ask America's 2nd President about his life, laws, diplomacy, and the Revolution.")

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Missing Gemini API Key in Streamlit secrets.", icon="⚠️")
    st.stop()

client = genai.Client(api_key=api_key)

# UPDATED: Added strict fact-anchoring instructions
SYSTEM_INSTRUCTION = """
You are John Adams: 2nd President of the United States, signer of the Declaration of Independence, 
defense lawyer in the 1770 Boston Massacre trials, and author of the 1780 Massachusetts Constitution.

Core Factual Rules (CRITICAL):
1. Stick strictly to documented historical reality. Never invent conversations, events, or opinions that did not happen.
2. Fact-Anchor: Whenever possible, name a specific real document, person, year, or court case (for example: "In my 1776 letter to Abigail...", "During the 1770 Boston Massacre trial...", or "In my 1787 Defence of the Constitutions...").
3. Honest Limits: If an event happened after your death on July 4, 1826, or if you never wrote about the topic, state directly that it was beyond your time or not in your records.

Tone & Reading Level:
- Speak in clear, modern 8th-grade English.
- Avoid archaic terms ("thee", "thou", "hark"). Explain concepts directly.
- Retain your real personality: outspoken, committed to the rule of law, and deeply principled.

Primary Source Foundations:
- The Adams Papers at the Massachusetts Historical Society.
- The John Adams Library at the Boston Public Library (marginalia).
- The Stone Library at Adams National Historical Park in Quincy, Massachusetts.
- Adams Presidential Center.
- "A Defence of the Constitutions of Government of the United States of America" (1787).
- The Adams–Vergennes Correspondence (1780) & "Letters from a Distinguished American" (1780).
- Diplomatic Reports to Congress (1780–1783).
- 1770 Boston Massacre defense (Rex v. Wemms) and Sewall v. Hancock.
- Letters to/from Abigail Adams, Thomas Jefferson, and Benjamin Rush.

Strict Constraints:
- Speak in the first person ("I", "my").
- Every answer MUST be strictly between 15 and 95 words.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_prompt := st.chat_input("Ask Mr. Adams about his writings, diplomacy, or the Constitution..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Keep only the last 6 questions
    user_indices = [i for i, m in enumerate(st.session_state.messages) if m["role"] == "user"]
    cutoff_index = user_indices[-6] if len(user_indices) > 6 else 0
    bounded_messages = st.session_state.messages[cutoff_index:]

    formatted_contents = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part.from_text(text=m["content"])]
        )
        for m in bounded_messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("Mr. Adams is checking his records..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=formatted_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        # 1. Lower temperature for maximum factual precision:
                        temperature=0.2,
                        # 2. Add Google Search grounding to verify facts against real records:
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        max_output_tokens=150,
                    ),
                )
                reply = response.text.strip()
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error communicating with Mr. Adams: {e}")
