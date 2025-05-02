# server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import threading
from proctor import SuspiciousBehaviorAnalyzer
import numpy as np
import asyncio

app = FastAPI()
analyzer = SuspiciousBehaviorAnalyzer()

# Allow frontend (React at localhost:3000)
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
        # Start ffmpeg subprocess to read from stdin and output raw frames
        ffmpeg_process = subprocess.Popen(
            [
                "ffmpeg",
                "-i", "pipe:0",                # input from stdin
                "-f", "rawvideo",              # output format
                "-pix_fmt", "rgb24",           # pixel format
                "-vcodec", "rawvideo",
                "pipe:1"                       # output to stdout
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL         # optional: silence logs
        )

        def read_frames():
            width, height = 640, 480
            frame_size = 640 * 480 * 3  # assuming 640x480 RGB frames
            while True:
                raw_frame = ffmpeg_process.stdout.read(frame_size)
                if not raw_frame:
                    break
                # Here you can process raw_frame as needed (e.g., run analysis)
                print("Received frame from ffmpeg")

                # Convert bytes to numpy array
                frame = np.frombuffer(raw_frame, np.uint8).reshape((height, width, 3))

                # Process the frame
                events = analyzer.process_frame(frame)
                if events:
                    print("Flags:", events)

        # Start a thread to read frames from ffmpeg's stdout
        threading.Thread(target=read_frames, daemon=True).start()

        while True:
            data = await websocket.receive_bytes()
            if ffmpeg_process.stdin:
                ffmpeg_process.stdin.write(data)
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
        if ffmpeg_process:
            ffmpeg_process.kill()
