import cv2
import time
from datetime import datetim
from picamera import PiCamera
import io
import logging
import socketserver
from threading import Condition
from http import server
import imutils


PAGE="""\
<html>
	<head>
		<title>Traffic camera</title>
	</head>
	<body>
		<center><h1>Raspberry Pi - Surveillance Camera</h1></center>
		<center><img src="stream.mjpg" width="640" height="480"></center>
	</body>
</html>
"""

class StreamingOutput(object):
	def __init__(self):
		self.frame = None
		self.buffer = io.BytesIO()
		self.condition = Condition()

	def write(self, buf):
		if buf.startswith(b'\xff\xd8'):
			self.buffer.truncate()
			with self.condition:
				self.frame = self.buffer.getvalue()
                spotCar(self.frame)
				self.condition.notify_all()
			self.buffer.seek(0)
		return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path == '/':
			self.send_response(301)
			self.send_header('Location', '/index.html')
			self.end_headers()
		elif self.path == '/index.html':
			content = PAGE.encode('utf-8')
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.send_header('Content-Length', len(content))
			self.end_headers()
			self.wfile.write(content)
		elif self.path == '/stream.mjpg':
			self.send_response(200)
			self.send_header('Age', 0)
			self.send_header('Cache-Control', 'no-cache, private')
			self.send_header('Pragma', 'no-cache')
			self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
			self.end_headers()
			try:
				while True:
					with output.condition:
						output.condition.wait()
						frame = output.frame
					self.wfile.write(b'--FRAME\r\n')
					self.send_header('Content-Type', 'image/jpeg')
					self.send_header('Content-Length', len(frame))
					self.end_headers()
					self.wfile.write(frame)
					self.wfile.write(b'\r\n')
			except Exception as e:
				logging.warning('Exception with streaming client %s: %s', self.client_address, str(e))
		else:
			self.send_error(404)
			self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
	allow_reuse_address = True
	daemon_threads = True

with PiCamera(resolution='640x480', framerate=24) as camera:
	output = StreamingOutput()
	camera.start_recording(output, format='mjpeg')
	try:
		address = ('', 8000)
		server = StreamingServer(address, StreamingHandler)
		server.serve_forever()
	finally:
		camera.stop_recording()
	

# Create full body classifier
classify_car = cv2.CascadeClassifier("haarcascade_car.xml")

# Capture the video
# TO DO, connect the camera here
def spotCar(input_frame):
    vid_capture = cv2.VideoCapture(input_frame)

    while vid_capture.isOpened():

        # Read the frame
        ret, frame = vid_capture.read()

        # Convert the image to greyscale 
        greyscale_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Pass the frame to the full body classifier
        cars_detected = classify_car.detectMultiScale(greyscale_image, 1.4, 2)


        # Density detection logic
        # TO DO show red green blue collor respectivly on
        # the bonnet vision kit or raw rasberry pi 
        if(len(cars_detected ) <= 1):
            print("LOW DENSITY " + str(datetime.today()))
        if(len(cars_detected) == 2):
            print("MEDIUM DENSITY" + str(datetime.today()))
        if(len(cars_detected) > 2):
            print("HIGH DENSITY" + str(datetime.today()))
        
        # Draw bounding boxes around finded objects
        for(x,y,w,h) in cars_detected:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 255), 2)
            cv2.imshow("Here are the cars", frame)

        # Exit the window with q
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    vid_capture.release()
    cv2.destroyAllWindows()                