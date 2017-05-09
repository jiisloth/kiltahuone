import socket
import os
import textwrap
import subprocess
import config

from time import strftime, localtime, time, sleep
from colorama import Fore, Back, Style

FNULL = open(os.devnull, "w")
place = []
placers = {}
placetimer = time() - 90


class Message:
    def __init__(self, data, irc):
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
            if data[2] == config.nick:
                self.channel = "query"
            elif self.sender == config.ircserver:
                self.channel = "msg form server"
            else:
                self.channel = data[2]
            self.msg = " ".join(data[3:])[1:]


def connect():
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Trying to connect to", config.ircserver)
    irc.connect((config.ircserver, config.port))
    irc.send("USER {} a a :{}\r\n".format(config.username, config.realname).encode('utf-8'))
    irc.send("NICK {}\n".format(config.nick).encode('utf-8'))
    for channel in config.channels:
        irc.send("JOIN {}\n".format(channel).encode('utf-8'))
    return irc


def inputloop(irc):
    status = "connecting"
    while True:
        global placetimer
        placetimeout = False
        try:
            msgbuffer = str(irc.recv(4096), "UTF-8", "replace").splitlines()
        except ConnectionResetError:
            return 1
        for msg in msgbuffer:
            m = Message(msg, irc)

            if m.type == "JOIN" and status == "connecting":
                print("\nJoined channel: " + msg.split()[2].lstrip(":"))

            if m.type == "332":
                topic = " ".join(msg.split()[4:]).lstrip(":")
                topics[msg.split()[3]] = topic
            if m.type == "TOPIC":
                topic = " ".join(msg.split()[3:]).lstrip(":")
                topics[msg.split()[2]] = topic
                spacing = checklines()
                multiprint(spacing)

            if (m.channel in config.channels or m.channel == "query") and config.testmode <= 1:
                status = "connected"
                if m.channel == config.place:
                    placer(irc, m)
                else:
                    status = "messaging"
                    placetimer = time()
                    parsemsg(m)
                    addtolist(m)
                    spacing = checklines()
                    multiprint(spacing)
            if config.testmode >= 1:
                print("")
                print(msg)


def placer(irc, m):
    spot = m.msg.split(" ")
    spot[0] = spot[0].split("-")
    if len(spot[0]) == 2:
        if len(spot) == 2:
            spot[1] = spot[1].lower()
            if spot[0][0].isdigit() and spot[0][1].isdigit():
                if int(spot[0][0]) < config.columns and int(spot[0][1]) < config.rows*2:
                    if spot[1] in config.placeBC.keys():
                        if m.sender in placers.keys():
                            placers[m.sender] += 1
                        else:
                            placers[m.sender] = 1

                        if int(spot[0][1]) % 2 == 0:
                            place[int(int(spot[0][1]) / 2)][int(spot[0][0])][0] = config.placeBC[spot[1]]
                            place[int(int(spot[0][1]) / 2)][int(spot[0][0])][2] = m.sender
                        if int(spot[0][1]) % 2 == 1:
                            place[int((int(spot[0][1]) - 1) / 2)][int(spot[0][0])][1] = config.placeFC[spot[1]]
                            place[int((int(spot[0][1]) - 1) / 2)][int(spot[0][0])][3] = m.sender
                        printplace()
                    else:
                        sendmessage(irc, config.place, "Color not good enough!!")
                else:
                    sendmessage(irc, config.place, "these numbers seem to be stupid.")
        elif len(spot) == 1:
            spot = spot[0]
            if spot[0].isdigit() and spot[1].isdigit():
                color = "??"
                sender = "??"
                if int(spot[1]) % 2 == 0:
                    color = place[int(int(spot[1]) / 2)][int(spot[0])][0]
                    sender = place[int(int(spot[1]) / 2)][int(spot[0])][2]
                    for ckey in config.placeBC.keys():
                        if config.placeBC[ckey] == color:
                            color = ckey
                if int(spot[1]) % 2 == 1:
                    color = place[int((int(spot[1]) - 1) / 2)][int(spot[0])][1]
                    sender = place[int((int(spot[1]) - 1) / 2)][int(spot[0])][3]
                    for ckey in config.placeFC.keys():
                        if config.placeFC[ckey] == color:
                            color = ckey
                message = spot[0] + "-" + spot[1] + " is " + color + " and was placed by " + sender
                sendmessage(irc, config.place, message)
    if m.msg == "!stats":
        for key in placers:
            stats = key + ": " + str(placers[key])
            sendmessage(irc, config.place, stats)
    if m.msg == "!size":
        sendmessage(irc, config.place, str(config.columns) + "x" + str(config.rows*2))
    if m.msg == "!colors":
        message = "Colors: " + " ".join(config.placeBC.keys())
        sendmessage(irc, config.place, message)

