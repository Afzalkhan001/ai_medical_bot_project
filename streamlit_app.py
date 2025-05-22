import streamlit as st
import re
import time
from medical_chatbot_voice import validate_age, extract_age, validate_yesno, normalize_yesno, validate_symptom, extract_symptom
from streamlit_voice_helper import voice_input, speak_text

st.set_page_config(page_title="Medical Chatbot", page_icon="🩺", layout="centered")
st.title("🩺 Medical Virtual Health Assistant")
st.markdown("""
Welcome! I am your virtual health assistant. I will ask you some questions about your health and give you basic advice.\
If you need help at any time, just ask.\
**For best results, use text input. Voice input/output is experimental and works best in Chrome.**
""")

# --- Helper Functions ---
def chatbot_ask(question, key, validate_func=None, normalize_func=None, allowed=None, extract_func=None):
    response = ""
    attempts = 0
    st.markdown(f"**{question}**")
    # Voice input button
    transcript = voice_input(label=f"Speak your answer for {key}", key=key)
    if transcript:
        st.info(f"Voice input: {transcript}")
        response = transcript
    else:
        response = st.text_input("Or type your answer:", key=f"{key}_{attempts}")
    if st.button(f"Submit {key}", key=f"submit_{key}_{attempts}"):
        if response.strip().lower() == "skip":
            st.info("Skipping this question.")
            return "skipped"
        if extract_func:
            response = extract_func(response, allowed) if allowed else extract_func(response)
        if validate_func:
            if (allowed is not None and validate_func(response, allowed)) or (allowed is None and validate_func(response)):
                if normalize_func:
                    response = normalize_func(response)
                st.success(f"You answered: {response}")
                speak_text(response, key=f"tts_{key}")
                return response
            else:
                st.warning("Sorry, I did not understand. Please try again or type 'skip' to move on.")
                time.sleep(1)
                st.experimental_rerun()
        else:
            speak_text(response, key=f"tts_{key}")
            return response
    else:
        st.stop()

# --- Chatbot Flow ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'step' not in st.session_state:
    st.session_state.step = 0

steps = [
    {
        'question': "What is your age?",
        'key': 'age',
        'validate_func': validate_age,
        'extract_func': extract_age,
    },
    {
        'question': "Do you have a fever? (yes/no)",
        'key': 'fever',
        'validate_func': validate_yesno,
        'normalize_func': normalize_yesno,
    },
    {
        'question': "Are you experiencing cough or chest pain? (yes/no)",
        'key': 'cough',
        'validate_func': validate_yesno,
        'normalize_func': normalize_yesno,
    },
    {
        'question': "Do you have any chronic conditions? (diabetes/hypertension/asthma/heart disease/none)",
        'key': 'chronic',
        'validate_func': validate_symptom,
        'extract_func': extract_symptom,
        'allowed': ["diabetes", "hypertension", "asthma", "heart disease", "none"]
    }
]

for i, step in enumerate(steps):
    if st.session_state.step == i:
        answer = chatbot_ask(
            step['question'],
            step['key'],
            validate_func=step.get('validate_func'),
            normalize_func=step.get('normalize_func'),
            allowed=step.get('allowed'),
            extract_func=step.get('extract_func')
        )
        st.session_state.chat_history.append({"question": step['question'], "answer": answer})
        st.session_state.step += 1
        st.experimental_rerun()

# --- Show chat history so far ---
st.markdown("## Conversation so far:")
for entry in st.session_state.chat_history:
    st.markdown(f"**Q:** {entry['question']}  ")
    st.markdown(f"**A:** {entry['answer']}")

# --- Final Suggestion (simulate AI follow-up) ---
if st.session_state.step == len(steps):
    # Compose summary
    user_summary = "\n".join([f"{e['question']} {e['answer']}" for e in st.session_state.chat_history])
    st.markdown("---")
    st.markdown("### Suggestion:")
    st.info("Given your responses, please monitor your symptoms. If you experience any worsening or new symptoms, seek immediate medical attention. Please consult our doctor for further advice.")
    st.success("Thank you for using the Medical Virtual Health Assistant!")
    st.session_state.step += 1

# --- Reset button ---
if st.button("Restart Chatbot"):
    st.session_state.chat_history = []
    st.session_state.step = 0
    st.experimental_rerun()
