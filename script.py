import socket
import os
import textwrap
import subprocess
from time import strftime, localtime, time
from colorama import Fore, Back, Style

ircserver = "irc.oulu.fi"
port = 6667

nick = "kiltahuone2"
username = "kiltahuone"
realname = "OTiT kiltahuone"
#channels = ["#otit.kiltahuone", "#frisbeer", "#otit", "#otit.2016"]
channels = ["#otit.bottest"]
hilights = ["tissit", nick]
messages = []

bgColors = [Back.RED, Back.GREEN, Back.YELLOW, Back.MAGENTA, Back.CYAN, Back.WHITE]
textColors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.MAGENTA, Fore.CYAN, Style.BRIGHT + Fore.BLUE,
              Style.BRIGHT + Fore.RED, Style.BRIGHT + Fore.GREEN, Style.BRIGHT + Fore.YELLOW,
              Style.BRIGHT + Fore.MAGENTA, Style.BRIGHT + Fore.CYAN, Style.BRIGHT + Fore.WHITE]

rows = int(os.popen('stty size', 'r').read().split()[0])
columns = int(os.popen('stty size', 'r').read().split()[1])

lasttime = 0

FNULL = open(os.devnull, "w")

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
    print("Trying to connect to ", ircserver)
    irc.connect((ircserver, port))
    irc.send("USER {} a a :{}\r\n".format(username, realname).encode('utf-8'))
    irc.send("NICK {}\n".format(nick).encode('utf-8'))
    for channel in channels:
        irc.send("JOIN {}\n".format(channel).encode('utf-8'))
    return irc


def inputloop():
    while True:
        m = Message(str(irc.recv(4096), "UTF-8", "replace"))

        if m.channel in channels or m.channel == "query":
            parsemsg(m)
            addtolist(m)
            spacing = checklines()
            multiprint(spacing)


def playsound(soundfile):
    global lasttime
    if time() < lasttime + 30:
        return
    lasttime = time()
    subprocess.Popen(["omxplayer", soundfile], stdin=None, stdout=FNULL, stderr=subprocess.STDOUT, close_fds=True)


def parsemsg(m):
    m.parsedmsg = textwrap.fill("{} {}: {}".format(strftime("%H:%M", m.time), m.sender, m.msg), width=columns)
    for hilight in hilights:
        if hilight in m.parsedmsg:
            m.parsedmsg = ('\033[1m' + Fore.RED + hilight + Style.RESET_ALL + '\033[0m').join(m.parsedmsg.split(hilight))
            if hilight == nick:
                playsound("sounds/daisy.wav")
            else:
                playsound("sounds/hilight.wav")
    if m.msg in commands:
        command, args = commands[m.msg]
        command(*args)
    sender = 0
    for char in m.sender:
        sender += ord(char)
    m.parsedmsg = (textColors[sender % len(textColors)] + m.sender + Style.RESET_ALL).join(m.parsedmsg.split(m.sender, 1))



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
    screenprint = ("\033[F"*rows)
    screenprint += (" "*columns*rows)
    screenprint += ("\033[F"*rows)
    for i in range(spacing):
        screenprint += "\n"
    for m in messages:
        screenprint += "\n"
        if channelflag != m.channel:
            channelflag = m.channel
            if m.channel == "query":
                screenprint += Back.BLUE + " Query".ljust(columns) + Style.RESET_ALL + "\n"
            else:
                screenprint += bgColors[channels.index(m.channel)%len(bgColors)] + Fore.BLACK + m.channel.ljust(columns) + Style.RESET_ALL + "\n"
        screenprint += m.parsedmsg
    print(screenprint, end="")


commands = {"!oviauki": (playsound, ["sounds/oviauki.wav"])}


if __name__ == "__main__":
    os.system("clear")
    irc = connect()
    inputloop()
