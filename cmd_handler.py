#! /usr/bin/env python
# encoding: utf-8

"""Usage: ./blackcat 'NICK CHANNEL SENDER MESSAGE'"""

from __future__ import with_statement
from BeautifulSoup import BeautifulSoup
import datetime as dt
import feedparser
import logging
import os
import pickle
import subprocess
import sys
import random
import re
import urllib

DOTFILES = os.path.expanduser('~') + '/.config/blackcat'

DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
FEEDS_FILE = DOTFILES + '/feeds.pickle'
FEEDS_MAX_ENTRIES = 3
LOG_FILE = DOTFILES + '/blackcat.log'
LOG_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
SPOTIFY_FILE = DOTFILES + '/spotify.pickle'

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
            (r'^help$', self.handle_help),
            (r'^(hi||hei|hai|hello|sup)$', self.handle_greeting),
            (r'^(hug|xim)( (?P<what>.*))*$', self.handle_hug),
            (r'^(insult|klette)( (?P<who>.*))*$', self.handle_insult),
            (r'^fortune$', self.handle_fortune),
            (r'^feeds( help)*$', self.feed_help),
            (r'^feeds list$', self.feed_list),
            (r'^feeds add (?P<feed_url>\S+)$', self.feed_add),
            (r'^feeds rm (?P<feed_url>\S+)$', self.feed_rm),
            (r'^whatsnew$', self.feed_whatsnew),
            (r'^spotify( help)*$', self.spotify_help),
            (r'^spotify status$', self.spotify_status),
            (r'^spotify add (?P<spotify_uri>spotify:\S+)$', self.spotify_add),
            (r'^spotify add http://open.spotify.com/(?P<spotify_url>\S+)$',
                self.spotify_add),
            (r'^spotify random$', self.spotify_random),
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
                    self.outn('Error: %(error)s', error=e.message)
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
        response = response % values
        logger.debug('Response: %s', response)
        print response

    def outn(self, response, **additional_values):
        if not self.is_privmsg():
            response = '%(nick)s: ' + response
        self.out(response, **additional_values)

    def is_privmsg(self):
        return self.sender == self.nick

    def handle_unknown(self):
        self.outn('Dunno. Fork http://code.jodal.no/git/?p=blackcat.git '
            + 'and fix it.')

    def handle_help(self):
        self.outn('Use the force, read the source: '
            + 'http://code.jodal.no/git/?p=blackcat.git;a=blob;f=cmd_handler.py;hb=HEAD')

    def handle_greeting(self):
        greetings = (
            'Hi, %(nick)s! How you doing?',
            '%(nick)s: Åssen hengern? Langs venstre kne som vanlig?',
            '%(nick)s: Åssen hengern? Gnur litt mot brystvortene?',
            '%(nick)s: Sup?',
            '%(nick)s: Wazzup? Lixom.',
        )
        self.out(random.choice(greetings))

    def handle_hug(self, what):
        hugs = (
            'klemme',
            'kose',
            'tafse på',
            'våtjokke',
            'kosemozeoverdoze',
            'xoxo',
        )
        hug = random.choice(hugs)
        if what:
            self.out('*%(hug)s %(what)s* ♥', hug=hug, what=what)
        else:
            self.out('*%(hug)s* ♥', hug=hug)

    def handle_insult(self, who):
        insults = (
            'Rævråtne lausunge!',
            'Flatbanka horeunge!',
            'Møkkete trailertøs!',
            'Skitne jødeelsker!',
            'Forbanna sandnigger!',
            'Loppeinfiserte puppehår!',
            'Møkkete tater!',
            'Skinkerytter!',
            'Spermbøtte!',
            'Gen-bunnslam!',
        )
        insult = random.choice(insults)
        if who:
            self.out('%(who)s: %(insult)s', who=who, insult=insult)
        else:
            self.outn(insult)

    def handle_fortune(self):
        with subprocess.Popen(['/usr/games/fortune', '-s'],
                stdout=subprocess.PIPE).stdout as pipe:
            for line in pipe:
                line = line.replace('\n', '').replace('\t', '  ')
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

    def feed_help(self):
        self.outn('Admin: feeds (help|list|add URL|rm URL)')
        self.outn('Usage: whatsnew')

    def feed_list(self):
        feeds = self._feed_load()
        if len(feeds[self.nick]['feeds']) == 0:
            self.outn('You are not watching any feeds')
        else:
            for feed in feeds[self.nick]['feeds']:
                self.outn(feed)

    def feed_add(self, feed_url):
        feeds = self._feed_load()
        if feed_url in feeds[self.nick]['feeds']:
            self.outn("You're already watching that feed")
        else:
            feeds[self.nick]['feeds'].append(feed_url)
            self._feed_save(feeds)
            self.outn('Feed added!')

    def feed_rm(self, feed_url):
        feeds = self._feed_load()
        if feed_url not in feeds[self.nick]['feeds']:
            self.outn("You're not watching that feed")
        else:
            feeds[self.nick]['feeds'].remove(feed_url)
            self._feed_save(feeds)
            self.outn('Feed removed!')

    def feed_whatsnew(self):
        feeds = self._feed_load()
        new_entries = []
        for feed_url in feeds[self.nick]['feeds']:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                updated = dt.datetime(*entry.updated_parsed[:6])
                if updated > feeds[self.nick]['last']:
                    new_entries.append('%(feed)s: %(entry)s <%(url)s>' % {
                        'feed': feed.feed.title,
                        'entry': entry.title,
                        'url': entry.link,
                    })
        if new_entries:
            num_entries = len(new_entries)
            self.outn(
                'Listing %(num_listed)d of %(num_entries)d new',
                num_listed=min(num_entries, FEEDS_MAX_ENTRIES),
                num_entries=num_entries,
            )
            for entry in new_entries[:FEEDS_MAX_ENTRIES]:
                self.outn(entry)
            feeds[self.nick]['last'] = dt.datetime.now()
            self._feed_save(feeds)
        else:
            self.outn('Nothing new')

    def spotify_help(self):
        self.outn('Usage: spotify (help|status|add URL|random)')

    def spotify_status(self):
        url = 'http://www.spotify.com/en/help/service-status/'
        url_handle = urllib.urlopen(url)
        page = BeautifulSoup(url_handle)
        div = page.find('div', id='service-status')
        status = div.h2.contents[0]
        self.outn(status)

    def _spotify_load(self):
        spotify_uris = {}
        if os.path.exists(SPOTIFY_FILE):
            with open(SPOTIFY_FILE, 'rb') as file:
                spotify_uris = pickle.load(file)
        return spotify_uris

    def _spotify_save(self, spotify_uris):
        with open(SPOTIFY_FILE, 'wb') as file:
            pickle.dump(spotify_uris, file)

    def _spotify_url_to_uri(self, spotify_url):
        return 'spotify:%s' % spotify_url.replace(
            'http://open.spotify.com/', '').replace('/', ':')

    def _spotify_uri_to_url(self, spotify_uri):
        return 'http://open.spotify.com/%s' % spotify_uri.replace(
            'spotify:', '').replace(':', '/')

    def spotify_add(self, spotify_uri=None, spotify_url=None):
        assert spotify_uri is not None or spotify_url is not None
        if spotify_uri is None and spotify_url is not None:
            spotify_uri = self._spotify_url_to_uri(spotify_url)
        if not spotify_uri.startswith('spotify:'):
            self.outn('Sorry, that is not a Spotify URI')
            return
        spotify_uris = self._spotify_load()
        if spotify_uri in spotify_uris.keys():
            self.outn('The URL has already been added by %(added_by)s',
                **spotify_uris[spotify_uri])
        else:
            spotify_uris[spotify_uri] = {'added_by': self.nick}
            self._spotify_save(spotify_uris)
            self.outn('URL added!')

    def spotify_random(self):
        spotify_uris = self._spotify_load()
        spotify_uri = random.choice(spotify_uris.keys())
        spotify_url = self._spotify_uri_to_url(spotify_uri)
        self.outn('%(url)s added by %(added_by)s',
            url=spotify_url, **spotify_uris[spotify_uri])

if __name__ == '__main__':
    blackcat = Blackcat()
    if len(sys.argv) == 2:
        blackcat.parse_input(sys.argv[1])
    else:
        sys.exit(__doc__)
