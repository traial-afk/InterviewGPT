import websockets
import asyncio
import json
from groq import AsyncGroq
import pyaudio
import streamlit as st
from collections import deque

# Page config
st.set_page_config(page_title="IntervewGPT", page_icon=":brain:", layout="wide")

# ---- MAINPAGE ----
st.title(":brain: InterviewGPT")
st.markdown("##")

# API setup
client = AsyncGroq(
    api_key="YOUR_GROQ_API_KEY",
)
DEEPGRAM_API_KEY = "YOUR_DEEPGRAM_API_KEY"

# Initialize session state
if "text" not in st.session_state:
    st.session_state["text"] = "Listening..."
    st.session_state["run"] = False

# Audio setup
FRAMES_PER_BUFFER = 8000
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()

# Start recording
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER,
)

conversation_history = deque(maxlen=5)
transcript = []

def start_listening():
    st.session_state["run"] = True

def stop_listening():
    with open("conversation.txt", "w") as file:
        file.write("\n".join(transcript))
    st.session_state["run"] = False

# UI Controls
start, stop = st.columns(2)
start.button("Start listening", on_click=start_listening)
stop.button("Stop listening", on_click=stop_listening)

# Deepgram WebSocket URL
DEEPGRAM_URL = "wss://api.deepgram.com/v1/listen?encoding=linear16&sample_rate=16000&channels=1&language=en-US"

async def send_receive():
    print("Connecting to Deepgram...")
    
    async with websockets.connect(
        DEEPGRAM_URL,
        extra_headers={
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
        }
    ) as _ws:
        print("Connected to Deepgram")

        async def send():
            while st.session_state["run"]:
                try:
                    data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                    await _ws.send(data)
                except websockets.exceptions.ConnectionClosedError as e:
                    print(f"Send error: {e}")
                    break
                except Exception as e:
                    print(f"Unexpected send error: {e}")
                    break
                await asyncio.sleep(0.01)

        async def receive():
            while st.session_state["run"]:
                try:
                    result_str = await _ws.recv()
                    result = json.loads(result_str)
                    
                    # Check if we have a final transcript
                    if "channel" in result and "alternatives" in result["channel"] and \
                       len(result["channel"]["alternatives"]) > 0 and \
                       "transcript" in result["channel"]["alternatives"][0] and \
                       result["is_final"]:
                        
                        transcript_text = result["channel"]["alternatives"][0]["transcript"]
                        
                        if transcript_text.strip():  # Only process non-empty transcripts
                            print(f"User said: {transcript_text}")
                            
                            st.session_state["text"] = f"<span style='color: orange;'>User:</span> {transcript_text}"
                            st.markdown(st.session_state["text"], unsafe_allow_html=True)
                            transcript.append(f"User: {transcript_text}")
                            conversation_history.append({"role": "user", "content": transcript_text})

                            # Generate response using Groq
                            messages = [
                                {"role": "system", "content": "You are a helpful assistant."}
                            ] + list(conversation_history)

                            chat_completion = await client.chat.completions.create(
                                messages=messages,
                                model="llama3-8b-8192",
                                temperature=0.5,
                                max_tokens=300,
                                stream=False
                            )
                            reply = chat_completion.choices[0].message.content
                            print(f"InterviewGPT: {reply}")
                            conversation_history.append({"role": "assistant", "content": reply})
                            transcript.append(f"InterviewGPT: {reply}")

                            st.session_state["chatText"] = f"<span style='color: green;'>InterviewGPT:</span> {reply}"
                            st.markdown(st.session_state["chatText"], unsafe_allow_html=True)

                except websockets.exceptions.ConnectionClosedError as e:
                    print(f"Receive error: {e}")
                    break
                except Exception as e:
                    print(f"Unexpected receive error: {e}")
                    continue

        await asyncio.gather(send(), receive())

if __name__ == "__main__":
    asyncio.run(send_receive())
