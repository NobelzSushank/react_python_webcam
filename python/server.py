# import cv2
# import numpy as np
# import asyncio
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from proctor import SuspiciousBehaviorAnalyzer
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()
# analyzer = SuspiciousBehaviorAnalyzer()


# @app.websocket("/stream")
# async def stream_endpoint(ws: WebSocket):
#     await ws.accept()
#     print("WebSocket connection accepted")
#     buffer = bytearray()
#     while True:
#         chunk = await ws.receive_bytes()
#         buffer.extend(chunk)

#         # Attempt to decode a full WebM frame:
#         # (In practice, you’d parse container boundaries—here’s a simplified loop)
#         nparr = np.frombuffer(buffer, np.uint8)
#         cap = cv2.VideoCapture()
#         cap.open(nparr.tobytes(), apiPreference=cv2.CAP_FFMPEG)
#         ret, frame = cap.read()
#         if not ret:
#             print("If not ret")
#             continue

#         # Process the frame
#         events = analyzer.process_frame(frame)
#         if events:
#             print("Flags:", events)

#         print("Before buffer clear")
#         # Reset buffer (or remove consumed bytes)
#         buffer.clear()




# *********************************************
# BELOW CODE IS WORKING
# *********************************************
# server.py (FastAPI backend)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import av
import io

app = FastAPI()

# Allow CORS from the React frontend (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/stream")
async def stream(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection accepted")
    try:
        while True:
            # Receive a chunk of video/audio data (as bytes)
            data = await websocket.receive_bytes()
            # Decode the chunk in-memory using PyAV
            try:
                container = av.open(io.BytesIO(data))
                # Iterate through decoded video frames
                for frame in container.decode(video=0):
                    # Mock event detection: log frame PTS and time
                    print(f"Detected event in frame PTS={frame.pts}, time={frame.time:.3f}")
                # (Optionally decode audio frames similarly:
                # for frame in container.decode(audio=0): ...)
            except Exception as decode_err:
                print("Decoding error (invalid chunk?):", decode_err)
    except WebSocketDisconnect:
        print("WebSocket client disconnected")