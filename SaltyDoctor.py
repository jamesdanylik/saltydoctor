import threading
import Queue
import signal
import sys
from time import sleep
import logging # need to explicitly grab logging, else websocket does weird things
# gstreamer must be manually linked into venv to work... see gst_to_venv.sh

import Tkinter as tk

from urllib import urlopen
import websocket # note: this is 'websocket-client' on pip
import socket

# video stuff?
# needs install gi?
# also needs gst-plugins-bad?
# also needs gst-libav?
# obviously livestreamer too

import gi
from gi.repository import GObject as gobject, Gst as gst, GstPbutils as gstpb
import os
from livestreamer import Livestreamer, StreamError, PluginError, NoPluginError

class SaltySocketClient:
	def __init__(self, queue):
		logging.basicConfig()

		self.queue = queue
		self.running = False

		self.connect()

	def connect(self):
		if not self.running:
			u = urlopen("http://www-cdn-twitch.saltybet.com:8000/socket.io/1/")
			response = u.readline()
			socketID = response.split(':')[0]	

			self.ws = websocket.WebSocketApp(
				"ws://www-cdn-twitch.saltybet.com:8000/socket.io/1/websocket/"+socketID, 
				on_message = self.on_message, 
				on_error = self.on_error, 
				on_close = self.on_close)
			self.ws.on_open = self.on_open

			self.wst = threading.Thread(target=self.ws.run_forever)
			self.wst.daemon = True
			self.wst.start()

	def disconnect(self):
		# print 'WS: Shutdown'
		self.ws.close()

	def on_message(self, ws, msg):
		# print 'WS RECV: ' + msg
		if str(msg) != '1::':
			# print 'WS ACK: ' + msg
			ws.send(msg)
			self.queue.put(msg)

	def on_error(self, ws, err):
		print 'WS ERR: '+err
		self.running = False

	def on_open(self, ws):
		# print 'WS: [Socket Connected]'
		self.running = True

	def on_close(self, ws):
		# print 'WS: [Socket Closed]'
		self.running = False


class SaltyChatClient:
	def __init__(self, queue):
		self.queue = queue
		self.running = False

		self.host = 'irc.twitch.tv'
		self.port = 6667
		self.nick = 'ratherbelucky' # TODO: un-hardcode this
		self.pswd = 'oauth:uuquepqhh83tg7g4ta98m5hba3seo8' #TODO: get oauth automatically from login?
		self.chan = '#saltybet'

		self.connect()

	def connect(self):
		if not self.running:
			s = socket.socket()
			s.connect( (self.host, self.port) )
			s.send('PASS {}\r\n'.format(self.pswd).encode('utf-8'))
			s.send('NICK {}\r\n'.format(self.nick).encode('utf-8'))
			s.send('JOIN {}\r\n'.format(self.chan).encode('utf-8'))
			self.s = s
			self.running = True
			# print 'TC: [Chat Connected]'

			self.tct = threading.Thread(target=self.run)
			self.tct.daemon = True
			self.tct.start()

	def disconnect(self):
		if self.running:
			self.s.send('QUIT'.encode('utf-8'))
			self.s.close()
			self.running = False
			# print 'TC: [Chat Disconnected]'

	def send(self, msg):
		pass #TODO enable sending messages

	def run(self):
		while self.running:
			rsp = self.s.recv(4096).decode('utf-8')
			if rsp == 'PING :tmi.twitch.tv\r\n':
				self.s.send('PONG :tmi.twitch.tv\r\n'.encode('utf-8'))
				# print 'TC: PONG'
			elif 'PRIVMSG' in rsp:
				try: 
					msg = rsp[1:].split(':', 1)[1][:-1]
					usr = rsp[1:].split('!', 1)[0]
					print(usr+': '+msg)
					self.queue.put((usr, msg))
				except:
					print('!!!PARSE PRIVMSG ERROR!!! : '+rsp[:-1])

			sleep(0.1)

