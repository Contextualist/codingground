# -*- coding: utf-8 -*-  
'''
CAUTION: Make sure there is only ONE doc in the AHA BC folder,
         otherwise the doc catcher may catch a wrong one.
NOTICE:  To update the broadcast structure, you need to update
         1) KeyWord, 2) BWeight, 3) PNperB;
         To update the host list, you need to update
         1) Host.

Main idea: 
  i. group sections into portions
  ii. then distribute the portions to each host, so that
      a. the STD of hosts' word counts is minimized
      b. the continuity is maximized

B_   block(column)
S_   section(paragraph)
P_   portion(read by a host)
_N   number, count

For those who are new to python, remember, 
1. The index of a python list starts with 0.
2. Variables in Python are pointers. So to copy a list but not the address of the list, use a=copy.deepcopy(b), instead of a=b.

Progress: Hope to improve efficiency of DISTRIBUTE
'''

import quip

'''
====================DOC CATCHER====================
'''
'''
client = quip.QuipClient(access_token="Wk9EQU1BcDZFS04=|1483091850|CF037JVoITJPnAET8aHWnZwEZACvrIm7jtkRIQCaX3g=")
AHA_BC = client.get_folder("PCeAOAQx6sO") # folder AHA BC
for td in AHA_BC['children'] :
    if 'thread_id' in td :
        theID = td['thread_id'] #find a doc
        break
thread = client.get_thread(id=theID)
'''
client = quip.QuipClient(access_token="Wk9EQU1BcDZFS04=|1483091850|CF037JVoITJPnAET8aHWnZwEZACvrIm7jtkRIQCaX3g=")
theID = "Z0R5AhbLjUxu" # test doc 0309-c
thread = client.get_thread(id=theID)
'''
====================DOC PRE-PROCESSOR====================
extract SWordCount and SID
'''
from HTMLParser import HTMLParser
import re

html = thread["html"].decode('utf-8').encode('ascii', 'ignore') #clear all non-ascii
html = re.sub(r'<h1.+<\/h1>', '', html, count=1) #delete the header
'''SET'''
KeyWord = ("Good Morning AHA",
            "Now for this week in history",
            "In World News",
            "Now for the fun facts",
            "In AHA News")
BN = len(KeyWord)

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__BNNow = -1
        self.__SNNow = 0
        self.__newline = 0 #when there are total two <p> and <br />, new section
        self.__SIDNow = ''
        self.SWordCount = []
        self.SID = []

    def handle_starttag(self, tag, attrs):
        if tag == "p" :
            self.__SIDNow = attrs[0][1] #extract the ID attr
            self.__newline += 1

    def handle_startendtag(self, tag, attrs):
        if tag == "br" :
            self.__newline += 1

    def handle_data(self, data):
        wordcount = len(re.findall(r"\b\w+\b", data))
        if wordcount == 0 : return 0
        if (self.__BNNow+1<=BN-1 and data.find(KeyWord[self.__BNNow+1])!=-1) :
            self.__BNNow += 1 #new block
            self.__SNNow = 0
            self.SWordCount += [[0]]
            self.SID += [[self.__SIDNow]]
            self.__IgnoreNextp = True
        elif self.__newline>=2 :
            self.__SNNow += 1 #new section
            self.SWordCount[self.__BNNow] += [0]
            self.SID[self.__BNNow] += [self.__SIDNow]
        self.SWordCount[self.__BNNow][self.__SNNow] += wordcount
        self.__newline = 0

parser = MyHTMLParser()
parser.feed(html)

SWordCount = parser.SWordCount
SID = parser.SID

'''
====================SETTINGS====================
'''
import random

'''SET'''
Host = ["Edward", "Katherine", "Sissy", "Harry"]
random.shuffle(Host)
HostN = len(Host)
HostWordCount = [0.00] * HostN

#                  Greet   History   World  Fun   AHA
'''SET'''
BWeight = (1.00,   1.30,    1.50,  1.20, 1.00)  # B[]
SNperB = [ len(b) for b in SWordCount ]     # B[SN]
for b in xrange(BN) :
    for s in xrange(SNperB[b]) :
        SWordCount[b][s] *= BWeight[b]      # B[S[]]

