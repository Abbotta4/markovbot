#!/usr/bin/python
import pickle,random,sys,socket,re

# Markov Chain methods
def learn(argfile):
    b=open(argfile)
    c = r'\[\d\d:\d\d:\d\d\] <.+> '
    text=[]
    for line in b:
        s = re.search(c + '.+', line)
        if s is not None:
            line = re.sub(c, '', s.group(0));
            for word in line.split():
                text.append (word)
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
