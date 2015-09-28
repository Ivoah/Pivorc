import socket, json

class PyBot:
    def __init__(self, conf):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.factoids = {}
        self.conf = json.load(open(conf))
        self.loadFactoids(self.conf['factoids'])

    def connect(self):
        self.irc.connect(tuple(self.conf['server']))
        self.irc.send('NICK ' + self.conf['name'] + '\r\n')
        self.irc.send('USER ' + self.conf['name'] + ' 8 * :' + self.conf['name'] + '\r\n')
        while True:
            data = self.irc.recv(512)
            if self.conf['debug']: print data
            if '/MOTD' in data: break
        self.irc.send('JOIN ' + ','.join(self.conf['channels']) + '\r\n')

    def loadFactoids(self, filename):
        self.filename = filename
        factoids = open(self.filename)
        for factoid in factoids:
            text = '|'.join(factoid.split('|')[1:])
            text = text.replace('<action> ', '\x01ACTION ').replace('<action>', '\x01ACTION ').replace('<reply> ', '').replace('<reply>', '')
            self.factoids[factoid.split('|')[0].lower()] = text

    def process(self):
        try:
            self.irc.setblocking(False)
            raw_message = self.irc.recv(512)
            self.irc.setblocking(True)
        except socket.error:
            return ''

        if self.conf['debug']: print(raw_message)
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
            if nick in self.conf['bots']: i = 1
            else: i = 0
            if message[i][0] == '~':
                if channel == self.conf['name']: channel = nick
                try:
                    if self.conf['debug']: print('PRIVMSG ' + channel + ' :' + self.factoids[message[i][1:].lower()].replace('$nick', nick) + '\r\n')
                    self.irc.send('PRIVMSG ' + channel + ' :' + self.factoids[message[i][1:].lower()].replace('$nick', nick) + '\r\n')
                except KeyError:
                    if self.conf['verbose']: self.irc.send('PRIVMSG ' + channel + ' : I don\'t understand the command \'' + message[i][1:] + '\'\r\n')

        return raw_message

    def disconnect(self):
        self.irc.send('QUIT :' + self.conf['name'] + ' has better things to do\r\n')
        self.irc.close()

if __name__ == '__main__':
    bot = PyBot('config.json')
    bot.connect()
    while True:
        try:
            bot.process()
        except KeyboardInterrupt:
            bot.disconnect()
            print
            break
