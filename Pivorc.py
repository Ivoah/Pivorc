import socket

class Pivorc:
    def __init__(self, nick, server, channels):
        self.nick = nick
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if len(server) != 2: server = (server, 6667)
        if len(channels) == 1: channels = [channels]
        self.connect(server, channels)

    def connect(self, server, channels):
        self.server.connect(server)
        self.server.send('NICK ' + self.nick + '\r\n')
        self.server.send('USER ' + self.nick + ' 8 * :' + self.nick + '\r\n')
        self.server.send('JOIN ' + ','.join(channels) + '\r\n')

    def close(self):
        self.server.send('QUIT ' + self.nick + ' has better things to do\r\n')
        self.server.close()

if __name__ == '__main__':
    bot = Pivorc('Pivorc', 'irc.freenode.net', '#pico8')
    raw_input('Press enter to quit')
    bot.close()
