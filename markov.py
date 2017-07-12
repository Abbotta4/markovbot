import pickle,random,sys
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

    speech=''
    while speech!='quit':
        speech=raw_input('>')
        s=random.choice(speech.split())
        response=''
        while True:
            neword=nextword(s)
            response+=' '+neword
            s=neword
            if neword[-1] in ',?!.':
                break
        print response
