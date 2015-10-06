import Tkinter
import requests
import subprocess
import math

class Salty(Tkinter.Tk):

	# Init method called when the class is constructed
	def __init__(self,parent):
		# have to call the parent constructor
		Tkinter.Tk.__init__(self,parent)
		
		# always a good idea to have a reference to parent
		self.parent = parent
		self.session = requests.Session()

		self.initialize_statics()

		# intialize the GUI
		self.initialize_gui()

	# this function just saves all the 'static' type variables in our class; there's
	# probably a better way to do this, but I'm not sure what it is in Python
	def initialize_statics(self):
		self.urls = {}
		self.urls['base'] = 'http://www.saltybet.com/'
		self.urls['auth'] = self.urls['base'] + 'authenticate'
		self.urls['state']= self.urls['base'] + 'state.json'
		self.urls['zdata']= self.urls['base'] + 'zdata.json'
		self.urls['ncash']= self.urls['base'] + 'ajax_tournament_end.php'
		self.urls['tcash']= self.urls['base'] + 'ajax_tournament_start.php'
		self.urls['bet'] = self.urls['base'] + 'ajax_place_bet.php'
		self.urls['logout'] = self.urls['base'] + 'logout'

		# temporary hardcoded login object? 
		self.login = {}
		self.login['email'] = 'shiohakase@gmail.com'
		self.login['pword'] = 'jankenpo'
		self.login['authenticate'] = 'signin'
		self.login['signin'] = '1'

		self.colors = {
			'red': 'dark red',
			'dark red': 'darkgoldenrod',
			'dark blue': 'darkgoldenrod',
			'blue': 'royal blue',
			'green': 'lime green',
			'dark green': 'dark green',
			'black': 'black',
			'gray': 'light gray',
			'white': 'white',
			'purple': 'dark violet'
		}

		self.intervals = {
			'data': 5000,
			'state': 5000
		}

	# Methods to handle GUI initialization
	def initialize_gui(self):
		# Main window items
		self.title('Shio Hakase')
		self.windowicon = Tkinter.PhotoImage(file='hakase.png')
		self.tk.call('wm', 'iconphoto', self._w, self.windowicon)

		# User login and username/rank display
		self.user_frame = Tkinter.Frame(self)
		self.username_data = Tkinter.StringVar()
		self.username_data.set('Currently logged out.')
		self.username_label = Tkinter.Label(self.user_frame, textvariable=self.username_data)
		self.username_label.pack(side=Tkinter.LEFT)
		self.usercash_data = Tkinter.IntVar()
		self.usercash_data.set(0)
		self.usercash_label = Tkinter.Label(self.user_frame, textvariable=self.usercash_data)
		self.usercash_label.pack(side=Tkinter.LEFT)
		self.userbutn_data = Tkinter.StringVar()
		self.userbutn_data.set('Log in')
		self.userbutn_butn = Tkinter.Button(self.user_frame, textvariable=self.userbutn_data, command=self.sign_in)
		self.userbutn_butn.pack(padx=10, side=Tkinter.RIGHT)
		self.user_frame.pack(pady=10, fill=Tkinter.X)

		# Main dashboard with bookie status, tournament count, combantants, total pools,
		# (when available) and your bet status for this round. 
		self.dashboard_frame = Tkinter.Frame(self)
		self.players_frame = Tkinter.Frame(self.dashboard_frame)
		self.redplayer_frame = Tkinter.Frame(self.players_frame, background=self.colors['red'])
		self.blueplayer_frame = Tkinter.Frame(self.players_frame, background=self.colors['blue'])

		self.tstatus_data = Tkinter.StringVar()
		self.tstatus_data.set('Mode status unknown!')
		self.tstatus_label = Tkinter.Label(self.dashboard_frame, bg=self.colors['purple'], fg=self.colors['white'], textvariable=self.tstatus_data)
		self.tstatus_label.pack(fill=Tkinter.X, side=Tkinter.TOP)

		self.saltystatus_data = Tkinter.StringVar()
		self.saltystatus_data.set('SaltyBet round status unknown.')
		self.saltystatus_label = Tkinter.Label(self.dashboard_frame, bg=self.colors['green'], fg=self.colors['black'], textvariable=self.saltystatus_data)
		self.saltystatus_label.pack(fill=Tkinter.X, side=Tkinter.TOP)

		self.redplayer_data = Tkinter.StringVar()
		self.redplayer_data.set('Player 1')
		self.redplayer_label = Tkinter.Label(self.redplayer_frame, width=30, textvariable=self.redplayer_data, bg=self.colors['red'], fg=self.colors['white'])
		self.redplayer_label.pack()
		self.redtotal_data = Tkinter.StringVar()
		self.redtotal_data.set('$--')
		self.redtotal_label = Tkinter.Label(self.redplayer_frame, textvariable=self.redtotal_data, bg=self.colors['red'], fg=self.colors['gray'])
		self.redtotal_label.pack()
		self.redplayer_frame.pack(side=Tkinter.LEFT, fill=Tkinter.X, expand=1)

		self.blueplayer_data = Tkinter.StringVar()
		self.blueplayer_data.set('Player 2')
		self.blueplayer_label = Tkinter.Label(self.blueplayer_frame, width=30, textvariable=self.blueplayer_data, bg=self.colors['blue'], fg=self.colors['white'])
		self.blueplayer_label.pack()
		self.bluetotal_data = Tkinter.StringVar()
		self.bluetotal_data.set('$--')
		self.bluetotal_label = Tkinter.Label(self.blueplayer_frame, textvariable=self.bluetotal_data, bg=self.colors['blue'], fg=self.colors['gray'])
		self.bluetotal_label.pack()
		self.blueplayer_frame.pack(side=Tkinter.LEFT, fill=Tkinter.X, expand=1)

		self.betstatus_data = Tkinter.StringVar()
		self.betstatus_data.set('Can\'t place bets without logging in!')
		self.betstatus_label = Tkinter.Label(self.dashboard_frame, bg=self.colors['green'], fg=self.colors['black'], textvariable=self.betstatus_data)
		self.betstatus_label.pack(fill=Tkinter.X, side=Tkinter.BOTTOM)

		self.players_frame.pack(fill=Tkinter.X)
		self.dashboard_frame.pack(fill=Tkinter.X)

		# Bottom status bar
		self.status_data = Tkinter.StringVar()
		self.status_data.set("Initialization complete.")
		self.status_label = Tkinter.Label(self, anchor=Tkinter.W, relief=Tkinter.SUNKEN, textvariable=self.status_data)
		self.status_label.pack(fill=Tkinter.X, side=Tkinter.BOTTOM)

		# Quickbet area 
		self.mquickbet_frame = Tkinter.Frame(self)
		self.mquickbet_btn1 = Tkinter.Button(self.mquickbet_frame, text='1', command=lambda: self.quickbet_set(int(math.floor(1.0/100*self.usercash_data.get()))))
		self.mquickbet_btn1.pack(side=Tkinter.LEFT)
		self.mquickbet_btn2 = Tkinter.Button(self.mquickbet_frame, text='3', command=lambda: self.quickbet_set(int(math.floor(3.0/100*self.usercash_data.get()))))
		self.mquickbet_btn2.pack(side=Tkinter.LEFT)
		self.mquickbet_btn3 = Tkinter.Button(self.mquickbet_frame, text='5', command=lambda: self.quickbet_set(int(math.floor(5.0/100*self.usercash_data.get()))))
		self.mquickbet_btn3.pack(side=Tkinter.LEFT)
		self.mquickbet_btn4 = Tkinter.Button(self.mquickbet_frame, text='10', command=lambda: self.quickbet_set(int(math.floor(10.0/100*self.usercash_data.get()))))
		self.mquickbet_btn4.pack(side=Tkinter.LEFT)
		self.mquickbet_btn5 = Tkinter.Button(self.mquickbet_frame, text='15', command=lambda: self.quickbet_set(int(math.floor(15.0/100*self.usercash_data.get()))))
		self.mquickbet_btn5.pack(side=Tkinter.LEFT)
		self.mquickbet_btn6 = Tkinter.Button(self.mquickbet_frame, text='20', command=lambda: self.quickbet_set(int(math.floor(20.0/100*self.usercash_data.get()))))
		self.mquickbet_btn6.pack(side=Tkinter.LEFT)
		self.mquickbet_btn7 = Tkinter.Button(self.mquickbet_frame, text='25', command=lambda: self.quickbet_set(int(math.floor(25.0/100*self.usercash_data.get()))))
		self.mquickbet_btn7.pack(side=Tkinter.LEFT)
		self.mquickbet_btn8 = Tkinter.Button(self.mquickbet_frame, text='33', command=lambda: self.quickbet_set(int(math.floor(33.0/100*self.usercash_data.get()))))
		self.mquickbet_btn8.pack(side=Tkinter.LEFT)
		self.mquickbet_btn9 = Tkinter.Button(self.mquickbet_frame, text='50', command=lambda: self.quickbet_set(int(math.floor(50.0/100*self.usercash_data.get()))))
		self.mquickbet_btn9.pack(side=Tkinter.LEFT)
		self.mquickbet_btn10 = Tkinter.Button(self.mquickbet_frame, text='70', command=lambda: self.quickbet_set(int(math.floor(70.0/100*self.usercash_data.get()))))
		self.mquickbet_btn10.pack(side=Tkinter.LEFT)
		self.mquickbet_btn11 = Tkinter.Button(self.mquickbet_frame, text='90', command=lambda: self.quickbet_set(int(math.floor(90.0/100*self.usercash_data.get()))))
		self.mquickbet_btn11.pack(side=Tkinter.LEFT)
		self.mquickbet_btn12 = Tkinter.Button(self.mquickbet_frame, text='100', command=lambda: self.quickbet_set(int(math.floor(1.0*self.usercash_data.get()))))
		self.mquickbet_btn12.pack(side=Tkinter.LEFT)
		self.mquickbet_frame.pack(fill=Tkinter.X, side=Tkinter.BOTTOM)

		# Manual bet entry field and commit buttons
		self.mbet_frame = Tkinter.Frame(self)
		self.mbetred_tgle = Tkinter.IntVar()
		self.mbetred_butn = Tkinter.Checkbutton(self.mbet_frame, command=self.preparebet_red, activeforeground=self.colors['red'], highlightcolor=self.colors['black'], selectcolor=self.colors['dark red'], bg=self.colors['red'], fg=self.colors['white'], text='Bet Red', var=self.mbetred_tgle, indicatoron=False)
		self.mbetred_butn.pack(side=Tkinter.LEFT)
		self.mbetamnt_entry = Tkinter.Entry(self.mbet_frame, justify=Tkinter.CENTER)
		self.mbetamnt_entry.pack(fill=Tkinter.X, expand=1, side=Tkinter.LEFT)
		self.mbetamnt_entry.delete(0, Tkinter.END)
		self.mbetamnt_entry.insert(0, "place manual bet...")
		self.mbetamnt_entry.bind('<Button-1>', self.mbet_entry_handler)
		self.mbetamnt_entry.bind('<Button-2>', self.mbet_entry_placenow)
		self.mbetamnt_entry.bind('<Button-3>', self.mbet_entry_reset)
		self.mbetblue_tgle = Tkinter.IntVar()
		self.mbetblue_butn = Tkinter.Checkbutton(self.mbet_frame, command=self.preparebet_blue, activeforeground=self.colors['blue'], highlightcolor=self.colors['black'], selectcolor=self.colors['dark blue'], bg=self.colors['blue'], fg=self.colors['white'], text='Bet Blue', var=self.mbetblue_tgle, indicatoron=False)
		self.mbetblue_butn.pack(side=Tkinter.RIGHT)
		self.mbet_frame.pack(fill=Tkinter.X, side=Tkinter.BOTTOM)

		# Checkbutton controll bar
		self.controlbar_frame = Tkinter.Frame(self)
		self.alerts_tgle = Tkinter.IntVar()
		self.alerts_butn = Tkinter.Checkbutton(self.controlbar_frame, command=self.alert_toggle, variable=self.alerts_tgle, selectcolor=self.colors['dark green'], highlightcolor=self.colors['black'], activebackground=self.colors['green'], activeforeground=self.colors['black'], indicatoron=False, text='Round Alarm')
		self.alerts_tgle.set(1)
		self.alerts_butn.pack(fill=Tkinter.X, expand=1, side=Tkinter.LEFT)
		self.mute_tgle = Tkinter.IntVar()
		self.mute_butn = Tkinter.Checkbutton(self.controlbar_frame, variable=self.mute_tgle, selectcolor=self.colors['dark green'], highlightcolor=self.colors['black'], activebackground=self.colors['green'], activeforeground=self.colors['black'], indicatoron=False, text='Mute')
		self.mute_butn.pack(fill=Tkinter.X, expand=1, side=Tkinter.LEFT)
		self.alertfav_tgle = Tkinter.IntVar()
		self.alertfav_butn = Tkinter.Checkbutton(self.controlbar_frame, variable=self.alertfav_tgle, selectcolor=self.colors['dark green'], highlightcolor=self.colors['black'], activebackground=self.colors['green'], activeforeground=self.colors['black'], indicatoron=False, text='Favorites')
		self.alertfav_tgle.set(1)
		self.alertfav_butn.pack(fill=Tkinter.X, expand=1, side=Tkinter.LEFT)
		self.history_tgle = Tkinter.IntVar()
		self.history_butn = Tkinter.Checkbutton(self.controlbar_frame, variable=self.history_tgle, selectcolor=self.colors['dark green'], highlightcolor=self.colors['black'], activebackground=self.colors['green'], activeforeground=self.colors['black'], state=Tkinter.DISABLED, indicatoron=False, text='Record')
		self.history_butn.pack(fill=Tkinter.X, expand=1, side=Tkinter.LEFT)
		self.auto_tgle = Tkinter.IntVar()
		self.auto_butn = Tkinter.Checkbutton(self.controlbar_frame, variable=self.auto_tgle, selectcolor=self.colors['dark green'], highlightcolor=self.colors['black'], activebackground=self.colors['green'], activeforeground=self.colors['black'], state=Tkinter.DISABLED, indicatoron=False, text='Auto')
		self.auto_butn.pack(fill=Tkinter.X, expand=1, side=Tkinter.LEFT)
		self.controlbar_frame.pack(fill=Tkinter.X, side=Tkinter.BOTTOM)

	def test(self):
		self.status_data.set('Enter was pressed.')

	def quickbet_set(self, amnt):
		self.mbetamnt_entry.delete(0, Tkinter.END)
		self.mbetamnt_entry.insert(0, amnt)

	def alert_toggle(self):
		if self.alerts_tgle.get() == 0:
			self.mute_tgle.set(0)
			self.mute_butn.config(state='disabled')
		else:
			self.mute_butn.config(state = 'normal')

	def quit(self, event):
		app.destroy()

	def update_state(self):
		r = self.session.get(self.urls['state'])
		data = r.json()
		self.redplayer_data.set(data['p1name'])
		self.redtotal_data.set('$'+data['p1total'])
		self.blueplayer_data.set(data['p2name'])
		self.bluetotal_data.set('$'+data['p2total'])
		if data['status'] == 'locked':
			self.saltystatus_data.set('Bets are locked until the next match.')
			self.mute_tgle.set(0)
		elif data['status'] == 'open':
			if (not self.saltystatus_data.get() == 'Bets are OPEN!') and self.userbutn_data.get() == 'Sign out':
				self.betstatus_data.set('No bet placed this round.')
			self.saltystatus_data.set('Bets are OPEN!')
			if self.alerts_tgle.get() == 1 and self.mute_tgle.get() ==  0:
				self.play_mp3('chime.mp3')

		elif data['status'] == '1':
			self.saltystatus_data.set(data['p1name'] + ' wins! Payouts to Team Red.')
		elif data['status'] == '2':
			self.saltystatus_data.set(data['p2name'] + ' wins! Payouts to Team Blue.')
		self.tstatus_data.set(data['remaining'])

		if self.userbutn_data.get() == 'Sign out':
			r = self.session.get(self.urls['ncash'])
			self.usercash_data.set(r.text)

		self.after(self.intervals['state'], self.update_state)

	def play_mp3(self, song):
		vol = 32768/2
		subprocess.Popen(['mpg123', '-f', str(vol), '-q', song ], stdin=subprocess.PIPE, stdout=None)

	def sign_in(self):
		r = self.session.post(self.urls['auth'], data=self.login)
		if r.status_code == 200:
			y = self.session.get(self.urls['ncash'])
			self.usercash_data.set(y.text)
			self.userbutn_data.set('Sign out')
			self.username_data.set('Hakase (hardcoded)')
			self.status_data.set('Signed in to Hakase.')
			self.betstatus_data.set('No bet placed this round.')
			self.userbutn_butn.config(command=self.sign_out)
		else:
			self.status_data.set('Sign in error.')

	def sign_out(self):
		if self.userbutn_data.get() == 'Sign out':
			r = self.session.get(self.urls['logout'])
			self.userbutn_data.set('Log in')
			self.username_data.set('Currently logged out.')
			self.status_data.set('Logged out.')
			self.betstatus_data.set('Can\'t place bets without logging in!')
			self.session = requests.Session()

	def preparebet_red(self):
		self.mbetblue_tgle.set(0)
		self.mquickbet_btn1.config(bg=self.colors['red'], fg=self.colors['white'])
		self.mquickbet_btn2.config(bg=self.colors['red'], fg=self.colors['white'])
		self.mquickbet_btn3.config(bg=self.colors['red'], fg=self.colors['white'])
		self.mquickbet_btn4.config(bg=self.colors['red'], fg=self.colors['white'])
		self.mquickbet_btn5.config(bg=self.colors['red'], fg=self.colors['white'])
		self.mquickbet_btn6.config(bg=self.colors['red'], fg=self.colors['white'])
		self.mquickbet_btn7.config(bg=self.colors['red'], fg=self.colors['white'])
		self.mquickbet_btn8.config(bg=self.colors['red'], fg=self.colors['white'])
		self.mquickbet_btn9.config(bg=self.colors['red'], fg=self.colors['white'])
		self.mquickbet_btn10.config(bg=self.colors['red'], fg=self.colors['white'])
		self.mquickbet_btn11.config(bg=self.colors['red'], fg=self.colors['white'])
		self.mquickbet_btn12.config(bg=self.colors['red'], fg=self.colors['white'])
		if self.mbetred_tgle.get() == 0:
			self.preparebet_clear() 

	def preparebet_blue(self):
		self.mbetred_tgle.set(0)
		self.mquickbet_btn1.config(bg=self.colors['blue'], fg=self.colors['white'])
		self.mquickbet_btn2.config(bg=self.colors['blue'], fg=self.colors['white'])
		self.mquickbet_btn3.config(bg=self.colors['blue'], fg=self.colors['white'])
		self.mquickbet_btn4.config(bg=self.colors['blue'], fg=self.colors['white'])
		self.mquickbet_btn5.config(bg=self.colors['blue'], fg=self.colors['white'])
		self.mquickbet_btn6.config(bg=self.colors['blue'], fg=self.colors['white'])
		self.mquickbet_btn7.config(bg=self.colors['blue'], fg=self.colors['white'])
		self.mquickbet_btn8.config(bg=self.colors['blue'], fg=self.colors['white'])
		self.mquickbet_btn9.config(bg=self.colors['blue'], fg=self.colors['white'])
		self.mquickbet_btn10.config(bg=self.colors['blue'], fg=self.colors['white'])
		self.mquickbet_btn11.config(bg=self.colors['blue'], fg=self.colors['white'])
		self.mquickbet_btn12.config(bg=self.colors['blue'], fg=self.colors['white'])
		if self.mbetblue_tgle.get() == 0:
			self.preparebet_clear() 

	def preparebet_clear(self):
		self.mquickbet_btn1.config(bg=self.colors['black'], fg=self.colors['green'])
		self.mquickbet_btn2.config(bg=self.colors['black'], fg=self.colors['green'])
		self.mquickbet_btn3.config(bg=self.colors['black'], fg=self.colors['green'])
		self.mquickbet_btn4.config(bg=self.colors['black'], fg=self.colors['green'])
		self.mquickbet_btn5.config(bg=self.colors['black'], fg=self.colors['green'])
		self.mquickbet_btn6.config(bg=self.colors['black'], fg=self.colors['green'])
		self.mquickbet_btn7.config(bg=self.colors['black'], fg=self.colors['green'])
		self.mquickbet_btn8.config(bg=self.colors['black'], fg=self.colors['green'])
		self.mquickbet_btn9.config(bg=self.colors['black'], fg=self.colors['green'])
		self.mquickbet_btn10.config(bg=self.colors['black'], fg=self.colors['green'])
		self.mquickbet_btn11.config(bg=self.colors['black'], fg=self.colors['green'])
		self.mquickbet_btn12.config(bg=self.colors['black'], fg=self.colors['green'])

	def mbet_entry_handler(self, event):
		self.mbetamnt_entry.delete(0, Tkinter.END)
		self.status_data.set('Manual bet started! Complete card to bet!')

	def mbet_entry_reset(self, event):
		self.quickbet_set("place manual bet...")
		self.status_data.set('Manual bet aborted!')

	def mbet_entry_placenow(self, event):
		if self.saltystatus_data.get() == 'Bets are OPEN!' and self.betstatus_data.get() == 'No bet placed this round.'\
		and int(self.mbetamnt_entry.get()) <= self.usercash_data.get():
			bet = {
				'selectedplayer': 0,
				'wager': int(self.mbetamnt_entry.get())
			}
			if self.mbetred_tgle.get() == 1:
				bet['selectedplayer'] = 'player1'
			elif self.mbetblue_tgle.get() == 1:
				bet['selectedplayer'] = 'player2'
			else:
				print 'Error occured in bet process!'
				return


			self.session.post(self.urls['bet'], bet)
		else:
			print 'Error occured in bet process!'

if __name__ == "__main__":
	app = Salty(None)
	app.after(1000,app.update_state)
	app.mainloop()