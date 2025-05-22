# --- Imports ---
import os
#from transformers import AutoProcessor, AutoModelForImageTextToText
import speech_recognition as sr
import pyttsx3
from huggingface_hub import login

import requests
import speech_recognition as sr
import pyttsx3
import json
import os
import re
import time

# --- OpenRouter API Settings ---
OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "mistralai/devstral-small:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# --- Text-to-Speech Engine ---
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# --- Voice Input Helper ---
def get_voice_input(prompt):
    # Only print/speak once
    print(prompt)
    speak(prompt)
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except Exception as e:
        print(f"Sorry, I could not understand you. Let's try typing for this question.")
        speak("Sorry, I could not understand you. Let's try typing for this question.")
        return input("Please type your answer and press Enter: ")

# --- Input Mode (set once at start) ---
input_mode = None

def get_user_input(prompt, validate_func=None, normalize_func=None, allowed=None, extract_func=None):
    global input_mode
    attempts = 0
    last_prompt = None
    while True:
        if last_prompt != prompt:
            print(prompt)
            speak(prompt)
            last_prompt = prompt
        if input_mode == 'voice':
            answer = get_voice_input("")  # Don't repeat prompt
        else:
            answer = input("Please type your answer and press Enter: ")
        # Accessibility: allow "repeat" or silence to repeat the question
        if answer.strip().lower() in ["repeat", "please repeat", "say again", "what?"] or not answer.strip():
            print("Repeating the question...")
            speak("Repeating the question.")
            continue
        if answer.strip().lower() == "skip":
            print("Skipping this question.")
            speak("Skipping this question.")
            return "skipped"
        # Always extract first if extract_func is provided
        if extract_func:
            extracted = extract_func(answer, allowed) if allowed else extract_func(answer)
            answer = extracted
        # Validate
        if validate_func:
            if (allowed is not None and validate_func(answer, allowed)) or (allowed is None and validate_func(answer)):
                if normalize_func:
                    answer = normalize_func(answer)
                if attempts > 0 and input_mode == 'text':
                    print(f"You entered: {answer}. Thank you.")
                    speak(f"You entered: {answer}. Thank you.")
                return answer
            else:
                attempts += 1
                if attempts == 1:
                    print("Sorry, I did not understand. Please try again or type 'skip' to move on.")
                    speak("Sorry, I did not understand. Please try again or say skip to move on.")
                elif attempts == 2 and input_mode == 'voice':
                    print("Let's switch to typing for this question.")
                    speak("Let's switch to typing for this question.")
                    input_mode_backup = input_mode
                    input_mode = 'text'
                    continue
                elif attempts > 2:
                    print("If you need help, please ask someone nearby or type 'skip'.")
                    speak("If you need help, please ask someone nearby or say skip.")
                    return "skipped"
        else:
            return answer
        time.sleep(1)

# --- OpenRouter Chat Function ---
def ask_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful medical assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 256,
        "temperature": 0.7
    }
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"[ERROR] OpenRouter API: {e}")
        return "⚠️ Sorry, couldn't get a response from the AI."

# --- Response Validation ---
def extract_age(ans):
    # Accepts 'I am 25', 'My age is 25', 'twenty five', etc.
    ans = ans.lower()
    # Try to extract a number
    match = re.search(r'(\d{1,3})', ans)
    if match:
        return match.group(1)
    # Optionally: convert written numbers (not implemented here)
    return ans.strip()

def validate_age(age):
    try:
        age_num = int(age)
        return 0 < age_num < 120
    except:
        return False

# Robust yes/no validation for conversational answers
# Accepts phrases like "yes I have a fever", "no, I am fine", etc.
def validate_yesno(ans):
    ans = ans.lower().strip()
    yes_keywords = ["yes", "yeah", "yep", "of course", "i have", "i do", "affirmative", "sure", "correct"]
    no_keywords = ["no", "not", "don't", "do not", "never", "none", "negative", "i don't", "i do not"]
    # Ambiguity: both yes and no words
    if any(y in ans for y in yes_keywords) and any(n in ans for n in no_keywords):
        return False  # ambiguous
    # Accept if any yes/no keyword appears anywhere
    for y in yes_keywords:
        if y in ans:
            return True
    for n in no_keywords:
        if n in ans:
            return True
    # fallback: if only yes/no present
    return ans in ["yes", "no", "y", "n"]


