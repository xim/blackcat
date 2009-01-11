#! /usr/bin/env python

import sys
import pickle
import datetime
import feedparser

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

        self.feeds = []
        self.checks = {}
        try:
            _input = open(".irc-feeds", "rb")
            self.feeds = pickle.load(_input)
            _input.close()
            _input = open(".irc-lastcheck", "rb")
            self.checks = pickle.load(_input)
            _input.close()
        except IOError:
            print "A virgin feeder?"

        self.handle_message()

    def handle_message(self):
        # TODO Replace with list of regexps and handlers
        if self.command == 'hi':
            self.handle_hi()
        elif self.command == 'addfeed':
            self.register_feed(self.message)
        elif self.command == 'whatsnew?':
            self.find_latest(self.nick)
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

    def handle_unknown(self):
        self.out(
            '%(nick)s: Dunno. '
            'Fork http://code.jodal.no/git/?p=blackcat.git and fix it.'
        )

    def register_feed(self, url):
        if url in self.feeds:
            print "I'm allready watching that feed.. thanks though"
            return
        self.feeds.append(url)
        out = open(".irc-feeds", "rb")
        pickle.dump(self.feeds, out)
        out.close()
        print "OK, all done!"

    def find_latest(self, nick):
        if nick in self.checks and self.checks[nick]:
            last = self.checks[nick]
        else:
            self.checks[nick] = datetime.datetime.now().timetuple()
            last = self.checks[nick]

        for feed in self.feeds:
            try:
                p = feedparser.parse(feed)
                for entry in p['entries']:
                    if entry.updated_parsed > last:
                        print "%s: %s ( %s )" % (feed['title'], entry['title'], entry['link'])
            except:
                print "ERROR: Could not parse feed %s" % feed

        out = open(".irc-lastcheck", "rb")
        pickle.dump(self.checks, out)
        out.close()

if __name__ == '__main__':
    blackcat = Blackcat()
