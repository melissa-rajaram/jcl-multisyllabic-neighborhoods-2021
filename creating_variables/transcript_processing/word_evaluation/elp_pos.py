""" Downloaded from the English Lexicon Project website.

    This code takes the entire ELP data, and makes a dict for the
    ORTH -> POS mapping

    LAST EXAMINED: 8-29-18
	LAST CODED: early 2018?
    STATUS: works as desired
    
"""
path  = '/home/melissa/Dropbox/experiments/python/current_projects'
import sys
sys.path.insert(0,path)

from jcl_multisyllabic_neighborhoods_2021.static.locations import Locations

class EnglishLexiconProjectPOS():
    def __init__(self):
        self.l = Locations()
        self.location = self.l.english_lexicon_project
        self.elp_pos = dict()
        self.pos_map = self.load_pos_map()
        self.loadPOSFromFile()

    def load_pos_map(self):
        pos_map = dict()
        pos_map['JJ'] = 'ADJECTIVE'
        pos_map['NN'] = 'NOUN'
        pos_map['RB'] = 'ADVERB'
        pos_map['VB'] = 'VERB'
        pos_map['encl'] = 'ENCLITIC'
        pos_map['minor'] = 'OTHER'
        pos_map['?'] = 'UNKNOWN'
        return pos_map

    def loadPOSFromFile(self):

        def readable_pos(shortpos):
            if '|' in shortpos:
                longpos = ""
                indvpos = shortpos.split('|')
                for ipos in indvpos:
                    longpos = longpos + self.pos_map[ipos] + '|'
                return longpos.rstrip('|')
            else:
                return self.pos_map[shortpos]

        f = open(self.location)
        f.readline()
        for line in f.readlines():
            # print(line)
            line = line.replace('"', '')
            line = line.rstrip()
            pieces = line.split(",")
            word = pieces[0].replace('"', "").lower()
            pos = pieces[37].replace('"', "")
            if not 'NULL' in pos:
                pos = readable_pos(pos)
                self.elp_pos[word] = pos
        f.close()

    def print_num_words(self):
        print('len pos =', len(self.elp_pos))


if __name__ == "__main__":
    T = EnglishLexiconProjectPOS()
    T.print_num_words()