def sendmessage(irc, channel, message):
    irc.send("PRIVMSG {} :{}\n".format(channel, message).encode('utf-8'))
    sleep(0.1)


def printplace():
    global placetimer
    if time() < placetimer + 90:
        return
    placetext = ""
    for rows in place:
        row = ""
        for columns in rows:
            pixel = "".join(columns[:2]) + "\u2584" + Style.RESET_ALL
            row += pixel
        placetext += row

    screenprint = ("\033[F" * config.rows)
    screenprint += (" " * config.columns * config.rows)
    screenprint += ("\033[F" * config.rows)
    print(screenprint + placetext + "\033[F" * config.rows, end="")


def playsound(soundfile):
    global lasttime
    if time() < lasttime + 30:
        return
    lasttime = time()
    subprocess.Popen(["omxplayer", soundfile], stdin=None, stdout=FNULL, stderr=subprocess.STDOUT, close_fds=True)


def parsemsg(m):
    m.parsedmsg = textwrap.fill("{} {}: {}".format(strftime("%H:%M", m.time), m.sender, m.msg), width=config.columns)
    for hilight in config.hilights:
        if hilight in m.parsedmsg:
            m.parsedmsg = ('\033[1m' + Fore.RED + hilight + Style.RESET_ALL + '\033[0m').join(
                m.parsedmsg.split(hilight))
            if hilight == config.nick + ":":
                playsound("sounds/daisy.wav")
            else:
                playsound("sounds/hilight.wav")

    if "kaljaa" in m.msg:
        playsound("sounds/beer.wav")

    if m.msg in config.commands:
        command, args = config.commands[m.msg]
        if command == "playsound":
            playsound(*args)
    sender = 0
    for char in m.sender:
        sender += ord(char)
    m.parsedmsg = (config.textColors[sender % len(config.textColors)] + m.sender + Style.RESET_ALL).join(
        m.parsedmsg.split(m.sender, 1))


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
        if linecount > config.rows:
            oldestmessage = messages[0]
            for m in messages:
                if m.time < oldestmessage.time:
                    oldestmessage = m
            messages.remove(oldestmessage)
        elif linecount <= config.rows:
            return config.rows - linecount


def multiprint(spacing):
    channelflag = ""
    screenprint = ("\033[F" * config.rows)
    screenprint += (" " * config.columns * config.rows)
    screenprint += ("\033[F" * config.rows)
    for i in range(spacing):
        screenprint += "\n"
    for m in messages:
        screenprint += "\n"
        if channelflag != m.channel:
            channelflag = m.channel
            if m.channel == "query":
                screenprint += Back.BLUE + " Query".ljust(config.columns)[:config.columns] + Style.RESET_ALL + "\n"
            else:
                screenprint += config.bgColors[config.channels.index(m.channel) % len(
                    config.bgColors)] + Fore.BLACK + str(m.channel + " | " + topics[m.channel]).ljust(config.columns)[
                                                     :config.columns] + Style.RESET_ALL + "\n"
        screenprint += m.parsedmsg
    print(screenprint, end="")


def createplace():
    for i in range(config.rows):
        row = []
        for j in range(config.columns):
            column = [Back.BLACK, Fore.BLACK, "me", "me"]
            row.append(column[:])
        place.append(row[:])


if __name__ == "__main__":
    if config.place in config.channels:
        createplace()
    while True:
        lasttime = 0
        messages = []
        topics = {}
        for channel in config.channels:
            topics[channel] = ""
        if config.osclear:
            os.system("clear")
        error = inputloop(connect())
        if error == 1:
            print("Connection error!")
            if config.wait >= 0:
                print("Trying again after " + str(config.wait) + " seconds")
                sleep(config.wait)
        else:
            print("Somehow got out of the input loop with error value:", error)
            break
    print("Shutting down.")