'''SET'''
PNperB =  (   1,      1,       2,     1,    3)  # B[PN]
CutSign = [ [0]*pn for pn in PNperB ]
PWordCount = [ [0]*pn for pn in PNperB ]
PAssign = [ [0]*pn for pn in PNperB ]
IsBetterPDivision = 0
#Continuity = 0
for i in xrange(BN) :
    if PNperB[i] > SNperB[i] : PNperB[i] = SNperB[i]
Ans_CutSign = []
Ans_PAssign = []
#Ans_Continuity = 0
Ans_HostWordCountSTD = 1000.00
CutSign[0][0] = 0
'''
====================DISTRIBUTE(S->P)====================
'''
import copy

def std(d):
    m = 0.00
    for x in d : m += x
    m = m / len(d)
    s = 0.00
    for x in d : s += ( x - m ) ** 2
    return (s / len(d)) ** 0.5

def AssignP(b, p) :
    global HostN, PAssign, BN, PNperB, PWordCount, HostWordCount
    global Ans_PAssign, IsBetterPDivision, Ans_HostWordCountSTD, AnsC
    op = range(HostN)
    if p == 0 : #forbid the host to cross a block
        op = range(PAssign[b-1][PNperB[b-1]-1])+range(PAssign[b-1][PNperB[b-1]-1]+1,HostN)
    for i in op:
        PAssign[b][p] = i
        HostWordCount[i] += PWordCount[b][p]
        #if (p!=0)&&(i!=PAssign[b][p-1]) : Continuity += 1
        if p == PNperB[b]-1 :
            if b == BN-1 :
                t = std(HostWordCount)
                if t < Ans_HostWordCountSTD :
                    Ans_HostWordCountSTD = t
                    Ans_PAssign = copy.deepcopy(PAssign)
                    IsBetterPDivision = 1
            else :
                AssignP(b+1,0)
        else :
            AssignP(b,p+1)
        HostWordCount[i] -= PWordCount[b][p]

def GenerateP(b, p) : #block 'b' from 'CutSign[b,p]+1' to the end start dividing the 'p'th sections
    global PNperB, SNoerB, BN, CutSign, PWordCount, SWordCount, HostWordCount, HostN, PAssign
    global IsBetterPDivision, Ans_CutSign
    if p == PNperB[b]-1 :
        PWordCount[b][PNperB[b]-1] = sum(SWordCount[b][CutSign[b][p]:])
        if b < BN-1 :
            CutSign[b+1][0] = 0
            GenerateP(b+1,0)   #next B
        else :
            IsBetterPDivision = 0
            HostWordCount = [0] * HostN
            PAssign[0][0] = 0
            HostWordCount[0] += PWordCount[0][0]
            if PNperB[0]>1 :
                AssignP(0, 1)
            else : 
                AssignP(1, 0) #start assigning hosts
            if IsBetterPDivision : 
                Ans_CutSign = copy.deepcopy(CutSign)
    else :
        PWordCount[b][p] = 0
        for i in xrange(CutSign[b][p]+1,SNperB[b]) :
            PWordCount[b][p] += SWordCount[b][i-1]
            CutSign[b][p+1] = i
            GenerateP(b,p+1)


GenerateP(0, 0)
#    CutSign =   [[0],   [0],     [],       , []] # B[P[SN]] generated first
#    PWordCount =[ ,      ,   [],       , []] # B[P[]] generated first
#        PAssign =   [[0],   [1],     [],       , []] # B[P[Host]] subsequent

'''
====================POST DIVISIONS====================
'''
for b in xrange(BN) :
    for p in xrange(PNperB[b]) :
        print Ans_PAssign[b][p], Ans_CutSign[b][p], SID[b][Ans_CutSign[b][p]]
        '''
        client.edit_document(thread_id=theID.decode('utf-8').encode('ascii'), content=r"_//%s_<br/>" % (Host[Ans_PAssign[b][p]]), format="markdown", 
                             operation=client.BEFORE_SECTION, section_id=SID[b][Ans_CutSign[b][p]])
                             '''