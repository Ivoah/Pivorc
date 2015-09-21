import socket

class PyBot:
    def __init__(self, nick, server, channels):
        self.nick = nick
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dict = {}
        if len(server) != 2: server = (server, 6667) #If we don't have a port number, use 6667
        self.server = server
        if isinstance(channels, basestring): channels = [channels] #If we only have one channel, then make it a list for self.connect
        self.channels = channels
        self.debug = False
        self.bots = []
        self.verbose = False

    def connect(self):
        self.irc.connect(self.server)
        self.irc.send('NICK ' + self.nick + '\r\n') #Set nickname
        self.irc.send('USER ' + self.nick + ' 8 * :' + self.nick + '\r\n') #Set username
        while True:
            data = self.process()
            if 'End of /MOTD command' in data: break
        self.irc.send('JOIN ' + ','.join(self.channels) + '\r\n') #Join channels

    def setDebug(self, debug):
        self.debug = debug

    def setBots(self, bots):
        if isinstance(bots, basestring): self.bots = [bots]
        else: self.bots = bots

    def setVerbose(self, verbose):
        self.verbose = verbose

    def loadFactoids(self, filename):
        self.filename = filename
        factoids = open(self.filename)
        for factoid in factoids:
            text = '|'.join(factoid.split('|')[1:])
            text = text.replace('<action> ', '\x01ACTION ').replace('<action>', '\x01ACTION ').replace('<reply> ', '').replace('<reply>', '')
            self.dict[factoid.split('|')[0].lower()] = text

    def process(self):
        try:
            self.irc.setblocking(False)
            raw_message = self.irc.recv(512)
            self.irc.setblocking(True)
        except socket.error:
            return ''

        if self.debug: print(raw_message)
        if raw_message[0] == ':':
            nick = raw_message.split('!')[0][1:]
            message = raw_message.split()[1:]
        else:
            nick = None
            message = raw_message.split()
        command = message[0]
        message = message[1:]

        if command == 'PING':
            self.irc.send('PONG ' + ' '.join(message) + '\r\n')
        elif command == 'PRIVMSG':
            channel = message[0]
            message = message[1:]
            message[0] = message[0][1:]
            if nick in self.bots: i = 1
            else: i = 0
            if message[i][0] == '~':
                if channel == self.nick: channel = nick
                try:
                    if self.debug: print('PRIVMSG ' + channel + ' :' + self.dict[message[i][1:].lower()].replace('$nick', nick) + '\r\n')
                    self.irc.send('PRIVMSG ' + channel + ' :' + self.dict[message[i][1:].lower()].replace('$nick', nick) + '\r\n')
                except KeyError:
                    if self.verbose: self.irc.send('PRIVMSG ' + channel + ' : I don\'t understand the command \'' + message[i][1:] + '\'\r\n')

        return raw_message

    def close(self):
        self.irc.send('QUIT ' + self.nick + ' has better things to do\r\n')
        self.irc.close()

if __name__ == '__main__':
    bot = PyBot('IvoBot', 'irc.eversible.net', ['#cemetech', '#flood'])
    bot.setBots('saxjax')
    bot.setDebug(True)
    bot.setVerbose(False)
    bot.connect()
    bot.loadFactoids('factoids.txt')
    while True:
        try:
            bot.process()
        except KeyboardInterrupt:
            bot.close()
            print
            break
