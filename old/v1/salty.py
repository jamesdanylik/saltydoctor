#!/usr/bin/python2
import requests
import sys
import select

urls = {}
urls['salty'] = 'http://www.saltybet.com/'
urls['login'] = urls['salty'] + 'authenticate'
urls['state'] = urls['salty'] + 'state.json'
urls['zdata'] = urls['salty'] + 'zdata.json'
urls['ncash'] = urls['salty'] + 'ajax_tournament_end.php'
urls['tcash'] = urls['salty'] + 'ajax_tournament_start.php'

running = True

while running:
	x = keyboard.read(1000, timeout = 0)
	if len(x):
		running = False