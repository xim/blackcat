# encoding: utf-8

def handle_unknown(cat, command):
    cat.outn('Unknown command "%s"' % command)

handlers = (
    # Prints on all messages. Most likely, you don't want this.
    (r'^!?(?P<command>.\S*)', handle_unknown),
)
