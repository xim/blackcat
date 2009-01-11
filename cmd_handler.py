#! /usr/bin/env python

import sys
import pickle
import datetime

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

        feeds = []
        checks = {}
        try:
            input = open(".irc-feeds", "rb")
            feeds = pickle.load(input)
            input.close()
            input = open(".irc-lastcheck", "rb")
            checks = pickle.load(input)
            input.close()
        except IOError:
            print "A virgin feeder?"

        self.handle_message()

    def handle_message(self):
        # TODO Replace with list of regexps and handlers
        if self.command == 'hi':
            self.handle_hi()
        elif self.command == 'addfeed':
            register_feed(rest)
        elif self.command == 'whatsnew?':
            find_latest(nick)
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

    def register_feed(url):
        if url in feeds:
            print "I'm allready watching that feed.. thanks though"
            return
        feeds.append(url)
        out = open(".irc-feeds", "rb")
        pickle.dump(feeds, out)
        out.close()
        print "OK, all done!"

    def find_latest(nick):
        import feedparser
        if nick in checks and checks[nick]:
            last = checks[nick]
        else:
            checks[nick] = datetime.datetime.now().timetuple()
            last = checks[nick]

        for feed in feeds:
            try:
                p = feedparser.parse(feed)
                for entry in p['entries']
                    if entry.updated_parsed > last:
                        print "%s: %s ( %s )" % (feed['title'], entry['title'], entry['link'])
            except, e:
                print "ERROR: Could not parse feed %s" % feed

        out = open(".irc-lastcheck", "rb")
        pickle.dump(checks, out)
        out.close()

if __name__ == '__main__':
    blackcat = Blackcat()
