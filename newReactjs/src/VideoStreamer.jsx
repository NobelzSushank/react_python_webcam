// VideoStreamer.jsx (React component)
import React, { useRef, useEffect } from 'react';

function VideoStreamer() {
  const videoRef = useRef(null);

  useEffect(() => {
    async function startStreaming() {
      try {
        // Request camera and microphone
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        // Show the local video feed
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }

        // Open WebSocket to backend
        const socket = new WebSocket("ws://localhost:5000/stream");

        // Choose a supported MIME type (WebM or MP4 H.264/AAC)
        let mimeType = 'video/webm; codecs=vp8,opus';
        if (typeof MediaRecorder.isTypeSupported === 'function') {
          if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = 'video/mp4; codecs="avc1.42E01E,mp4a.40.2"';
            if (!MediaRecorder.isTypeSupported(mimeType)) {
              console.error('No supported MIME type for MediaRecorder');
              return;
            }
          }
        } else {
          // Older Safari: assume MP4/H.264 is supported
          mimeType = 'video/mp4';
        }

        // Create MediaRecorder with chosen options
        const mediaRecorder = new MediaRecorder(stream, { mimeType });
        mediaRecorder.onerror = (err) => console.error("MediaRecorder error:", err);

        // When a data chunk is available, send it via WebSocket
        mediaRecorder.ondataavailable = (event) => {
          if (event.data && event.data.size > 0 && socket.readyState === WebSocket.OPEN) {
            socket.send(event.data);
          }
        };

        // WebSocket event handlers
        socket.onerror = (err) => console.error("WebSocket error:", err);
        socket.onclose = (e) => console.log("WebSocket closed:", e);

        // Start recording when WebSocket is open
        socket.onopen = () => {
          mediaRecorder.start(1000); // emit a blob every 1 second
          console.log("MediaRecorder started, streaming to backend...");
        };
      } catch (err) {
        console.error("Error accessing media devices:", err);
      }
    }

    startStreaming();
  }, []);

  return (
    <video
      ref={videoRef}
      autoPlay
      muted
      playsInline
      style={{ width: "640px", height: "480px", backgroundColor: "#000" }}
    />
  );
}

export default VideoStreamer;
