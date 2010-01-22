# encoding: utf-8

import random

def handle_help(cat):
    cat.outn("Read the source: http://github.com/xim/blackcat/ =)")

def handle_greeting(cat):
    greetings = (
        'Hi, %(sender)s! How you doing?',
        'Greetings, %(sender)s! How you doing?',
        '%(sender)s: Sup?'
    )
    cat.out(random.choice(greetings))

def handle_hug(cat, what):
    hugs = (
        'hug',
        'xoxo',
    )
    hug = random.choice(hugs)
    if what:
        cat.out('*%(hug)s %(what)s* ♥', hug=hug, what=what)
    else:
        cat.out('*%(hug)s* ♥', hug=hug)

handlers = (
    ('^!help$', handle_help),
    ('^!(|hi|hei|hai|hello|sup)$', handle_greeting),
    ('^!hug( (?P<what>.*))?$', handle_hug),
)
