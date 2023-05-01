from flask import Flask, send_file, request
from picamera2 import Picamera2, Preview
from libcamera import controls
from io import BytesIO
import time

app = Flask(__name__)

image_name = 'cam1.jpg'

picam2 = Picamera2()
still_config = picam2.create_still_configuration()
picam2.configure(still_config)
picam2.start(show_preview=False)
time.sleep(2)
print('Cam started.')

@app.route('/capture', methods=['GET'])
def capture_image():
    try:
        print("autofocus running...")
        success = picam2.autofocus_cycle()
        print(f'Successful: {success}')

        img_data = BytesIO()
        picam2.capture_file(img_data, format="jpeg")
        print("SNAP!")
        img_data.seek(0)
        return send_file(img_data, mimetype='image/jpeg', as_attachment=True, download_name=image_name)

    except Exception as e:
        print(f"Error capturing image: {str(e)}")
        return "Error capturing image", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)