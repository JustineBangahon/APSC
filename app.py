from flask import Flask, request, jsonify, render_template, Response, url_for
import cv2
import os

app = Flask(__name__)

# Global variable to store which cameras are active
active_cameras = []

# Dictionary holding camera names and their RTSP URLs
cameras_info = {
    "camera1": "rtsp://camera1:camera1@192.168.43.67/stream1",
    "camera2": "rtsp://camera2:camera2@192.168.43.68/stream1",
    "camera3": "rtsp://camera3:camera3@192.168.43.69/stream1"
}

# ----------------------
# Alexa Webhook Endpoint
# ----------------------
@app.route('/alexa', methods=['POST'])
def alexa_webhook():
    req = request.get_json()
    if not req or 'request' not in req:
        return build_response("Invalid Request", True)
    
    req_type = req['request'].get('type')
    
    if req_type == "LaunchRequest":
        return build_response("Welcome to your Alexa Camera Control. Say something like 'show camera1' or 'remove all' to control your cameras.", False)
    
    elif req_type == "IntentRequest":
        intent = req['request'].get('intent', {})
        intent_name = intent.get('name', "")
        slots = intent.get('slots', {})
        
        # Handle "ShowCameraIntent"
        if intent_name == "ShowCameraIntent":
            camera_slot = slots.get("CameraName", {})
            camera_value = camera_slot.get("value", "").lower()
            if camera_value:
                if camera_value == "all":
                    active_cameras[:] = list(cameras_info.keys())
                    speech_text = "Displaying all cameras."
                else:
                    if camera_value in cameras_info:
                        if camera_value not in active_cameras:
                            active_cameras.append(camera_value)
                        speech_text = f"Displaying {camera_value}."
                    else:
                        speech_text = f"I don't recognize {camera_value}."
            else:
                speech_text = "I didn't catch which camera to display."
            return build_response(speech_text, True)
        
        # Handle "RemoveCameraIntent"
        elif intent_name == "RemoveCameraIntent":
            camera_slot = slots.get("CameraName", {})
            camera_value = camera_slot.get("value", "").lower()
            if camera_value:
                if camera_value == "all":
                    active_cameras.clear()
                    speech_text = "Removed all cameras."
                else:
                    if camera_value in active_cameras:
                        active_cameras.remove(camera_value)
                        speech_text = f"Removed {camera_value} from display."
                    else:
                        speech_text = f"{camera_value} is not currently displayed."
            else:
                speech_text = "I didn't catch which camera to remove."
            return build_response(speech_text, True)
        
        else:
            return build_response("I'm not sure how to help with that.", True)
    
    else:
        return build_response("Invalid Request Type", True)

def build_response(text, should_end_session):
    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": text
            },
            "shouldEndSession": should_end_session
        }
    }
    return jsonify(response)

# ----------------------
# OpenCV Streaming Setup
# ----------------------
def generate_frames(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# Web route for the main page
@app.route('/')
def index():
    # Only display cameras that are active (set by Alexa)
    display_cameras = {cam: cameras_info[cam] for cam in active_cameras if cam in cameras_info}
    return render_template("index.html", cameras=display_cameras)

# Streaming route for each camera feed
@app.route('/video_feed/<camera_name>')
def video_feed(camera_name):
    if camera_name in cameras_info:
        rtsp_url = cameras_info[camera_name]
        return Response(generate_frames(rtsp_url),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Camera not found", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
