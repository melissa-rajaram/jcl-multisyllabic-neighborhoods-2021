#! /usr/bin/python

"""
    Contains the subs to aid in the evaluation of orthographic forms from the salt
    root word lists.
    
    The words are evaluated by hand for 'non-representative' words, and also to collapse words
    to their root forms.

"""
path  = '/home/melissa/Dropbox/experiments/python/current_projects'
import sys
sys.path.insert(0,path)

import numpy as np
import pandas as pd
import sklearn.metrics as skmet
from jcl_multisyllabic_neighborhoods_2021.creating_variables.transcript_processing.word_evaluation.elp_pos import EnglishLexiconProjectPOS
from jcl_multisyllabic_neighborhoods_2021.creating_variables.transcript_processing.word_evaluation.mobypos import MobyPOS
from jcl_multisyllabic_neighborhoods_2021.creating_variables.transcript_processing.word_transformation.transform_orth_to_klattese import \
    PhonologicalFromOrthographic
from jcl_multisyllabic_neighborhoods_2021.creating_variables.transcript_processing.word_evaluation.closed_class import ClosedClass
from jcl_multisyllabic_neighborhoods_2021.static.locations import Locations


class WordEvaluation:
    """

    """
    def __init__(self):
        """

        """
        self.l = Locations()
        self.phon = PhonologicalFromOrthographic()
        self.mobypos = MobyPOS(self.l.mybase)
        self.mremove = list(['Conjunction', 'Interjection', 'Pronoun',
                        'Preposition', 'Definite Article', 'Indefinite Article'])
        self.elppos = EnglishLexiconProjectPOS()
        self.closed = ClosedClass()

        self.keep_as_is = set()
        self.remove_not_representative = set()
        self.keep_to_root = set()
        self.inflect_to_root = dict()

    def mobyeval(self,word):
        if word in self.mobypos.mobypos:
            moby = self.mobypos.mobypos[word]
            for POS in moby.split('|'):
                if POS in self.mremove:
                    return True
                else:
                    return False
        else:
            return False

    def elpeval(self,word):
        if word in self.elppos.elp_pos:
            if 'OTHER' in self.elppos.elp_pos[word]:
                return True
            else:
                return False
        else:
            return False

    def closedeval(self,word):
        if word in self.closed.closedclass:
            return True
        else:
            return False

    def get_potential_words(self):
        # gets the orthographic words that have a phonological_transformation translation
        # in the CMU pronunciation dictionary
        ## BROKEN< FIX UP

        def orthographic_from_rwl():
            """

            :param rwl_file:
            :return:
            """

            # extracts each orthographic form from the SALT RWL

            def get_orth_words(rwl_file):
                orth_words = set()

                f = open(rwl_file, "r")
                f.readline()
                for line in f.readlines():
                    wordInfo = line.split(",")
                    orth_words.add(wordInfo[0].lower())
                f.close()

                return orth_words

            c3 = get_orth_words(self.l.threeChildSALT)
            c4 = get_orth_words(self.l.fourChildSALT)
            c6 = get_orth_words(self.l.sixChildSALT)
            a3 = get_orth_words(self.l.threeAdultSALT)
            a4 = get_orth_words(self.l.fourAdultSALT)
            a6 = get_orth_words(self.l.sixAdultSALT)

            return c3,c4,c6,a3,a4,a6

        def getwordsfromsalt():
            # gets the orthographic forms from the SALT Root Word List files

            c3,c4,c6,a3,a4,a6 = orthographic_from_rwl()
            words = c3 | c4 | c6 | a3 | a4 | a6
            return words

        allwords = self.phon.orthographic_with_phonological(getwordsfromsalt())

        return allwords

    def transorm_evaluation_list(self):
        # loads previously evaluated words with POS marking
        # removes pos marking and closed class words

        new = open(self.l.current_eval,'w')
        old = open(self.l.prior_word_eval)
        lines = old.readlines()
        new.write("orth,representative,root\n")
        for x in range(1, len(lines)):
            line = lines[x].rstrip("\n")
            line = line.split(",")
            #if 'ok' in line[0]:
            #    print(line[0],'-',line[1],line[2])
            if not (self.mobyeval(line[0]) or self.elpeval(line[0]) or self.closedeval(line[0])):
                new.write(line[0] + ',' + line[3] + ',' + line[4] + '\n')
        old.close()
        new.close()

    def load_evaluated_words(self):
        # loads the previous evaluation, allowing for a partial evaluation

        f = open(self.l.current_eval,'r')
        words = f.readlines()
        for word in range(1, len(words)):
            # variables written explicitly for clarity
            orth = words[word].rstrip().split(",")[0]
            include = words[word].rstrip().split(",")[1]
            root = words[word].rstrip().split(",")[2]

            if include == '1':
                if root != "":
                    self.keep_to_root.add(orth)
                    self.inflect_to_root[orth] = root
                else:
                    self.keep_as_is.add(orth)
            elif include == '0':
                self.remove_not_representative.add(orth)
            else:
                print(words[word].rstrip())
                print('ERROR: MISEVALUATED!')
                quit()

        #print('len kept as is',len(self.keep_as_is))
        #print('len keep to root', len(self.keep_to_root))
        #print('len remove not representative',len(self.remove_not_representative))

    def get_second_rater_set(self,numget):

        words = open(self.l.current_eval)
        words.readline()
        allwords = words.readlines()
        wordset = np.random.choice(allwords,numget,False)
        f = open(self.l.word_eval_base + 'test_1.csv','w')
        f.write("orth,include,root\n")
        for line in wordset:
            ps = line.split(',')
            f.write(ps[0]+'\n')
        f.close()
        words.close()

    def representative_set(self):

        def find_pcts(zs,os,rts):
            return (zs/(zs+os),os/(zs+os),rts/os)

        def ft(num):
            return np.round(num,2)

        original = pd.read_csv(self.l.current_eval)

        zero = np.sum(original['representative'] == 0)
        ones = np.sum(original['representative'] == 1)
        notnull = original['root'].notnull()
        root = np.sum(np.logical_and(ones,notnull))
        print('zeros',zero,'ones',ones,'root',root)
        whole_rating_teaching = 40
        root_rating_teaching = 20
        pct_10_whole = int(np.ceil(len(original)* .1)) + whole_rating_teaching
        pct_10_root = int(np.ceil(root * .1)) + root_rating_teaching


        rater_yesno = original.sample(pct_10_whole)
        rater_root = original[np.logical_and(ones,notnull)].sample(pct_10_root)
        rater_yesno[0:whole_rating_teaching].to_csv(self.l.word_eval_base + 'rater_yesno_train.csv')
        rater_yesno[whole_rating_teaching + 1:len(rater_yesno)].to_csv(self.l.word_eval_base + 'rater_yesno.csv')
        rater_root[0:root_rating_teaching].to_csv(self.l.word_eval_base + 'rater_root_train.csv')
        rater_root[root_rating_teaching+1:len(rater_root)].to_csv(self.l.word_eval_base + 'rater_root.csv')

    def print_reliability(self):
        # serializes the reliability
        root_acc, root_kappa = self.second_rater_reliability_root()
        yesno_acc, yesno_kappa = self.second_rater_reliability_yesno()
        filename = self.l.word_eval_base + 'second_rater_stats.txt'
        f = open(filename,'w')
        f.write('Yes/No\n')
        f.write('Accuracy: ' + str(yesno_acc) + '\nKappa: ' + str(yesno_kappa) + '\n')
        f.write('Root words\n')
        f.write('Accuracy: ' + str(root_acc) + '\nKappa: ' + str(root_kappa)+'\n')
        f.close()

    def second_rater_reliability_root(self):
        # determines if word rating is sufficient
        second = 'project_files/phonological_neighborhoods/word_evaluation/'
        rater_root = self.l.mybase + second + 'second_rater_root.csv'
        self.load_evaluated_words()
        f = open(rater_root,'r')
        f.readline()
        first = list()
        second = list()
        same = 0
        different = 0
        for line in f.readlines():
            pieces = line.split(',')
            word = pieces[0]
            root = pieces[1].rstrip('\n').rstrip(' ')
            second.append(root)
            if word in self.inflect_to_root:
                first.append(self.inflect_to_root[word])
                if root == self.inflect_to_root[word]:
                    same +=1
                else:
                    #print(word, self.inflect_to_root[word],root)
                    different+= 1
            else:
                if word == 'pajamas':
                    first.append('pajamas')
                print(word,'not in inflected set?')

        return same/(same+different), skmet.cohen_kappa_score(first,second)

    def second_rater_reliability_yesno(self):
        # determines if word rating is sufficient
        second = 'project_files/phonological_neighborhoods/word_evaluation/'
        rater_yesno = self.l.word_eval_base + 'second_rater_yesno.csv'
        self.load_evaluated_words()
        f = open(rater_yesno,'r')
        f.readline()
        first = list()
        second = list()
        same = 0
        different = 0
        for line in f.readlines():
            pieces = line.split(',')
            word = pieces[0]
            include = pieces[1].rstrip('\n').rstrip(' ')
            if include == '1':
                second.append(1)
                if word in self.inflect_to_root:
                    first.append(1)
                    same +=1
                elif word in self.keep_as_is:
                    same +=1
                    first.append(1)
                else:
                    #print('disagree yes',word )
                    different+= 1
                    first.append(0)
            elif include == '0':
                second.append(0)
                if word in self.remove_not_representative:
                    same +=1
                    first.append(0)
                elif word == 'fourteens':
                    same +=1
                    first.append(0)
                else:
                    #print('disagree no',word)
                    different +=1
                    first.append(1)
            else:
                print('----bad eval',include)
                quit()

        return same/(same+different), skmet.cohen_kappa_score(first,second)


if __name__ == "__main__":

    TEST_CASE = WordEvaluation()
    # generates blank eval of all words from before
    #(allwords) = TEST_CASE.get_potential_words()
    # add information from pos of english lexicon project
    TEST_CASE.second_rater_reliability_root()
    TEST_CASE.second_rater_reliability_yesno()
    TEST_CASE.print_reliability()
    TEST_CASE.representative_set()


