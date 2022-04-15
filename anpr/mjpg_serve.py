#!/usr/bin/python
import cv2
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import time
import os
import signal
import subprocess
import time
import sys

capture=None
global server



# Class that sets up HTTP Server and Converts - We need not modify this
class CamHandler(BaseHTTPRequestHandler):
	# function that converts rtsp to http ans sent it to the client
	def do_GET(self):
		try:
			self.send_response(200)
			self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
			self.end_headers()
			capture = cv2.VideoCapture(rtsplink)
			print("client connected")
			while(capture.isOpened()):
				try:
					rc,img = capture.read()
					if (rc==True):
						imgRGB = img
						imgRGB = cv2.resize(imgRGB,(960,380))
						r, buf = cv2.imencode(".jpg",imgRGB)
						self.wfile.write("--jpgboundary\r\n")
						self.send_header('Content-type','image/jpeg')
						self.send_header('Content-length',str(len(buf)))
						self.end_headers()
						self.wfile.write(bytearray(buf))
						self.wfile.write('\r\n')
						time.sleep(0.005)
					else:
						continue   
				except Exception as e: #KeyboardInterrupt:
					print("Exception in Capturing",e)
					break
			capture.release()	 
			return
		except Exception as e:
			print("Client Disconnected", e)
			return

def killProcess(port):
	try:
		# this command is used to get the pid of the process which is running in the given port
		command = "netstat -ltnp | grep "+ str(port)   #linux
		# command = "netstat -aon | findstr " + str(port)  #windows
		c = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
		stdout, stderr = c.communicate()
		#Getting process id of the existing HTTP Server process
		pid = int(stdout.decode().strip().split(' ')[-1].split('/')[0])
		# kill the process 
		os.kill(pid, signal.SIGTERM)
	except Exception as e:
		print("All Existing HTTP Servers killed. Killing Process Exception - ",str(e))
	#Sleep for 2 seconds is necessary for HTTP Servers to restart again    
	time.sleep(2)

def main(rtsp):
	global rtsplink
	global capture
	rtsplink = rtsp
	# While loop just in case rtsp link returns error
	while(1):
		# kill the process
		killProcess(9090)  
		try:
			# start a new server
			server = HTTPServer(('localhost',int(9090)),CamHandler)
			server.serve_forever()
		except Exception as e:
			print("Exception in Main",e)
		killProcess(9090)

if __name__ == '__main__':
	try:
		main(sys.argv[1])
	except Exception as e:
		print("Exception in calling main..", e)

