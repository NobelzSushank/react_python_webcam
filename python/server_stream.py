# stream_server.py
import cv2
import numpy as np
import asyncio
from fastapi import FastAPI, WebSocket
from proctor import SuspiciousBehaviorAnalyzer

app = FastAPI()
analyzer = SuspiciousBehaviorAnalyzer()


@app.websocket("/stream")
async def stream_endpoint(ws: WebSocket):
    await ws.accept()
    buffer = bytearray()
    while True:
        chunk = await ws.receive_bytes()
        buffer.extend(chunk)

        # Attempt to decode a full WebM frame:
        # (In practice, you’d parse container boundaries—here’s a simplified loop)
        nparr = np.frombuffer(buffer, np.uint8)
        cap = cv2.VideoCapture()
        cap.open(nparr.tobytes(), apiPreference=cv2.CAP_FFMPEG)
        ret, frame = cap.read()
        if not ret:
            continue

        # Process the frame
        events = analyzer.process_frame(frame)
        if events:
            print("Flags:", events)

        # Reset buffer (or remove consumed bytes)
        buffer.clear()

# @app.websocket("/stream")
# async def stream_endpoint(ws: WebSocket):
#     await ws.accept()
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
#             continue

#         # Process the frame
#         events = analyzer.process_frame(frame)
#         if events:
#             print("Flags:", events)

#         # Reset buffer (or remove consumed bytes)
#         buffer.clear()
