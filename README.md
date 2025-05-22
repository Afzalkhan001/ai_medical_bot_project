# Medical Virtual Health Assistant (Streamlit Web App)

A user-friendly medical chatbot designed for elderly and general users, featuring robust natural language understanding, text and (experimental) voice input/output, and professional health suggestions. Deployable for free using Streamlit Cloud.

## Features
- Step-by-step health questionnaire (age, fever, cough/chest pain, chronic conditions)
- Robust input validation (accepts natural language answers)
- "Repeat" and "skip" options for accessibility
- Experimental browser-based voice input/output
- Concise, professional medical suggestions
- Clean, accessible web interface (Streamlit)

## Quick Start (Local)
1. Clone this repo and navigate to the folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run streamlit_app.py
   ```

## Deploy for Free on Streamlit Cloud
1. Push your code to GitHub (include `streamlit_app.py`, `requirements.txt`, and `medical_chatbot_voice.py`).
2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and sign in with GitHub.
3. Click **New app**, select your repo, branch, and set the main file to `streamlit_app.py`.
4. Click **Deploy**. Your app will be live at a free public URL!

## Experimental Voice Input/Output
- The app supports experimental browser voice input (microphone) and output (speech synthesis) via Streamlit components and JavaScript.
- For best results, use Chrome or Edge browsers.

## File Structure
- `streamlit_app.py` — Main Streamlit web app
- `medical_chatbot_voice.py` — Chatbot logic (imported by the app)
- `requirements.txt` — Python dependencies

## Security
- **Do NOT share your OpenRouter API key publicly.**
- This app is for educational/demo purposes and does not replace professional medical advice.

## Screenshots
See below for step-by-step deployment guide with screenshots.

---
