from flask import Flask, render_template, Response, url_for
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from flask_ask_sdk.skill_adapter import SkillAdapter
from ask_sdk_model import Response as AskResponse
import cv2
import os

os.environ["OSCRYPTO_NO_LIBCRYPTO_VERSION_CHECK"] = "true"
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
# Alexa Skill Setup
# ----------------------
sb = SkillBuilder()

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)
    def handle(self, handler_input):
        speech_text = ("Welcome to your Alexa Camera Control. "
                       "Say something like 'show camera1' or 'remove all' to control your cameras.")
        return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response

class ShowCameraIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("ShowCameraIntent")(handler_input)
    def handle(self, handler_input):
        global active_cameras
        slots = handler_input.request_envelope.request.intent.slots
        camera_slot = slots.get("CameraName")
        if camera_slot and camera_slot.value:
            camera = camera_slot.value.lower()
            if camera == "all":
                active_cameras = list(cameras_info.keys())
                speech_text = "Displaying all cameras."
            else:
                if camera in cameras_info:
                    if camera not in active_cameras:
                        active_cameras.append(camera)
                    speech_text = f"Displaying {camera}."
                else:
                    speech_text = f"I don't recognize {camera}."
        else:
            speech_text = "I didn't catch which camera to display."
        return handler_input.response_builder.speak(speech_text).set_should_end_session(True).response

class RemoveCameraIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("RemoveCameraIntent")(handler_input)
    def handle(self, handler_input):
        global active_cameras
        slots = handler_input.request_envelope.request.intent.slots
        camera_slot = slots.get("CameraName")
        if camera_slot and camera_slot.value:
            camera = camera_slot.value.lower()
            if camera == "all":
                active_cameras = []
                speech_text = "Removed all cameras."
            else:
                if camera in active_cameras:
                    active_cameras.remove(camera)
                    speech_text = f"Removed {camera} from display."
                else:
                    speech_text = f"{camera} is not currently displayed."
        else:
            speech_text = "I didn't catch which camera to remove."
        return handler_input.response_builder.speak(speech_text).set_should_end_session(True).response

# Register Alexa handlers
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ShowCameraIntentHandler())
sb.add_request_handler(RemoveCameraIntentHandler())

# Create the Alexa skill adapter for Flask
skill_adapter = SkillAdapter(skill=sb.create(), skill_id="amzn1.ask.skill.bc788426-894f-4e91-bdfe-e0b2102df4e5", app=app)

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
