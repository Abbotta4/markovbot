# Markov chain bot

    USAGE: python markov.py [OPTION] ([FILE])

    Options:
    -l: Learn a file. Takes one argument FILE to learn.
    -t: Starts the Telegram bot configured in config.ini
    -n: Sends the output chain to stdout

`markovbot.py` will build a PostgreSQL database of words and words that are most likely to follow after it to construct [Markov chains](https://en.wikipedia.org/wiki/Markov_chain) used to simulate language. Currently a telegram bot configuration and outputting to `stdout` are supported methods of generating chains.

This program depends on the following python2 modules

    python-telegram-bot
    psycopg2