class SaltyMainGUI:
	def __init__(self, master):
		self.master = master
		self.frame = tk.Frame(self.master)

		gobject.threads_init()
		gst.init(None)
		self.livestreamer = Livestreamer()
		self.livestreamer.set_loglevel("info")
		self.livestreamer.set_logoutput(sys.stdout)
		self.fd = None

		try:
			self.streams = self.livestreamer.streams('http://www.twitch.tv/saltybet')
		except NoPluginError:
			exit("Livestreamer failed to handle the url.")
		except PluginError as err:
			exit("Livestreamer plugin error: {}".format(err))

		if not self.streams:
			exit("No streams found.")

		if 'best' not in self.streams:
			exit("Unable to select livestreamer quality.")

		self.stream = self.streams['best']

		try:
			self.fd = self.stream.open()
		except SteamError as err:
			self.exit("Livestreamer failed to open stream.")

		self.init_gui()
		# self.login()

		self.window_id = self.video.winfo_id()

		self.player = gst.ElementFactory.make('playbin', None)
		self.player.set_property('video-sink', None)
		self.player.set_property('uri', 'appsrc://')

		self.player.connect('source-setup', self.on_source_setup)

		self.bus = self.player.get_bus()
		self.bus.add_signal_watch()
		self.bus.enable_sync_message_emission()
		self.bus.connect('sync-message::element', self.on_sync_message, self.window_id)
		self.bus.connect('message::eos', self.on_eos)
		self.bus.connect('message::error', self.on_error)

		self.player.set_state(gst.State.PLAYING)

	def init_gui(self):
		self.master.title('SaltyDoctor')

		self.master.geometry('640x480')

		self.video = tk.Frame(self.master, bg='black')
		self.video.pack(side=tk.TOP, anchor=tk.N, expand=tk.YES, fill=tk.BOTH)

		self.mute_btn = tk.Button(self.master, text='Mute', command=self.mute_stream)
		self.mute_btn.pack()

		self.frame.pack()

	def shutdown(self):
		self.player.set_state(gst.State.NULL)
		self.master.destroy()

	def mute_stream(self):
		if self.player.get_property('mute'):
			self.player.set_property('mute', False)
		else:
			self.player.set_property('mute', True)

	def login(self):
		self.login_window = tk.Toplevel(self.master)
		self.app = SaltyLoginGUI(self.login_window)

	def on_source_setup(self, element, source):
		# print 'Source setup called.'
		source.connect("need-data", self.on_source_need_data)

	def on_source_need_data(self, source, length):
		try:
			data = self.fd.read(length)
		except IOError as err:
			exit('Failed to read data from stream.')

		if not data:
			source.emit('end-of-stream')
			return

		buf = gst.Buffer.new_wrapped(data)
		source.emit('push-buffer', buf)

	def on_sync_message(self, bus, message, window_id):
		# print 'On sync message called: ' + message.get_structure().get_name()
		if not message.get_structure() is None:
			if message.get_structure().get_name() == 'prepare-window-handle':
				# print 'Setting window xid'
				image_sink = message.src 
				image_sink.set_property('force-aspect-ratio', True)
				image_sink.set_window_handle(self.window_id)
			if message.get_structure().get_name() == 'missing-plugin':
				print 'Gstreamer missing plugin: ' + gstpb.missing_plugin_message_get_description(message)

	def on_eos(self, bus, msg):
		self.stop()

	def on_error(self, bus, msg):
		error = msg.parse_error()[1]
		exit(error)

class SaltyLoginGUI:
	def __init__(self, master):
		self.master = master
		self.frame = tk.Frame(self.master)

		self.master.title('Please Login')

		self.button = tk.Button(self.frame, text='Login', width=25, command=self.close_window)
		self.button.pack()
		self.frame.pack()

	def close_window(self):
		self.master.destroy()

def main():
	root = tk.Tk()
	app = SaltyMainGUI(root)
	root.protocol('WM_DELETE_WINDOW', app.shutdown)
	root.mainloop()

if __name__ == '__main__':
	main()


