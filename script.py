import socket
import os
import time
import sys
from time import strftime, localtime

import colorama
from colorama import Fore, Back, Style


ircserver = "irc.elisa.fi"
port = 6667

nick = "kiltahuone"
username = "kiltahuone"
realname = "kiltahuone"
channels = ["#kiltisbottest", "#kiltisbottest2"]


class Message:
	def __init__(self, data):
		self.channel = ""
		self.sender = ""
		self.channel = ""

		self.time = strftime("%H:%M", localtime())
		data = data.split()
		if data[0] == "PING":
			irc.send ("PONG {}\r\n".format(data[1]).encode('utf-8'))
		else:
			self.sender = data[0].lstrip(":").split("!")[0]
			if data[2] == nick:
				self.channel = "query"
			elif data[2] == ircserver:
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
				channelm(irc, m)
		if m.channel == "query":
			query(irc, m)
			
def query(irc, m):
	print("{} {}query from {}{}: {}{}".format(m.time, Fore.YELLOW, Fore.RED, m.sender ,Style.RESET_ALL, m.msg))
	return 0

def channelm(irc, m):
	print("{} {}{} {}{}: {}{}".format(m.time, Fore.YELLOW, m.channel, Fore.RED, m.sender ,Style.RESET_ALL, m.msg))

	return 0

if __name__ == "__main__":
	os.system("clear")
	irc = connect()
	inputloop()
