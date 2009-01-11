#! /usr/bin/env python

import sys

class Blackcat(object):
    def __init__(self):
        if len(sys.argv) < 2:
            sys.exit('Too few arguments')

        tokens = sys.argv[1].split(' ')
        self.nick = tokens[0]
        self.channel = tokens[1]
        self.sender = tokens[2]
        self.command = tokens[3]
        self.message = ' '.join(tokens[3:])

        self.handle_message()

    def handle_message(self):
        # TODO Replace with list of regexps and handlers
        if self.command == 'hi':
            self.handle_hi()
        else:
            self.handle_unknown()

    def out(self, text):
        # TODO Add nick, channel, etc. automatically
        print text

    def handle_hi(self):
        self.out('Hi, %s! How you doing?' % self.nick)

    def handle_unknown(self):
        self.out('%s: Dunno. Fork http://code.jodal.no/git/?p=blackcat.git and fix it.' % self.nick)

if __name__ == '__main__':
    blackcat = Blackcat()
