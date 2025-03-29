import streamlit as st
import numpy as np
import cv2
import time
import threading
import queue
import speech_recognition as sr
import pyttsx3
import base64
from PIL import Image
import io
import json
import requests

# Class definition with transformers dependency removed
class HologramAssistant:
    def __init__(self, api_key=None, hologram_model='assistant_default.mp4'):
        # Initialize AI components
        self.api_key = api_key
        if api_key:
            self.ai_mode = "openai"
        else:
            # Fallback to simple local responses if no API key
            self.ai_mode = "local"
            self.local_responses = {
                "hello": "Hello! How can I assist you today?",
                "how are you": "I'm functioning well. How can I help you?",
                "what can you do": "I can answer questions, have conversations, and assist with various tasks.",
                "thank you": "You're welcome! Is there anything else I can help with?",
                "bye": "Goodbye! Feel free to chat again anytime.",
                "help": "I'm your hologram assistant. You can ask me questions or just chat with me."
            }
        
        # Initialize speech components if needed
        self.speech_engine = pyttsx3.init() if not st.session_state.get('disable_speech', False) else None
        self.recognizer = sr.Recognizer() if not st.session_state.get('disable_voice', False) else None
        
        # Initialize hologram display
        self.hologram_model = hologram_model
        
        # State variables
        self.is_active = False
        self.conversation_history = []
        self.frame_queue = queue.Queue(maxsize=5)
        
    def start(self):
        """Start the hologram assistant"""
        self.is_active = True
        
        # Start hologram display thread
        threading.Thread(target=self._display_hologram_frames).start()
        
        if self.recognizer:
            threading.Thread(target=self._voice_listener).start()
        
        return "Hologram Assistant is now active."
    
    def stop(self):
        """Stop the hologram assistant"""
        self.is_active = False
        return "Hologram Assistant stopped."
    
    def _voice_listener(self):
        """Background thread to listen for voice commands"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.is_active:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    try:
                        text = self.recognizer.recognize_google(audio)
                        st.session_state.user_input = text
                        
                        # Use Streamlit's experimental rerun to update the UI
                        if "stop hologram" in text.lower() or "exit" in text.lower():
                            self.stop()
                        else:
                            # Process will happen in the main Streamlit loop
                            st.session_state.process_voice = True
                            
                    except sr.UnknownValueError:
                        pass
                    except sr.RequestError:
                        if self.speech_engine:
                            self.speech_engine.say("Sorry, I'm having trouble connecting to the speech recognition service.")
                            self.speech_engine.runAndWait()
                        
                except Exception as e:
                    st.error(f"Error in voice listener: {str(e)}")
    
    def generate_ai_response(self, text):
        """Generate AI response based on the input text"""
        self.conversation_history.append({"role": "user", "content": text})
        
        try:
            if self.ai_mode == "openai":
                try:
                    # OpenAI API for ChatGPT
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    }
                    
                    data = {
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": "You are a helpful hologram assistant."},
                            *self.conversation_history
                        ],
                        "max_tokens": 150
                    }
                    
                    response = requests.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        data=json.dumps(data)
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        answer = response_data["choices"][0]["message"]["content"]
                    else:
                        st.error(f"API error: {response.status_code}")
                        answer = "I'm sorry, I encountered an error with the API."
                except Exception as e:
                    st.error(f"Error with OpenAI API: {str(e)}")
                    answer = "I'm sorry, I encountered an error with the API."
            else:
                # Use simple local response logic
                lower_text = text.lower()
                
                # Check for direct matches
                for key, response in self.local_responses.items():
                    if key in lower_text:
                        answer = response
                        break
                else:
                    # Default responses for unmatched queries
                    if "?" in text:
                        answer = "That's an interesting question. As a simple hologram, I don't have access to that information without an API key."
                    elif any(greeting in lower_text for greeting in ["hi", "hello", "hey"]):
                        answer = "Hello there! How can I assist you today?"
                    elif any(word in lower_text for word in ["thanks", "thank you"]):
                        answer = "You're welcome! Is there anything else I can help with?"
                    elif any(word in lower_text for word in ["bye", "goodbye", "exit"]):
                        answer = "Goodbye! Have a great day!"
                    else:
                        answer = "I understand you're trying to communicate with me. For more advanced responses, please provide an OpenAI API key in the settings."
            
            self.conversation_history.append({"role": "assistant", "content": answer})
            
            # Speak the response if speech is enabled
            if self.speech_engine:
                threading.Thread(target=self._speak_response, args=(answer,)).start()
                
            return answer
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "I'm sorry, I encountered an error processing your request."
    
    def _speak_response(self, text):
        """Convert text response to speech"""
        if self.speech_engine:
            self.speech_engine.say(text)
            self.speech_engine.runAndWait()
    
    def _display_hologram_frames(self):
        """Generate hologram frames and put them in the queue"""
        try:
            # Open the video file or use webcam as a fallback
            try:
                cap = cv2.VideoCapture(self.hologram_model)
                if not cap.isOpened():
                    raise Exception("Could not open video file")
            except:
                # Use placeholder animation if webcam is not available
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    # If neither works, create a placeholder moving gradient
                    st.warning("Using placeholder animation - neither video file nor webcam available")
                    while self.is_active:
                        # Create a gradient background that shifts colors
                        t = time.time()
                        h, w = 480, 640
                        img = np.zeros((h, w, 3), dtype=np.uint8)
                        
                        for y in range(h):
                            for x in range(w):
                                r = int(127.5 + 127.5 * np.sin(x/30 + t))
                                g = int(127.5 + 127.5 * np.sin(y/20 - t))
                                b = int(200 + 55 * np.sin((x+y)/50 + t*2))
                                img[y, x] = [r, g, b]
                        
                        # Apply hologram effect
                        hologram_effect = self._apply_hologram_effect(img)
                        
                        if not self.frame_queue.full():
                            self.frame_queue.put(hologram_effect)
                        
                        time.sleep(0.04)  # ~25 fps
                    return
            
            while self.is_active:
                ret, frame = cap.read()
                if not ret:
                    # Loop the video when it ends
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                # Apply visual effects to create hologram appearance
                hologram_effect = self._apply_hologram_effect(frame)
                
                # Put frame in queue for streamlit to display
                if not self.frame_queue.full():
                    self.frame_queue.put(hologram_effect)
                
                time.sleep(0.04)  # ~25 fps
            
            cap.release()
            
        except Exception as e:
            st.error(f"Error in hologram display: {str(e)}")
    
    def _apply_hologram_effect(self, frame):
        """Apply visual effects to create a holographic appearance"""
        # Convert to float for processing
        frame_float = frame.astype(np.float32) / 255.0
        
        # Enhance blue channel to create holographic tint
        frame_float[:,:,0] *= 0.7  # Reduce red
        frame_float[:,:,1] *= 0.8  # Reduce green
        frame_float[:,:,2] *= 1.2  # Enhance blue
        
        # Add scanlines effect
        height, width = frame.shape[:2]
        for i in range(0, height, 4):
            frame_float[i:i+1, :] *= 0.7
        
        # Add glow effect
        blurred = cv2.GaussianBlur(frame_float, (0, 0), 10)
        hologram = cv2.addWeighted(frame_float, 0.8, blurred, 0.2, 0)
        
        # Convert back to uint8 for display
        hologram = np.clip(hologram * 255, 0, 255).astype(np.uint8)
        
        return hologram
    
    def get_frame(self):
        """Get a frame from the queue if available"""
        if not self.frame_queue.empty():
            return self.frame_queue.get()
        return None


# Streamlit app
def main():
    st.set_page_config(page_title="AI Hologram Assistant", page_icon="🌌", layout="wide")
    
    # Custom CSS for holographic look
    st.markdown("""
        <style>
        .main {
            background-color: #000;
            color: #00BFFF;
        }
        .stTextInput input {
            background-color: rgba(0, 30, 60, 0.7);
            color: #00BFFF;
            border: 1px solid #0080FF;
        }
        .stButton>button {
            background-color: rgba(0, 40, 80, 0.8);
            color: #00FFFF;
            border: 1px solid #0080FF;
        }
        .stMarkdown {
            color: #00BFFF;
        }
        .chat-message {
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            display: flex;
        }
        .user-message {
            background-color: rgba(0, 30, 60, 0.7);
            border-left: 5px solid #0080FF;
        }
        .assistant-message {
            background-color: rgba(0, 60, 120, 0.7);
            border-left: 5px solid #00FFFF;
        }
        .message-content {
            margin-left: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'assistant' not in st.session_state:
        st.session_state.assistant = None
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    if 'process_voice' not in st.session_state:
        st.session_state.process_voice = False
    
    # Title
    st.title("AI Hologram Assistant")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("OpenAI API Key (optional)", type="password")
        
        video_source = st.selectbox("Video Source", 
                                    ["Default Animation", "Webcam", "Upload Video"],
                                    index=0)
        
        uploaded_file = None
        if video_source == "Upload Video":
            uploaded_file = st.file_uploader("Upload video for hologram", type=["mp4", "avi", "mov"])
        
        disable_speech = st.checkbox("Disable Speech Output")
        disable_voice = st.checkbox("Disable Voice Input")
        
        if st.button("Initialize Assistant"):
            # Save settings to session state
            st.session_state.disable_speech = disable_speech
            st.session_state.disable_voice = disable_voice
            
            # Determine hologram model source
            hologram_model = 'assistant_default.mp4'  # Default
            if video_source == "Webcam":
                hologram_model = 0
            elif video_source == "Upload Video" and uploaded_file:
                # Save uploaded file temporarily
                with open("temp_upload.mp4", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                hologram_model = "temp_upload.mp4"
            
            # Initialize assistant
            st.session_state.assistant = HologramAssistant(
                api_key=api_key if api_key else None,
                hologram_model=hologram_model
            )
            
            # Start the assistant
            start_msg = st.session_state.assistant.start()
            st.success(start_msg)
    
    # Layout with two columns - hologram display and chat
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.header("Hologram Visualization")
        
        # Placeholder for hologram display
        hologram_placeholder = st.empty()
        
        # If assistant is initialized, show hologram
        if st.session_state.assistant and st.session_state.assistant.is_active:
            # Display hologram frames
            while st.session_state.assistant.is_active:
                frame = st.session_state.assistant.get_frame()
                if frame is not None:
                    # Convert OpenCV BGR to RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Display using st.image
                    hologram_placeholder.image(rgb_frame, channels="RGB", use_column_width=True)
                
                # Short sleep to prevent UI lag
                time.sleep(0.1)
        else:
            # Show placeholder when assistant is not active
            placeholder_img = np.zeros((480, 640, 3), dtype=np.uint8)
            placeholder_img[:, :, 2] = 50  # Add some blue tint
            hologram_placeholder.image(placeholder_img, channels="RGB", use_column_width=True)
            st.info("Initialize the assistant from the sidebar to activate the hologram.")
    
    with col2:
        st.header("Chat Interface")
        
        # Display conversation history
        chat_container = st.container()
        with chat_container:
            for i, message in enumerate(st.session_state.conversation):
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div class="message-content">
                            <p><strong>You:</strong> {message["content"]}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="message-content">
                            <p><strong>Assistant:</strong> {message["content"]}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Input for chat
        user_input = st.text_input("Ask me anything:", value=st.session_state.user_input)
        
        # Process text input or voice input
        process_input = False
        if user_input and user_input != st.session_state.get('last_processed_input', ''):
            process_input = True
            st.session_state.last_processed_input = user_input
        elif st.session_state.get('process_voice', False):
            process_input = True
            st.session_state.process_voice = False
        
        if process_input and st.session_state.assistant:
            # Add user message to conversation
            st.session_state.conversation.append({"role": "user", "content": user_input})
            
            # Generate response
            response = st.session_state.assistant.generate_ai_response(user_input)
            
            # Add assistant response to conversation
            st.session_state.conversation.append({"role": "assistant", "content": response})
            
            # Clear input after processing
            st.session_state.user_input = ""
            
            # Force refresh
            st.experimental_rerun()
        
        # Stop button for assistant
        if st.session_state.assistant and st.session_state.assistant.is_active:
            if st.button("Stop Assistant"):
                stop_msg = st.session_state.assistant.stop()
                st.session_state.assistant = None
                st.info(stop_msg)
                st.experimental_rerun()

if __name__ == "__main__":
    main()