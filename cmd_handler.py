#! /usr/bin/env python
# encoding: utf-8

import subprocess
import sys
import pickle
import datetime
import feedparser

class Blackcat(object):
    def __init__(self):
        self.feeds = []
        self.checks = {}

        try:
            _input = open(".irc-feeds", "rb")
            self.feeds = pickle.load(_input)
            _input.close()
            _input = open(".irc-lastcheck", "rb")
            self.checks = pickle.load(_input)
            _input.close()
        except:
            pass

        self.parse_input()
        self.handle_message()

    def parse_input(self):
        if len(sys.argv) < 2:
            sys.exit('Too few arguments (%s)' % sys.argv)
        tokens = sys.argv[1].split(' ')
        if len(tokens) < 4:
            sys.exit('Too few tokens (%s)' % tokens)
        self.nick = tokens[0]
        self.channel = tokens[1]
        self.sender = tokens[2]
        self.command = tokens[3]
        self.message = ' '.join(tokens[3:])



    def handle_message(self):
        # TODO Replace with list of regexps and handlers
        if self.command == 'hi':
            self.handle_hi()
        elif self.command == 'xim':
            self.handle_xim()
        elif self.command == 'fortune':
            self.handle_fortune()
        elif self.command == 'addfeed':
            self.register_feed(self.message)
        elif self.command == 'whatsnew':
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

    def handle_xim(self):
        self.out('*klemme %(nick)s* ♥')

    def handle_fortune(self):
        # TODO Works from command line, but not from IRC
        pipe = subprocess.Popen(['fortune', '-s'],
                stdout=subprocess.PIPE).stdout
        try:
            for line in pipe:
                line = line.replace('\n', '')
                if line.strip():
                    self.out(line)
        except OSError, e:
            self.out(e)
        finally:
            pipe.close()

    def handle_unknown(self):
        self.out(
            self.command
        )

    def register_feed(self, url):
        if url in self.feeds:
            print "I'm allready watching that feed.. thanks though"
            return
        self.feeds.append(url.split(" ")[1])
        out = open(".irc-feeds", "wb")
        pickle.dump(self.feeds, out)
        out.close()
        print "OK, all done!"

    def find_latest(self, nick):
        if nick in self.checks and self.checks[nick]:
            last = self.checks[nick]
        else:
            last = datetime.datetime.now() + datetime.timedelta(days=-1)

        for feed in self.feeds:
            try:
                p = feedparser.parse(feed)
                for entry in p['entries']:
                    u = entry.updated_parsed
                    u = datetime.datetime(u[0],u[1],u[2],u[3],u[4],u[5],u[6])
                    if u > last:
                        print "%s: %s ( %s )" % (p['feed']['title'], entry['title'], entry['link'])
            except IOError:
                print "ERROR: Could not parse feed %s" % feed

        self.checks[nick] = datetime.datetime.now()
        out = open(".irc-lastcheck", "wb")
        pickle.dump(self.checks, out)
        out.close()

if __name__ == '__main__':
    blackcat = Blackcat()