def normalize_yesno(ans):
    ans = ans.lower().strip()
    yes_keywords = ["yes", "yeah", "yep", "of course", "i have", "i do", "affirmative", "sure", "correct"]
    no_keywords = ["no", "not", "don't", "do not", "never", "none", "negative", "i don't", "i do not"]
    for y in yes_keywords:
        if ans.startswith(y) or f" {y}" in ans:
            return "yes"
    for n in no_keywords:
        if ans.startswith(n) or f" {n}" in ans:
            return "no"
    # fallback
    if ans in ["yes", "y"]:
        return "yes"
    if ans in ["no", "n"]:
        return "no"
    return ans  # fallback: return original

def extract_symptom(ans, allowed):
    # Accepts 'I have asthma', 'My doctor said I have hypertension', etc.
    ans = ans.lower()
    for item in allowed:
        if item in ans:
            return item
    return ans.strip()

def validate_symptom(symptom, allowed):
    # Accept if any allowed word is present in the answer
    return any(item in symptom.lower() for item in allowed)

# --- Main Chatbot Flow ---
def medical_chatbot():
    print("\nHello! I'm your virtual health assistant.")
    speak("Hello! I'm your virtual health assistant.")
    print("I will ask you some questions about your health and give you basic advice.")
    speak("I will ask you some questions about your health and give you basic advice.")
    print("If you need help at any time, just ask.")
    speak("If you need help at any time, just ask.")

    global input_mode
    # Ask once for input mode at the start
    while True:
        mode_choice = input("\nWould you like to speak your answers or type them?\nType 'v' for voice, or press Enter for typing: ").strip().lower()
        if mode_choice == 'v':
            input_mode = 'voice'
            print("You can answer by speaking after each question.")
            speak("You can answer by speaking after each question.")
            break
        elif mode_choice == '':
            input_mode = 'text'
            print("You can answer by typing after each question.")
            speak("You can answer by typing after each question.")
            break
        else:
            print("Sorry, I did not understand. Please type 'v' for voice or just press Enter for typing.")
            speak("Sorry, I did not understand. Please type v for voice or just press Enter for typing.")

    conversation = []
    chat_json = []

    # 1. Age
    age = get_user_input("What is your age?", validate_func=validate_age, extract_func=extract_age)
    conversation.append(f"Age: {age}")
    chat_json.append({"question": "What is your age?", "answer": age})
    time.sleep(1)

    # 2. Fever
    fever = get_user_input("Do you have a fever? (yes/no)", validate_func=validate_yesno, normalize_func=normalize_yesno)
    conversation.append(f"Fever: {fever}")
    chat_json.append({"question": "Do you have a fever? (yes/no)", "answer": fever})
    time.sleep(1)

    # 3. Cough or Chest Pain
    cough = get_user_input("Are you experiencing cough or chest pain? (yes/no)", validate_func=validate_yesno, normalize_func=normalize_yesno)
    conversation.append(f"Cough/Chest pain: {cough}")
    chat_json.append({"question": "Are you experiencing cough or chest pain? (yes/no)", "answer": cough})
    time.sleep(1)

    # 4. Chronic Conditions
    chronic_list = ["diabetes", "hypertension", "asthma", "heart disease", "none"]
    chronic = get_user_input("Do you have any chronic conditions? (diabetes/hypertension/asthma/heart disease/none)", validate_func=validate_symptom, allowed=chronic_list, extract_func=extract_symptom)
    conversation.append(f"Chronic conditions: {chronic}")
    chat_json.append({"question": "Do you have any chronic conditions?", "answer": chronic})
    time.sleep(1)

    # 5. Dynamic follow-up via OpenRouter
    prompt = "Patient information:\n" + "\n".join(conversation) + "\nAsk a relevant medical follow-up question. If no further questions are needed, say 'No further questions.'"
    follow_up = ask_openrouter(prompt)
    print("", follow_up)
    speak(follow_up)

    if "no further questions" not in follow_up.lower():
        answer = get_user_input(follow_up)
        conversation.append(f"{follow_up.strip()} {answer}")
        chat_json.append({"question": follow_up.strip(), "answer": answer})

    # 6. Final suggestion (short, professional, always end with consult message)
    summary_prompt = (
        "Patient details:\n" + "\n".join(conversation) +
        "\nIn 1-2 short sentences, provide a clear and professional medical suggestion. "
        "If urgent or professional help is needed, say so. Always end with: 'Please consult our doctor for further advice.'"
    )
    suggestion = ask_openrouter(summary_prompt)
    print("\n Suggestion:", suggestion)
    speak(f"Here is my suggestion. {suggestion}")

    # 7. Save conversation (bonus)
    try:
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump(chat_json, f, indent=2)
        print("\n[Conversation saved to chat_history.json]")
    except Exception as e:
        print(f"[Could not save chat history: {e}]")

# Run it
if __name__ == "__main__":
    medical_chatbot()
