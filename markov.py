#!/usr/bin/env python2
import random,sys,socket,re,psycopg2,json

# PostgreSQL learn
def learn(argfile, conn):
    cursor = conn.cursor()
    cursor.execute("""SELECT filename FROM logfiles WHERE filename = %s""", (argfile, ))
    if cursor.fetchall():
        print "%s has already been learned" % argfile
        return
    print "learning %s" % argfile
    b=open(argfile)
    c = r'\[\d\d:\d\d:\d\d\] <.+> '
    for line in b:
        text = []
        s = re.search(c + '.+', line)
        if s is not None:
            line = re.sub(c, '', s.group(0));
            print line
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
        
# IRC methods
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
def send(chan, msg):
    irc.send("PRIVMSG " + chan + " :" + msg + "\n")
        
def connect(server, channel, botnick):
    #defines the socket
    print "connecting to: " + server
    irc.connect((server, 6667)) #connects to the server
    irc.send("USER " + botnick + " " + botnick + " " + botnick + " :This is a fun bot!\n") #user authentication
    irc.send("NICK " + botnick + "\n")
    irc.send("JOIN " + channel + "\n") #join the chan
    
def get_text():
    text=irc.recv(2048)  #receive the text
    if text.find('PING') != -1:
        irc.send('PONG ' + text.split() [1] + '\n')
    return text

# Main
conn_string = "host='localhost' port=5432 dbname='testdb' user='postgres' password='postgres'"
conn = psycopg2.connect(conn_string)
    
if len(sys.argv)==3 and sys.argv[1]=="-l":
    learn(sys.argv[2], conn)
else:
    cursor = conn.cursor()
    ''' for local testing
    channel = "#anoo"
    server = "chat.freenode.net"
    nickname = "leebow"

    connect(server, channel, nickname)

    text = "";
    while text != ":Abbott!~Abbott@unaffiliated/abbott PRIVMSG leebow :go away\r\n":
        text = get_text()
        if text:
            print text
        
        if "PRIVMSG" in text and "Abbott" in text:
    ''' #for local testing
    cursor.execute("""SELECT word, freq FROM markov WHERE freq > 0""")
    r = weighted_choice(dict((k[0], k[1]) for k in cursor.fetchall()))
    response = r
    while True:
        cursor.execute("""SELECT next FROM markov WHERE word = %s""", (r, ))
        r = weighted_choice(cursor.fetchall()[0][0])
        if str(r) == 'null':
            #if r == None:
            break
        else:
            r = str(r)
            response += ' ' + r
    print response
    #send("Abbott", response) #comment for local testing
    conn.close()
