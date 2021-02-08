"""
    Loads a file containing part of speech data into a format useful for
    marking the orthographic forms of words.


    Creates dictionary of the forms:
    - RAW -> orth to pos as the file has translated
    - CONDENSED -> orth to phon in noun, verb, adjective, other

     NOTE: the paths to files are hardcoded
    
    RAW POS
    N Nounthe
    p Plural
    h Noun Phrase
    V Verb (usu participle)
    t Verb (transitive)
    i Verb (intransitive)
    A Adjective
    v Adverb
    C Conjunction
    P Preposition
    ! Interjection
    r Pronoun
    D Definite Article
    I Indefinite Article
    o Nominative

    CONDENSED POS
    [N,p,h]		= N - Noun
    [V,t,i]		= V - Verb
    [A,v]		= M - Modifier
    [C,P,!,r,D,I,o] = O - Other

    LAST EXAMINED: 8-29-18
    LAST CODED: early 2018?
    STATUS: works as desired

 """
path  = '/home/melissa/Dropbox/experiments/python/current_projects'
import sys
sys.path.insert(0,path)
from jcl_multisyllabic_neighborhoods_2021.static.locations import Locations


class MobyPOS():
    def __init__(self, posType="RAW"):
        self.l = Locations()
        self.mobypos = dict()


        self.posdef = {'N': 'Noun', 'p': 'Plural', 'h': 'Noun Phrase', 'V': 'Verb (usu participle)',
                       't': 'Verb (transitive)',
                       'i': 'Verb (intransitive)', 'A': 'Adjective', 'v': 'Adverb', 'C': 'Conjunction',
                       'P': 'Preposition',
                       '!': 'Interjection', 'r': 'Pronoun', 'D': 'Definite Article', 'I': 'Indefinite Article',
                       'o': 'Nominative','N/A':'N/A','e':'UNKNOWN'}
        self.loadRawPOS()
        if "CONDENSED" in posType:
            self.condensePOS()

    def loadRawPOS(self):
        posFile = self.l.moby_pos
        f = open(posFile, "r")
        posLines = f.readlines()
        f.close()
        for line in posLines:
            if len(line.split("&")[1].strip()) > 1:
                allpos = line.split("&")[1].strip()
                #print(allpos)
                bigpos = ''
                for pos in allpos:
                    bigpos = bigpos + '|' + self.posdef[pos]
                bigpos = bigpos[1:]
                #print(bigpos)
                self.mobypos[line.split("&")[0]] = bigpos
            # print "------", line.split("&")[1][0]
            else:
                self.mobypos[line.split("&")[0]] = self.posdef[line.split("&")[1].strip()]
                # print "len of raw",len(self.posDict)

    def condensePOS(self):
        nouns = set(["N", "p", "h"])
        verbs = set(["V", "t", "i"])
        modify = set(["A", "v"])
        other = set(["C", "P", "!", "r", "D", "I", "o"])
        for word, pos in self.mobypos.iteritems():
            if pos in nouns:
                self.mobypos[word] = "N"
            elif pos in verbs:
                self.mobypos[word] = "V"
            elif pos in modify:
                self.mobypos[word] = "M"
            elif pos in other:
                self.mobypos[word] = "O"
            else:
                print("invalid pos type:", pos)
                quit()

if __name__ == "__main__":

    MOBY = MobyPOS()