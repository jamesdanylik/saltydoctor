#!/usr/bin/python2

import wx

app = wx.App()

frame = wx.Frame(None, -1, 'Salty Doctor')
frame.Show()

class Login(wx.Frame):
	def __init__(self, parent, title):
		super(Login, self).__init__(parent, title=title, size=(320, 120))
		self.Show()


app.MainLoop()