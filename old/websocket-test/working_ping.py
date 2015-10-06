from urllib import urlopen
import websocket
import thread
import time

def on_message(ws, message):
    print message
    if str(message) in ('2::', '3::'):
    	print('ACK (' +message+') ')
    	ws.send(message)

def on_error(ws, error):
    print error

def on_close(ws):
    print "[Socket Closed]"

def on_open(ws):
	print '[Socket Connected]'


if __name__ == "__main__":
	u = urlopen("http://www-cdn-twitch.saltybet.com:8000/socket.io/1/")
	response = u.readline()
	socketID = response.split(':')[0]

	ws = websocket.WebSocketApp("ws://www-cdn-twitch.saltybet.com:8000/socket.io/1/websocket/"+socketID, on_message = on_message, on_error = on_error, on_close = on_close)
	ws.on_open = on_open
	ws.run_forever()