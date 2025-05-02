# app.py
from flask import Flask, request, jsonify
import cv2
import numpy as np
from proctor import SuspiciousBehaviorAnalyzer


app = Flask(__name__)
analyzer = SuspiciousBehaviorAnalyzer()

@app.route('/analyze/frame', methods=['POST'])
def analyze_frame():
    # Receive image as bytes
    img_bytes = request.files['frame'].read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Analyze
    events = analyzer.process_frame(frame)
    return jsonify(events)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
