#!/usr/bin/env python2
import random,sys,socket,re,psycopg2,json,logging
from telegram.ext import Updater,MessageHandler,CommandHandler,Filters,BaseFilter

logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)

# PostgreSQL learn
def learn(argfile, cursor):
    cursor.execute("""SELECT filename FROM logfiles WHERE filename = %s""", (argfile, ))
    if cursor.fetchall():
        print("%s has already been learned", argfile)
        return
    print ("learning %s", argfile)
    b = open(argfile)
    c = r'\[\d\d:\d\d:\d\d\] <.+> '
    for line in b:
        text = []
        s = re.search(c + '.+', line)
        if s is not None:
            line = re.sub(c, '', s.group(0));
            print(line)
            for word in line.split():
                text.append(word)
        # Insert into DB
        for index, word in enumerate(text):
            cursor.execute("""SELECT * FROM markov WHERE word = %s""", (word, ))
            f = cursor.fetchall()
            if not f:
                cursor.execute("""INSERT INTO markov (word, freq, next, total) VALUES ( %s, %s, '{}', 0)""", (word, 1 if index == 0 else 0))
                cursor.execute("""SELECT * FROM markov WHERE word = %s""", (word, ))
                f = cursor.fetchall()
            ff = list(f[0])
            if index is 0: # If the first word, then add to freq
                ff[1] += 1
                cursor.execute("""UPDATE markov SET freq = %s WHERE word = %s""", (ff[1], word))
            j = ff[2]
            if index is len(text) - 1: # If it's the last word, set the next word to NULL
                if not None in j:
                    j[None] = 0
                j[None] += 1
            else: # If it precedes another word
                n = text[index + 1]
                if not n in j:
                    j[n] = 0
                j[n] += 1
            cursor.execute("""UPDATE markov SET next = %s WHERE word = %s""", (json.dumps(j), word))
    cursor.execute("""INSERT INTO logfiles (filename) VALUES (%s)""", (argfile, ))
    conn.commit()
    cursor.close()
    b.close()

def weighted_choice(choices):
    total = sum(choices.values())
    r = random.uniform(0, total)
    upto = 0
    for f in choices.items():
        if upto + f[1] >= r:
            return f[0]
        upto += f[1]
    assert False, "Shouldn't get here. (Is your database empty?)"

# Main
conn_string = "host='localhost' port=5432 dbname='testdb' user='postgres' password='postgres'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
    
if len(sys.argv) == 3 and sys.argv[1] == "-l":
    learn(sys.argv[2], cursor)
    
if len(sys.argv) == 2 and sys.argv[1] == "-t":
    updater = Updater(token = '415135313:AAGEOslKHmSpANt_dUMRKL-SvT4Kkel12Rw')
    dispatcher = updater.dispatcher

    class FilterSabetsu(BaseFilter):
        def filter(self, message):
            return '@Sabetsu' in message.text
    filter_sabetsu = FilterSabetsu()
    
    def respond(bot, update):
        cursor.execute("""SELECT word, freq FROM markov WHERE freq > 0""")
        r = weighted_choice(dict((k[0], k[1]) for k in cursor.fetchall()))
        response = r
        while True:
            cursor.execute("""SELECT next FROM markov WHERE word = %s""", (r, ))
            r = weighted_choice(cursor.fetchall()[0][0])
            if str(r) == 'null':
                break
            else:
                r = str(r)
                response += ' ' + r
        print(response)
        bot.send_message(chat_id = update.message.chat_id, text = response)

    markov_handler = MessageHandler(filter_sabetsu, respond)
    dispatcher.add_handler(markov_handler)

    updater.start_polling()
    updater.idle()

if len(sys.argv)==2 and sys.argv[1] == "-n":
    cursor.execute("""SELECT word, freq FROM markov WHERE freq > 0""")
    r = weighted_choice(dict((k[0], k[1]) for k in cursor.fetchall()))
    response = r
    while True:
        cursor.execute("""SELECT next FROM markov WHERE word = %s""", (r, ))
        r = weighted_choice(cursor.fetchall()[0][0])
        if str(r) == 'null':
            break
        else:
            r = str(r)
            response += ' ' + r
    print(response)
            
else:
    print('USAGE: python markov.py [OPTION] [ARGUMENT]\n\nOptions:\n-l: learn a file\n-t: telegram\n-i: irc')

conn.close()
