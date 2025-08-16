from flask import Flask, Response, render_template, request, jsonify, send_from_directory
import json
import os

from employee_tracking_fixed import EmployeeTracker

app = Flask(__name__)
tracker = EmployeeTracker()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    def generate():
        while True:
            frame = tracker.get_current_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_tracking', methods=['POST'])
def start_tracking():
    """Start tracking with configuration"""
    try:
        config = request.json
        return jsonify(tracker.start_tracking(config))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/upload_video', methods=['POST'])
def upload_video():
    """Handle video file upload"""
    try:
        if 'video' not in request.files:
            return jsonify({"status": "error", "message": "No video file in request"})
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({"status": "error", "message": "No video file selected"})
        
        # Extract other configuration parameters
        config = {
            "absence_threshold": request.form.get("absence_threshold", 5),
            "confidence": request.form.get("confidence", 0.5),
            "area_method": request.form.get("area_method", "auto"),
            "source_type": "upload"
        }
        
        if request.form.get("area_method") == "manual":
            config["manual_coords"] = request.form.get("manual_coords", "0.1,0.1,0.9,0.9")
        
        return jsonify(tracker.upload_video(video_file, config))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/stop_tracking', methods=['POST'])
def stop_tracking():
    """Stop tracking"""
    return jsonify(tracker.stop_tracking())

@app.route('/status')
def get_status():
    """Get current tracking status"""
    return jsonify(tracker.get_status())

@app.route('/logs')
def get_logs():
    """Get system logs"""
    logs = tracker.get_logs()
    return jsonify({"status": "success", "logs": logs})

@app.route('/captures/<path:filename>')
def get_capture(filename):
    """Serve captured frames"""
    return send_from_directory('output_frames', filename)

if __name__ == '__main__':
    # Ensure model is set up before starting
    tracker.setup_model()
    app.run(debug=True, host='0.0.0.0', port=5000)