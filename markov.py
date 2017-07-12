from irc import *
import pickle,random,sys,os
def nextword(a):
    if a in successorlist:
        return random.choice(successorlist[a])
    else:
        return 'the'

def learn(argfile):
    b=open(argfile)
    text=[]
    for line in b:
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

if len(sys.argv)==3 and sys.argv[1]=="-l":
    learn(sys.argv[2])
else:
    a=open('lexicon','rb')
    successorlist=pickle.load(a)
    a.close()

    channel = "#anoo"
    server = "chat.freenode.net"
    nickname = "leebow"

    irc = IRC()
    irc.connect(server, channel, nickname)

    while True:
        text = irc.get_text()
        if text:
            print text
        
        if "PRIVMSG" in text and "Abbott" in text and "hello" in text:        
            speech=text
            s=random.choice(speech.split())
            response=''
            while True:
                neword=nextword(s)
                response+=' '+neword
                s=neword
                if neword[-1] in ',?!.':
                    break
            print response
            irc.send("Abbott", response)
                    
