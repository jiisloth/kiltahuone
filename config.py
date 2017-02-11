from colorama import Fore, Back, Style
import os

osclear = True
testmode = 0  # 0 = Normal, 1 = print all, 2 = debug prints only

ircserver = "irc.oulu.fi"
port = 6667

nick = "kiltahuone"
username = "kiltahuone"
realname = "OTiT kiltahuone"
channels = ["#otit.kiltahuone", "#frisbeer", "#otit", "#otit.2016"]
hilights = ["tissit", nick + ":"]

wait = 10

commands = {"!oviauki": ("playsound", ["sounds/oviauki.wav"])}


bgColors = [Back.RED, Back.GREEN, Back.YELLOW, Back.MAGENTA, Back.CYAN, Back.WHITE]
textColors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.MAGENTA, Fore.CYAN, Style.BRIGHT + Fore.BLUE,
              Style.BRIGHT + Fore.RED, Style.BRIGHT + Fore.GREEN, Style.BRIGHT + Fore.YELLOW,
              Style.BRIGHT + Fore.MAGENTA, Style.BRIGHT + Fore.CYAN, Style.BRIGHT + Fore.WHITE]

rows = int(os.popen('stty size', 'r').read().split()[0])
columns = int(os.popen('stty size', 'r').read().split()[1])