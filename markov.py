#!/usr/bin/python
import pickle,random,sys,socket,re,psycopg2,json

# Pickle learn
def learn(argfile):
    b=open(argfile)
    c = r'\[\d\d:\d\d:\d\d\] <.+> '
    text=[]
    for line in b:
        s = re.search(c + '.+', line)
        if s is not None:
            line = re.sub(c, '', s.group(0));
            for word in line.split():
                text.append(word)
    b.close()
    textset=list(set(text))
    follow={}
    for l in range(len(textset)):
        working=[]
        check=textset[l]
        for w in range(len(text)-1):
            if check==text[w] and text[w][-1] not in '(),.?!':
                working.append(str(text[w+1]))
        follow[check]=working
    a=open('lexicon','wb')
    pickle.dump(follow,a,2)
    a.close()

# PostgreSQL learn
def learn2(argfile, conn):
    cursor = conn.cursor()
    b=open(argfile)
    c = r'\[\d\d:\d\d:\d\d\] <.+> '
    for line in b:
        text = []
        s = re.search(c + '.+', line)
        if s is not None:
            line = re.sub(c, '', s.group(0));
            for word in line.split():
                text.append(word)
        # Insert into DB
        for index, word in enumerate(text):
            print word + ' ' + str(len(text))
            cursor.execute("""SELECT * FROM markov WHERE word = %s""", (word, ))
            f = cursor.fetchall()
            if not f:
                cursor.execute("""INSERT INTO markov (word, freq, next, total) VALUES ( %s, 0, '{}', 0)""", (word, ))
                cursor.execute("""SELECT * FROM markov WHERE word = %s""", (word, ))
                f = cursor.fetchall()
            print f
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
if len(sys.argv)==3 and sys.argv[1]=="-l":
    learn(sys.argv[2])
else:
    '''
    #Define our connection string
    conn_string = "host='localhost' dbname='testdb' user='postgres' password='postgres'"
    # print the connection string we will use to connect
    print "Connecting to database\n->%s" % (conn_string)
    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)
    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    #cursor = conn.cursor()
    #print "Connected!\n"
    '''
    
    a=open('lexicon','rb')
    successorlist=pickle.load(a)
    a.close()

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
            speech=text
            s=random.choice(speech.split())
            response=''
            while True:
                #neword=nextword(s)
                if s in successorlist and successorlist[s]:
                    neword = random.choice(successorlist[s])
                else:
                    neword = ':^)'

                response+=neword
                s=neword
                if neword[-1] in ',?!.)':
                    break
                else:
                    response+=' '
            print response
            send("Abbott", response)
