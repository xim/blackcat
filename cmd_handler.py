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
import re

DOTFILES = os.path.expanduser('~') + '/.config/blackcat'
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
FEEDS_FILE = DOTFILES + '/feeds.pickle'
FEEDS_MAX_ENTRIES = 3
LOG_FILE = DOTFILES + '/blackcat.log'
LOG_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'

logger = logging.getLogger('blackcat')

class Blackcat(object):
    def __init__(self):
        self.create_dotfiles_dir()
        self.setup_logging(2)

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

    def parse_input(self, input):
        logger.debug('Request: %s', input)
        pattern = r'^(?P<nick>\S+)\s(?P<channel>\S+)\s(?P<sender>\S+)\s' \
            + r'(?P<request>.+)$'
        matches = re.match(pattern, input)
        if matches is not None:
            groups = matches.groupdict()
            self.nick = groups['nick']
            if groups['channel'] == 'null':
                self.channel = None
            else:
                self.channel = groups['channel']
            self.sender = groups['sender']
            self.handle_request(groups['request'])
        else:
            sys.exit(__doc__)

    def handle_request(self, request):
        handlers = (
            (r'^hi$', self.handle_hi),
            (r'^xim$', self.handle_xim),
            (r'^fortune$', self.handle_fortune),
            (r'^addfeed (?P<feed_url>\S+)$', self.feed_add),
            (r'^whatsnew$', self.feed_whatsnew),
            (r'^.*$', self.handle_unknown),
        )
        for pattern, handler in handlers:
            matches = re.match(pattern, request)
            if matches is not None:
                groups = matches.groupdict()
                try:
                    handler(**groups)
                except Exception, e:
                    logger.exception(e)
                    self.out('%(nick)s: Error: %(error)s', error=e.message)
                finally:
                    break

    def out(self, response, **additional_values):
        values = {
            'nick': self.nick,
            'channel': self.channel,
            'sender': self.sender,
        }
        if additional_values:
            values.update(additional_values)
        if not self.is_privmsg():
            response = '%(nick)s: ' + response
        response = response % values
        logger.debug('Response: %s', response)
        print response

    def is_privmsg(self):
        return self.sender == self.nick

    def handle_unknown(self):
        self.out('Dunno. Fork http://code.jodal.no/git/?p=blackcat.git '
            + 'and fix it.')

    def handle_hi(self):
        self.out('Hi, %(nick)s! How you doing?')

    def handle_xim(self):
        self.out('*klemme* ♥')

    def handle_fortune(self):
        # FIXME Works from command line, but not from IRC
        with subprocess.Popen(['fortune', '-s'],
                stdout=subprocess.PIPE).stdout as pipe:
            for line in pipe:
                line = line.replace('\n', '')
                if line.strip():
                    self.out(line)

    def _feed_load(self):
        feeds = {}
        if os.path.exists(FEEDS_FILE):
            with open(FEEDS_FILE, 'rb') as file:
                feeds = pickle.load(file)
        if self.nick not in feeds:
            feeds[self.nick] = {
                'last': dt.datetime.now() - dt.timedelta(days=1),
                'feeds': [],
            }
        return feeds

    def _feed_save(self, feeds):
        with open(FEEDS_FILE, 'wb') as file:
            pickle.dump(feeds, file)

    def feed_add(self, feed_url):
        feeds = self._feed_load()
        if feed_url in feeds[self.nick]['feeds']:
            self.out("You're already watching that feed.")
        else:
            feeds[self.nick]['feeds'].append(feed_url)
            self._feed_save(feeds)
            self.out('Feed added!')

    def feed_whatsnew(self):
        feeds = self._feed_load()
        new_entries = []
        for feed_url in feeds[self.nick]['feeds']:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                updated = dt.datetime(*entry.updated_parsed[:6])
                if updated > feeds[self.nick]['last']:
                    new_entries.append(entry)
        if new_entries:
            self.out(
                '%(num_entries)d new, listing %(num_listed)d',
                num_entries=len(new_entries),
                num_listed=min(len(new_entries), FEEDS_MAX_ENTRIES),
            )
            for entry in new_entries[:FEEDS_MAX_ENTRIES]:
                self.out(
                    '%(feed)s: %(entry)s <%(url)s>',
                    feed=feed.feed.title,
                    entry=entry.title,
                    url=entry.link,
                )
            feeds[self.nick]['last'] = dt.datetime.now()
            self._feed_save(feeds)
        else:
            self.out('Nothing new')

if __name__ == '__main__':
    blackcat = Blackcat()
    if len(sys.argv) == 2:
        blackcat.parse_input(sys.argv[1])
    else:
        sys.exit(__doc__)
