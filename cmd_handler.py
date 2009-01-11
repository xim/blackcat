#! /usr/bin/env python
# encoding: utf-8

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
        if self.command == 'xim':
            self.handle_xim()
        else:
            self.handle_unknown()

    def out(self, text, **additional_values):
        values = {
            'nick': self.nick,
            'channel': self.channel,
            'sender': self.sender,
            'command': self.command,
            'message': self.message,
        }
        if additional_values:
            values.update(additional_values)
        print text % values

    def handle_hi(self):
        self.out('Hi, %(nick)s! How you doing?')

    def handle_xim(self):
        self.out('*klemme %(nick)s* ♥')

    def handle_unknown(self):
        self.out(
            '%(nick)s: Dunno. '
            'Fork http://code.jodal.no/git/?p=blackcat.git and fix it.'
        )

if __name__ == '__main__':
    blackcat = Blackcat()
