import os, os.path, json, base64, asyncio, queue, time, threading
import numpy as np
import sounddevice as sd
import websockets
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# For OpenAI:
WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview"
# If you are on Azure OpenAI Realtime, the URL shape differs; see docs:
# https://learn.microsoft.com/azure/ai-foundry/openai/how-to/realtime-audio-webrtc  (WebRTC)
# https://learn.microsoft.com/azure/ai-foundry/openai/realtime-audio-reference      (events)
# And use the appropriate header: {"api-key": "..."} instead of Authorization.  # :contentReference[oaicite:1]{index=1}

VOICE = "verse"           # try: alloy, cedar, marin, verse (varies by account/model)
SAMPLE_RATE = 16000       # PCM16 @ 16kHz mono
CHUNK_MS = 50             # ~50ms per packet is a good balance
CHUNK_SIZE = int(SAMPLE_RATE * (CHUNK_MS/1000.0))
INPUT_DTYPE = np.int16

# ---- audio capture (producer) ----
def audio_stream(q: queue.Queue, stop_evt):
    """Capture mic audio and push chunks into a Queue until stop_evt is set."""
    def callback(indata, frames, time, status):
        if status:
            print("Audio status:", status, flush=True)
        if stop_evt.is_set():
            raise sd.CallbackStop()
        # indata is float32 in [-1, 1], convert to PCM16
        pcm16 = np.clip(indata[:, 0] * 32767, -32768, 32767).astype(INPUT_DTYPE).tobytes()
        q.put(pcm16)

    with sd.InputStream(
        channels=1, samplerate=SAMPLE_RATE, dtype="float32", callback=callback
    ):
        stop_evt.wait()  # block until we’re told to stop

# ---- audio playback (consumer) ----
class Player:
    def __init__(self, samplerate=SAMPLE_RATE):
        self.stream = sd.OutputStream(channels=1, samplerate=samplerate, dtype=np.float32)
        self.stream.start()

    def play_pcm16(self, data: bytes):
        # Convert bytes->int16->float32 for sounddevice
        # PCM16 data comes as int16, convert to float32 in range [-1, 1]
        arr = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0
        self.stream.write(arr)

    def close(self):
        self.stream.stop(); self.stream.close()

async def main():
    assert OPENAI_API_KEY, "Set OPENAI_API_KEY first"

    # Connect to Realtime WebSocket
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1",
    }
    async with websockets.connect(WS_URL, additional_headers=headers, ping_interval=20, max_size=50_000_000) as ws:
        print("Connected.")

        # 1) Configure the session: voice, audio formats, server VAD (turn-taking)
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "voice": VOICE,
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200,
                    "create_response": True,
                    "interrupt_response": True
                },
                # Optional: live transcription of your speech
                # "input_audio_transcription": {"model": "whisper-1"}
            }
        }))

        # Optionally drop in an opening instruction/message (text)
        await ws.send(json.dumps({
            "type": "response.create",
            "response": {
                "instructions": "You are a helpful English-speaking voice assistant. IMPORTANT: Always respond in English only. Listen to user input, process it intelligently, and provide helpful responses. Keep replies under 2 sentences unless asked. Be conversational and actually help with what the user asks."
            }
        }))

        # Start audio capture on a background thread
        mic_q: queue.Queue = queue.Queue(maxsize=20)
        stop_evt = threading.Event()  # Use threading.Event instead of asyncio.Event
        loop = asyncio.get_event_loop()
        mic_thread = loop.run_in_executor(None, audio_stream, mic_q, stop_evt)

        player = Player()

        async def sender():
            """Continuously send mic chunks to the server buffer."""
            try:
                while not stop_evt.is_set():
                    try:
                        chunk = mic_q.get(timeout=0.2)
                    except queue.Empty:
                        await asyncio.sleep(0.01)
                        continue

                    # send as base64 with event: input_audio_buffer.append
                    b64 = base64.b64encode(chunk).decode("ascii")
                    await ws.send(json.dumps({
                        "type": "input_audio_buffer.append",
                        "audio": b64
                    }))
                    # Backoff slightly to avoid overflow
                    await asyncio.sleep(CHUNK_MS / 1000.0 * 0.6)
                # Optionally: commit if you're not using server VAD
                # await ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
            except Exception as e:
                print("Sender error:", e)

        async def receiver():
            """Handle server events: play audio deltas as they stream."""
            try:
                async for raw in ws:
                    evt = json.loads(raw)
                    t = evt.get("type", "")
                    if t == "response.audio.delta":
                        # Audio bytes arrive base64-encoded PCM16
                        b64 = evt.get("delta", "")
                        if b64:
                            player.play_pcm16(base64.b64decode(b64))
                    elif t == "response.audio.done":
                        pass  # one spoken segment finished
                    elif t == "conversation.item.input_audio_transcription.completed":
                        text = evt.get("transcript", "")
                        if text:
                            print(f"[you →] {text}")
                    elif t == "response.output_text.delta":
                        # optional: text delta if you also requested text
                        print(evt.get("delta", ""), end="", flush=True)
                    elif t == "response.output_text.done":
                        print()  # newline after full text
                    elif t == "error":
                        print("Server error:", evt)
                    # You’ll also see VAD events like input_audio_buffer.speech_started/.speech_stopped
                    # and buffer started/stopped events. See audio events reference.  # :contentReference[oaicite:2]{index=2}
            except websockets.ConnectionClosed:
                pass

        # Run both tasks until Ctrl+C
        tasks = [asyncio.create_task(sender()), asyncio.create_task(receiver())]
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\nStopping…")
        finally:
            stop_evt.set()
            player.close()

if __name__ == "__main__":
    asyncio.run(main())
