from flask import Flask, render_template, Response
from camera import VideoCamera

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('testDisplay.html')

def gen(camera):
    while camera.video.isOpened():
        frame = camera.get_frame()
        yield(b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame
            + b'\r\n\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
        mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000', debug=True)
