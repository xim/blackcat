#! /usr/bin/env python

import sys

def main():
    if len(sys.argv) < 2:
        print 'Too few arguments: %s' % sys.argv

    input = sys.argv[1]
    tokens = input.split(' ')
    nick = tokens[0]
    channel = tokens[1]
    sender = tokens[2]
    first = tokens[3]
    rest = ' '.join(tokens[4:])

    if first == 'hi':
        print 'Hi, %s! How you doing?' % nick
    else:
        print '%s: Dunno. Fork http://code.jodal.no/git/?p=blackcat.git and fix it.' % nick

if __name__ == '__main__':
    main()
