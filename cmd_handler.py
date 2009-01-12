#! /usr/bin/env python
# encoding: utf-8

"""Usage: ./blackcat 'NICK CHANNEL SENDER MESSAGE'"""

from __future__ import with_statement
import datetime as dt
import feedparser
import logging
import os
import pickle
import subprocess
import sys

DOTFILES = os.path.expanduser('~') + '/.config/blackcat'
FEEDS_FILE = DOTFILES + '/feeds.pickle'
FEED_USERS_FILE = DOTFILES + '/feed-users.pickle'

LOG_FILE = DOTFILES + '/blackcat.log'
LOG_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

logger = logging.getLogger('blackcat')

class Blackcat(object):
    def __init__(self):
        self.create_dotfiles_dir()
        self.setup_logging()
        self.parse_input()
        self.feed_init()
        self.handle_message()

    def parse_input(self):
        if len(sys.argv) < 2:
            print 'Too few arguments'
            sys.exit(__doc__)
        tokens = sys.argv[1].split(' ')
        if len(tokens) < 4:
            print 'Too few tokens'
            sys.exit(__doc__)
        self.nick = tokens[0]
        self.channel = tokens[1]
        self.sender = tokens[2]
        self.command = tokens[3]
        self.message = ' '.join(tokens[3:])

    def create_dotfiles_dir(self):
        if not os.path.isdir(DOTFILES):
            os.makedirs(DOTFILES)

    def setup_logging(self, verbosity_level=1):
        if verbosity_level == 0:
            level = logging.WARNING
        elif verbosity_level == 2:
            level = logging.DEBUG
        else:
            level = logging.INFO
        logging.basicConfig(
            level=level,
            format=LOG_FORMAT,
            datefmt=DATE_TIME_FORMAT,
            filename=LOG_FILE,
            filemode='a',
        )

    def handle_message(self):
        # TODO Replace with list of regexps and handlers
        try:
            if self.command == 'hi':
                self.handle_hi()
            elif self.command == 'xim':
                self.handle_xim()
            elif self.command == 'fortune':
                self.handle_fortune()
            elif self.command == 'addfeed':
                self.feed_add()
            elif self.command == 'whatsnew':
                self.feed_whatsnew()
            else:
                self.handle_unknown()
        except Exception, e:
            logger.exception(e)
            self.out(e)

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

    def handle_unknown(self):
        self.out(
             '%(nick)s: Dunno. '
             'Fork http://code.jodal.no/git/?p=blackcat.git and fix it.'
        )

    def handle_hi(self):
        self.out('Hi, %(nick)s! How you doing?')

    def handle_xim(self):
        self.out('*klemme %(nick)s* ♥')

    def handle_fortune(self):
        # TODO Works from command line, but not from IRC
        with subprocess.Popen(['fortune', '-s'],
                stdout=subprocess.PIPE).stdout as pipe:
            for line in pipe:
                line = line.replace('\n', '')
                if line.strip():
                    self.out(line)

    def feed_init(self):
        self.feeds = []
        self.checks = {}
        if os.path.exists(FEEDS_FILE):
            with open(FEEDS_FILE, 'rb') as file:
                self.feeds = pickle.load(file)
        if os.path.exists(FEED_USERS_FILE):
            with open(FEED_USERS_FILE, 'rb') as file:
                self.checks = pickle.load(file)

    def feed_add(self):
        url = self.message.split(' ')[1]
        if url in self.feeds:
            self.out("I'm allready watching that feed.")
        else:
            self.feeds.append(url)
            with open(FEEDS_FILE, 'wb') as file:
                pickle.dump(self.feeds, file)
            self.out('OK, feed added!')

    def feed_whatsnew(self):
        anything_new = False
        if self.nick in self.checks and self.checks[self.nick]:
            last = self.checks[self.nick]
        else:
            last = dt.datetime.now() + dt.timedelta(days=-1)
        for feed_url in self.feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    updated = dt.datetime(*entry.updated_parsed[:6])
                    if updated > last:
                        anything_new = True
                        self.out(
                            '%(feed)s: %(entry)s <%(url)s>',
                            feed=feed.feed.title,
                            entry=entry.title,
                            url=entry.link,
                        )
            except IOError:
                self.out('ERROR: Could not parse feed: %(url)s',
                    url=feed_url)
        if anything_new:
            self.checks[self.nick] = dt.datetime.now()
            with open(FEED_USERS_FILE, 'wb') as file:
                pickle.dump(self.checks, file)
        else:
            self.out('%(nick)s: Nothing new.')

if __name__ == '__main__':
    blackcat = Blackcat()
