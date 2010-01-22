#! /usr/bin/env python
# encoding: utf-8

import logging
import os
import re
import sys

from optparse import OptionParser

try:
    import settings
    for variable in ['DOTFILES', 'DATE_TIME_FORMAT', 'LOG_FILE', \
            'APPS', 'LOG_FORMAT']:
        try:
            getattr(settings, variable)
        except AttributeError:
            sys.exit("Please define %s in settings" % variable)
except ImportError:
    sys.exit("Please place settings.py in path, and make sure it doesn't" \
            " cause an ImportError")


class Blackcat(object):

    """Usage: %prog 'NICK CHANNEL SENDER MESSAGE'"""

    def __init__(self, arguments):

        self._create_dotfiles_dir()

        self.logger = logging.getLogger('blackcat')
        if hasattr(settings, 'DEBUG_LEVEL'):
            self._setup_logging(settings.DEBUG_LEVEL)
        else:
            self._setup_logging()

        self.logger.debug("__init__ got arguments ['%s']" % "', '".join(arguments))

        self.nick = arguments[0]
        if arguments[1] == 'null':
            self.channel = None
        else:
            self.channel = arguments[1]
        self.sender = arguments[2]
        self._handle_message(arguments[3])

    def _create_dotfiles_dir(self):
        if not os.path.isdir(settings.DOTFILES):
            os.makedirs(settings.DOTFILES)

    def _setup_logging(self, verbosity_level=20):

        '''Sets up logging, verbosity 0 = OFF, 10 = DEBUG, 50 = CRITICAL'''

        if verbosity_level == 0:
            settings.LOG_FILE = '/dev/null'

        logging.basicConfig(
            level=verbosity_level,
            format=settings.LOG_FORMAT,
            datefmt=settings.DATE_TIME_FORMAT,
            filename=settings.LOG_FILE,
            filemode='a'
        )

        self.logger.debug('Set up logging, verbosity %s' % verbosity_level)

    def _handle_message(self, message):
        self.logger.info('Message: "%s"' % message)
        for app in settings.APPS:
            self.logger.debug('Loading app "%s"' % app)
            app = __import__(app)
            for pattern, handler in app.handlers:
                matches = re.match(pattern, message)
                if matches is not None:
                    self.logger.debug('matched pattern "%s"' % pattern)
                    groups = matches.groupdict()
                    try:
                        handler(self, **groups)
                        return
                    except Exception, e:
                        self.logger.exception(e)
                        self.outn('Error: %(error)s', error=str(e))
                        return

    def out(self, response, **additional_values):

        '''
        Print a response to channel. Usage example:
            additional_values = {
                'user_input': 'Rick Astley',
                'action': 'rules!'
            }
            cat.out('Hi, %(channel)s. %(user_input)s %(action)s', additional_values)
        Given cat joined to channel '#pycat', this makes the bot say:
        Hi, #pycat. Rick Astley rules!
        '''

        values = {
            'nick': self.nick,
            'channel': self.channel,
            'sender': self.sender,
        }
        if additional_values:
            values.update(additional_values)
        response = response % values
        self.logger.info('Response: "%s"', response)
        print response

    def outn(self, response, **additional_values):

        '''
        Prints a message, prepending the sender's username if message is not
        private. See out documentation for detailed usage.
        '''

        self.logger.debug('outn called for response')

        if not self.is_privmsg():
            response = '%(sender)s: ' + response
        self.out(response, **additional_values)

    def is_privmsg(self):

        '''Test whether or not a message is a private message'''

        private = self.sender == self.nick

        self.logger.debug('is_privmsg: %s' % private)

        return private

if __name__ == '__main__':
    arguments = sys.argv[1:]

    if len(arguments) == 4:
        Blackcat(arguments)
    else:
        print Blackcat.__doc__.replace('%prog', sys.argv[0])
