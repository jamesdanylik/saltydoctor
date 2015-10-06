import threading
import Queue
import signal
import sys
from time import sleep

import Tkinter

from urllib import urlopen
import websocket # note: this is 'websocket-client' on pip

def ws_on_message(ws, msg):
	print 'WS RECV: ' + msg
	if str(msg) != '1::':
		print 'WS ACK: ' + msg
		ws.send(msg)
		ws_queue.put(msg)

def ws_on_error(ws, err):
	print 'WS ERR: ' + err

def ws_on_open(ws):
	print 'WS: [Socket Connected]'

def ws_on_close(ws):
	print 'WS: [Socket Closed]'

if __name__ == '__main__':
	try:
		print 'MAIN: Starting WS Thread...'

		#print 'WS: Starting enabling debugging...'
		#websocket.enableTrace(True)

		ws_queue = Queue.Queue()

		print 'WS: Getting SocketID for handoff...'
		u = urlopen("http://www-cdn-twitch.saltybet.com:8000/socket.io/1/")
		response = u.readline()
		socketID = response.split(':')[0]	

		print 'WS: Establishing WebSocket connection...'
		ws = ws = websocket.WebSocketApp(
			"ws://www-cdn-twitch.saltybet.com:8000/socket.io/1/websocket/"+socketID, 
			on_message = ws_on_message, 
			on_error = ws_on_error, 
			on_close = ws_on_close)
		ws.on_open = ws_on_open

		wst = threading.Thread(target=ws.run_forever)
		wst.daemon = True
		wst.start()

		print 'MAIN: Finished setting up WS Thread.'

		# Wait for socket to connect
		ws_conn_timeout = 5
		while not ws.sock.connected and ws_conn_timeout:
			sleep(1)
			ws_conn_timeout -= 1


		while ws.sock.connected:
			print 'MAIN: Socket is connected!'
			while ws_queue.qsize():
				try:
					msg = ws_queue.get(0)
					print 'MAIN: Got queue '+msg
				except Queue.Empty:
					pass
			sleep(5)
	except KeyboardInterrupt:
		ws.close()
		sleep(1)
		print 'Shutting down...'

