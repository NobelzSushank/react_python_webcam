import React, { useEffect, useRef } from 'react';

const DELVideoStreamer = () => {
  const videoRef = useRef(null);
  const socketRef = useRef(null);
  const mediaRecorderRef = useRef(null);

  useEffect(() => {
    // 1. Open WebSocket
    socketRef.current = new WebSocket('ws://localhost:5000/stream');

    socketRef.current.onerror = (error) => {
        console.log("WebSocket error: ", error);
      };

    // 2. Get camera + mic
    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      .then(stream => {
        videoRef.current.srcObject = stream;

        // 3. Start MediaRecorder
        mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'video/webm; codecs=vp8' });
        mediaRecorderRef.current.ondataavailable = (e) => {
          if (e.data && e.data.size > 0) {
            console.log('send each chunk')
            // send each chunk
            socketRef.current.send(e.data);
          }
        };
        // Emit every 1 second
        mediaRecorderRef.current.start(1000);
      });

    return () => {
      mediaRecorderRef.current?.stop();
      socketRef.current?.close();
    };
  }, []);

  return <video ref={videoRef} autoPlay muted style={{ width: 320 }} />;
};

export default DELVideoStreamer;
