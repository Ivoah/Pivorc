import socket

class PyBot:
    def __init__(self, nick, server, channels):
        self.nick = nick
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if len(server) != 2: server = (server, 6667)
        if isinstance(channels, basestring): channels = [channels]
        self.connect(server, channels)

    def connect(self, server, channels):
        self.server.connect(server)
        self.server.send('NICK ' + self.nick + '\r\n')
        self.server.send('USER ' + self.nick + ' 8 * :' + self.nick + '\r\n')
        self.server.send('JOIN ' + ','.join(channels) + '\r\n')

    def process(self):
        try:
            self.server.setblocking(False)
            message = self.server.recv(512)
            self.server.setblocking(True)
        except socket.error:
            return
        print(message)

    def close(self):
        self.server.send('QUIT ' + self.nick + ' has better things to do\r\n')
        self.server.close()

if __name__ == '__main__':
    bot = PyBot('IvoBot', 'irc.freenode.net', '#pico8')
    while True:
        try:
            bot.process()
        except KeyboardInterrupt:
            bot.close()
            break
