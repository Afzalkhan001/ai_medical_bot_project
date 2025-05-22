import streamlit as st
import streamlit.components.v1 as components

def voice_input(label="Say something", key="voice_input"):
    """Display a button for browser mic recording and return transcript (experimental)."""
    html_code = f'''
    <button id="start-record-{key}">🎤 Speak</button>
    <span id="result-{key}"></span>
    <script>
    var recognizing = false;
    var final_transcript = "";
    var recognition;
    if ('webkitSpeechRecognition' in window) {{
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        document.getElementById("start-record-{key}").onclick = function() {{
            if (!recognizing) {{
                recognition.start();
                recognizing = true;
                document.getElementById("result-{key}").innerText = " Listening...";
            }}
        }};
        recognition.onresult = function(event) {{
            final_transcript = event.results[0][0].transcript;
            document.getElementById("result-{key}").innerText = final_transcript;
            window.parent.postMessage({{"streamlit_voice_input_{key}": final_transcript}}, "*");
            recognizing = false;
        }};
        recognition.onerror = function(event) {{
            document.getElementById("result-{key}").innerText = " [Error]";
            recognizing = false;
        }};
        recognition.onend = function() {{ recognizing = false; }};
    }} else {{
        document.getElementById("result-{key}").innerText = " (Speech recognition not supported)";
    }}
    </script>
    '''
    components.html(html_code, height=60)
    transcript = st.session_state.get(f"voice_input_{key}", "")
    return transcript

def speak_text(text, key="tts"):
    """Speak text using browser speech synthesis (experimental)."""
    html_code = f'''
    <button onclick="var msg = new SpeechSynthesisUtterance('{text}'); window.speechSynthesis.speak(msg);">🔊 Speak</button>
    '''
    components.html(html_code, height=40)
