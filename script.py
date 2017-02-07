import socket
import os
import textwrap
from time import strftime, localtime

from colorama import Fore, Back, Style

ircserver = "irc.oulu.fi"
port = 6667

nick = "slotbot"
username = "kiltahuone"
realname = "OTiT kiltahuone"
channels = ["#otit.bottest"]
hilights = ["tissit", nick]
messages = []

bgColors = [Back.RED, Back.GREEN, Back.YELLOW, Back.MAGENTA, Back.CYAN, Back.WHITE]
textColors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.MAGENTA, Fore.CYAN, Style.BRIGHT + Fore.BLUE,
              Style.BRIGHT + Fore.RED, Style.BRIGHT + Fore.GREEN, Style.BRIGHT + Fore.YELLOW,
              Style.BRIGHT + Fore.MAGENTA, Style.BRIGHT + Fore.CYAN, Style.BRIGHT + Fore.WHITE]

rows = int(os.popen('stty size', 'r').read().split()[0])
columns = int(os.popen('stty size', 'r').read().split()[1])

class Message:
    def __init__(self, data):
        self.channel = ""
        self.sender = ""
        self.msg = ""
        self.parsedmsg = ""

        data = data.split()

        self.time = localtime()
        self.type = data[1]

        if data[0] == "PING" or "PING" in data:
            irc.send("PONG {}\r\n".format(data[1]).encode('utf-8'))
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
        m = Message(str(irc.recv(4096), "UTF-8", "replace"))

        for channel in channels:
            if channel == m.channel or m.channel == "query":
                parsemsg(m)
                addtolist(m)
                spacing = checklines()
                # cprint(m)
                multiprint(spacing)


def parsemsg(m):
    msg = m.msg
    for hilight in hilights:
        if hilight in msg:
            msg = ('\033[1m' + hilight + '\033[0m').join(msg.split(hilight))
    sender = 0
    for char in m.sender:
        sender += ord(char)
    sender = textColors[sender%len(textColors)] + m.sender + Style.RESET_ALL
    m.parsedmsg = textwrap.fill("{} {}: {}".format(strftime("%H:%M", m.time), sender, msg), width=columns)




def addtolist(m):
    oldmessages = []
    newmessages = []
    for message in messages:
        if message.channel == m.channel:
            newmessages.append(message)
        else:
            oldmessages.append(message)
    newmessages.append(m)
    del messages[:]
    messages.extend(oldmessages)
    messages.extend(newmessages)


def checklines():
    while True:
        linecount = 0
        channelflag = ""
        for m in messages:
            if channelflag != m.channel:
                channelflag = m.channel
                linecount += 1
            linecount += len(m.parsedmsg.split("\n"))
        if linecount > rows:
            oldestmessage = messages[0]
            for m in messages:
                if m.time < oldestmessage.time:
                    oldestmessage = m
            messages.remove(oldestmessage)
        elif linecount <= rows:
            break
    return rows - linecount


def multiprint(spacing):
    channelflag = ""
    screenprint = ""
    for i in range(spacing):
        screenprint += "\n"
    for m in messages:
        screenprint += "\n"
        if channelflag != m.channel:
            channelflag = m.channel
            if m.channel == "query":
                screenprint += Back.BLUE + Fore.BLACK + " Query".ljust(columns) + Style.RESET_ALL + "\n"
            else:
                screenprint += bgColors[channels.index(m.channel)%len(bgColors)] + Fore.BLACK + m.channel.ljust(columns) + Style.RESET_ALL + "\n"
        screenprint += m.parsedmsg
    print(screenprint)


def cprint(m):
    colors(m)
    print(textwrap.fill("{} {} {}: {}".format(strftime("%H:%M", m.time), m.channel, m.sender, m.msg), width=columns))
    return 0


def colors(m):
    for hilight in hilights:
        if hilight in m.msg:
            m.sender = Back.YELLOW + m.sender + Style.RESET_ALL
        else:
            m.sender = Fore.RED + m.sender + Style.RESET_ALL
    if m.channel == "query":
        m.channel = Fore.CYAN + "query from" + Style.RESET_ALL
    else:
        m.channel = Fore.YELLOW + m.channel + Style.RESET_ALL


if __name__ == "__main__":
    os.system("clear")
    irc = connect()
    inputloop()
