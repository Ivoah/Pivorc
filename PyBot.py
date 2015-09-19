import socket

class PyBot:
    def __init__(self, nick, server, channels, debug = False):
        self.nick = nick
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.debug = debug
        if len(server) != 2: server = (server, 6667) #If we don't have a port number, use 6667
        if isinstance(channels, basestring): channels = [channels] #If we only have one channel, then make it a list for self.connect
        self.connect(server, channels) #Connect to the server

        #self.dict = {'pico-8': 'PICO-8 is a fantasy console for making, sharing and playing tiny games and other computer programs. When you turn it on, the machine greets you with a shell for typing in Lua commands and provides simple built-in tools for creating your own cartridges.',
        #             'BBS': 'http://www.lexaloffle.com/bbs/?cat=7'}
        factoids = open('factoids.txt')
        self.dict = {}
        for factoid in factoids:
            text = '|'.join(factoid.split('|')[1:])
            text = text.replace('$name', self.nick).replace('<action> ', '\x01ACTION ').replace('<action>', '\x01ACTION ').replace('<reply> ', '').replace('<reply>', '')
            self.dict[factoid.split('|')[0]] = text

    def connect(self, server, channels):
        self.server.connect(server)
        self.server.send('NICK ' + self.nick + '\r\n') #Set nickname
        self.server.send('USER ' + self.nick + ' 8 * :' + self.nick + '\r\n') #Set username
        self.server.send('JOIN ' + ','.join(channels) + '\r\n') #Join channels

    def process(self):
        try:
            self.server.setblocking(False)
            message = self.server.recv(512)
            self.server.setblocking(True)
        except socket.error:
            return

        if self.debug: print(message)
        if message[0] == ':': message = message.split()[1:]
        else: message = message.split()
        command = message[0]
        message = ' '.join(message[1:])

        if command == 'PING':
            self.server.send('PONG ' + message + '\r\n')
        elif command == 'PRIVMSG':
            channel = message.split()[0]
            message = ' '.join(message.split()[1:])[1:]
            if message[0] == '~':
                try:
                    if self.debug: print('PRIVMSG ' + channel + ' :' + self.dict[message.split()[0][1:]] + '\r\n')
                    self.server.send('PRIVMSG ' + channel + ' :' + self.dict[message.split()[0][1:]] + '\r\n')
                except KeyError:
                    self.server.send('PRIVMSG ' + channel + ' : I don\'t understand \'' + message.split()[0] + '\'\r\n')

    def close(self):
        self.server.send('QUIT ' + self.nick + ' has better things to do\r\n')
        self.server.close()

if __name__ == '__main__':
    bot = PyBot('IvoBot', 'irc.freenode.net', '#pico8', True)
    while True:
        try:
            bot.process()
        except KeyboardInterrupt:
            bot.close()
            print()
            break
