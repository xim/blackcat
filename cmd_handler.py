#! /usr/bin/env python

import sys
import pickle
import datetime

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

    if first == 'hi':
        print 'Hi, %s! How you doing?' % nick
    else if first == 'addfeed':
        register_feed(rest)
    else if first == 'whatsnew?':
        find_latest(nick)
    else:
        print '%s: Dunno. Fork http://code.jodal.no/git/?p=blackcat.git and fix it.' % nick

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
    main()
