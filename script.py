import socket
import os
import time
import sys
from time import strftime, localtime

import colorama
from colorama import Fore, Back, Style


ircserver = "irc.oulu.fi"
port = 6667

nick = "kiltahuonedev"
username = "kiltahuone"
realname = "kiltahuone"
channels = ["#kiltisbottest", "#kiltisbottest2"]
hilights = ["tissit"]

class Message:
	def __init__(self, data):
		self.channel = ""
		self.sender = ""
		self.channel = ""
		self.msg = ""
	
		data = data.split()
		
		self.time = strftime("%H:%M", localtime())
		self.type = data[1]

		if data[0] == "PING" or "PING" in data: 
			irc.send ("PONG {}\r\n".format(data[1]).encode('utf-8'))
		if self.type == "PRIVMSG":
			self.sender = data[0].lstrip(":").split("!")[0]
			if data[2] == nick:
				self.channel = "query"	
			elif self.sender == ircserver:
				self.channel = "msg form server"
			else:
				self.channel = data[2]
			self.msg = " ".join(data[3:])[1:]
		


def connect():
	irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	irc.connect((ircserver, port))

	irc.send("USER {} a a :{}\r\n".format(username, realname).encode('utf-8'))
	irc.send("NICK {}\n".format(nick).encode('utf-8'))
	for channel in channels:
		irc.send("JOIN {}\n".format(channel).encode('utf-8'))
	return irc

def inputloop():
	while True:
		m = Message(str(irc.recv(4096),"UTF-8", "replace"))
		for channel in channels:
			if channel == m.channel:
				channelm(m)
		if m.channel == "query":
			query(m)
			
def query(m):
	colors(m)
	print("{} {} {}: {}".format(m.time, m.channel, m.sender ,m.msg))
	return 0

def channelm(m):
	colors(m)
	print("{} {} {}: {}".format(m.time, m.channel, m.sender ,m.msg))
	return 0

def colors(m):
	for hilight in hilights:
		if hilight in m.msg:
			m.sender =  Back.YELLOW + m.sender + Style.RESET_ALL
		else:
			m.sender = Fore.RED + m.sender + Style.RESET_ALL
	if m.channel == "query":
		m.channel = Fore.BLUE + "query from" + Style.RESET_ALL
	else:
		m.channel = Fore.YELLOW + m.channel + Style.RESET_ALL


if __name__ == "__main__":
	os.system("clear")
	irc = connect()
	inputloop()
