from colorama import Fore, Back, Style
import os

osclear = True
testmode = 0  # 0 = Normal, 1 = print all, 2 = debug prints only

ircserver = "irc.oulu.fi"
port = 6667

nick = "Kiltahuone2"
username = "Kiltahuone2"
realname = "OTiT kiltahuone"
#channels = ["#otit.kiltahuone", "#frisbeer", "#otit", "#otit.2016", "#otit.place"]
channels = ['#otit.bottest']
place = "#otit.bottest"
hilights = ["tissit", nick + ":"]

wait = 10

commands = {"!oviauki": ("playsound", ["sounds/oviauki.wav"])}

placeBC = {"black": Back.BLACK, "red": Back.RED, "green": Back.GREEN, "yellow": Back.YELLOW, "blue": Back.BLUE,
               "magenta": Back.MAGENTA, "cyan": Back.CYAN, "white": Back.WHITE}
placeFC = {"black": Fore.BLACK, "red": Fore.RED, "green": Fore.GREEN, "yellow": Fore.YELLOW, "blue": Fore.BLUE,
               "magenta": Fore.MAGENTA, "cyan": Fore.CYAN, "white": Fore.WHITE}
bgColors = [Back.RED, Back.GREEN, Back.YELLOW, Back.MAGENTA, Back.CYAN, Back.WHITE]
textColors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.MAGENTA, Fore.CYAN, Style.BRIGHT + Fore.BLUE,
              Style.BRIGHT + Fore.RED, Style.BRIGHT + Fore.GREEN, Style.BRIGHT + Fore.YELLOW,
              Style.BRIGHT + Fore.MAGENTA, Style.BRIGHT + Fore.CYAN, Style.BRIGHT + Fore.WHITE]

rows = int(os.popen('stty size', 'r').read().split()[0])
columns = int(os.popen('stty size', 'r').read().split()[1])
