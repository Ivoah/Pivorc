import socket

class PyBot:
    def __init__(self, nick, server, channels):
        self.nick = nick
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.debug = False
        self.dict = {}
        if len(server) != 2: server = (server, 6667) #If we don't have a port number, use 6667
        if isinstance(channels, basestring): channels = [channels] #If we only have one channel, then make it a list for self.connect
        self.connect(server, channels) #Connect to the server

    def connect(self, server, channels):
        self.server.connect(server)
        self.server.send('NICK ' + self.nick + '\r\n') #Set nickname
        self.server.send('USER ' + self.nick + ' 8 * :' + self.nick + '\r\n') #Set username
        self.server.send('JOIN ' + ','.join(channels) + '\r\n') #Join channels

    def setDebug(self, debug):
        self.debug = debug

    def loadFactoids(self, filename):
        self.filename = filename
        factoids = open(self.filename)
        for factoid in factoids:
            text = '|'.join(factoid.split('|')[1:])
            text = text.replace('<action> ', '\x01ACTION ').replace('<action>', '\x01ACTION ').replace('<reply> ', '').replace('<reply>', '')
            self.dict[factoid.split('|')[0].lower()] = text

    def process(self):
        try:
            self.server.setblocking(False)
            message = self.server.recv(512)
            self.server.setblocking(True)
        except socket.error:
            return

        if self.debug: print(message)
        if message[0] == ':':
            nick = message.split('!')[0][1:]
            message = message.split()[1:]
        else:
            nick = None
            message = message.split()
        command = message[0]
        message = message[1:]

        if command == 'PING':
            self.server.send('PONG ' + message + '\r\n')
        elif command == 'PRIVMSG':
            channel = message[0]
            message = message[1:]
            message[0] = message[0][1:]
            if message[0][0] == '~':
                try:
                    if self.debug: print('PRIVMSG ' + channel + ' :' + self.dict[message[0][1:].lower()].replace('$nick', nick) + '\r\n')
                    self.server.send('PRIVMSG ' + channel + ' :' + self.dict[message[0][1:].lower()].replace('$nick', nick) + '\r\n')
                except KeyError:
                    self.server.send('PRIVMSG ' + channel + ' : I don\'t understand \'' + message[0] + '\'\r\n')

    def close(self):
        self.server.send('QUIT ' + self.nick + ' has better things to do\r\n')
        self.server.close()

if __name__ == '__main__':
    bot = PyBot('IvoBot', 'irc.freenode.net', '#pico8')
    bot.setDebug(True)
    bot.loadFactoids('factoids.txt')
    while True:
        try:
            bot.process()
        except KeyboardInterrupt:
            bot.close()
            print
            break
