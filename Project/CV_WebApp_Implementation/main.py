from flask import Flask, render_template, Response
from camera import VideoCamera

app = Flask(__name__)

@app.route('/')
def index(VideoCamera):
    return render_template('testDisplay.html', count= VideoCamera.getCount())

@app.route('/bicep_curls')
def bicep_curls():
    return render_template('BicepCurls.html')

@app.route('/jumping_jacks')
def jumping_jacks():
    return render_template('JumpingJacks.html')

@app.route('/toe_touch')
def toe_touch():
    return render_template('ToeTouch.html')

@app.route('/stats')
def stats_page():
    return render_template("Stats.html")

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
