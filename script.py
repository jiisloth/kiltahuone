import socket
import colorama
from colorama import Fore, Back, Style

ircserver = "irc.elisa.fi"
port = 6667

nick = "kiltisbot"
username = "kiltisbot"
realname = "kiltisbot"
channels = ["#kiltisbottest", "#kiltisbottest2"]
	
def main():
	irc = connect()
	inputloop(irc)

def connect():
	irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	irc.connect((ircserver, port))

	irc.send("USER {} a a :{}\r\n".format(username, realname).encode('utf-8'))
	irc.send("NICK {}\n".format(nick).encode('utf-8'))
	for channel in channels:
		irc.send("JOIN {}\n".format(channel).encode('utf-8'))
	return irc

def inputloop(irc):
	while True:
		try:
			data = str(irc.recv(4096),"UTF-8", "replace")
			data = data.split()
			name = data[0].lstrip(":").split("!")
			msg = " ".join(data[3:])
			msg = msg[1:]
			if "PING" == data[0]:
				irc.send ( "PONG {}\r\n".format(data[1]).encode('utf-8'))
			for channel in channels:
				if channel == data[2]:
					channelm(irc, data[2], name[0], msg)
			if "kiltisbot" == data[2] and name[0] != ircserver:
				query(irc, name[0], msg)
		except IndexError:
			pass
			
def query(irc, name, msg):
	print( Fore.YELLOW + "query from " + Fore.RED + name + Style.RESET_ALL + ": " + msg)
	return 0

def channelm(irc, channel, name, msg):
	print( Fore.YELLOW + channel + " " + Fore.RED + name + Style.RESET_ALL + ": " + msg)
	return 0

main()
