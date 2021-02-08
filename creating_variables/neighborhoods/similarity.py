""" 
    Computes the traditional neighborhood density measure and the 
    Stress: Onset Nucleus neighborhood measure. 

"""
import re
import pandas as pd
from collections import defaultdict
from copy import copy
from .syllabifier import Syllabifier


class SONSimilarity():

    def __init__(self,phonwords,marked_syllables=False):
        self.marked_syllables = marked_syllables
        if self.marked_syllables:
            self.phonsyll = phonwords
        else:
            (self.phonsyll, self.syll2phon, self.phon2syll) = self.createSyllableList(phonwords)

    def createSyllableList(self, phonList):
        # note that phonList can be of any iterable type (list, set)
        findShape = Syllabifier('STRESS')
        syllLex = list()
        syll2phon = dict()
        phon2syll = dict()
        for word in phonList:
            syll = findShape.syllableStructure(word, findShape.CVshape(word))
            syllLex.append(syll)
            syll2phon[syll] = word
            phon2syll[word] = syll
        return (syllLex, syll2phon,phon2syll)

    def trimSyllable(self, syll,trimtype = 'onset-nucleus',wholeword = ""):
        # takes the ending consonants off of the syllable
        # alter this to account for vocalic /r/

        def get_trimmed_syllable():
            # contains logic for trimming different parts of the stressed syllable down

            sylllist = list()
            if trimtype == 'nucleus':
                sylllist.append(syll[posNum:posNum+2])
            elif trimtype == 'onset-nucleus':
                sylllist.append(syll[:posNum + 2])
            elif trimtype == 'nucleus-coda':
                sylllist.append(syll[posNum:])
            elif trimtype == 'onset-nucleus-coda':
                sylllist.append(syll)
            elif trimtype == 'onset-nucleus&nucleus-coda':
                sylllist.append(syll[:posNum + 2])
                sylllist.append(syll[posNum:])
            else:
                print('invalid syllable trim type',trimtype)
                print('define_similar_words->trim syllable')
                quit()
            return sylllist

        def test_for_r(syllpart):
            if syllpart + 'r' in syll:
                return syllpart + 'r'
            else:
                return syllpart

        vowels = "[a@^cWYEReIioOUu]"
        vowelPos = re.findall(vowels, syll)
        if len(vowelPos) == 1:
            posNum = syll.index(vowelPos[0])
        else:
            print("more or less than one vowel: --",wholeword, syll,'-- define_similar_words -> trimsyllable')
            return "BROKEN"

        trimSyll = get_trimmed_syllable()
        for x in range(0,len(trimSyll)):
            trimSyll[x] = test_for_r(trimSyll[x])

        return trimSyll

    def stress_onset_nucleus_similarity_word(self,simtype='onset-nucleus'):
        # define_similar_words based on the number of words that share a similar stressed syllable (in any position)
        # syllable define_similar_words if shares the same onset-nucleus


        def o_n_to_wordset(phonSyll,simtype):
            # returns a dict of all the trimmed stressed syllables in words
            # words are trimmed (or not) based on the simtype

            # return the dict 'onset_nucleus_to_words' where the trimmed
            # stressed syllables are the keys, and the value is a set of
            # words with that stressed syllable

            onset_nucleus_to_words = dict()
            for word in phonSyll:

                syllables = word.split('_')
                for position in range(0, len(syllables)):
                    if "1" in syllables[position]:
                        onset_nucleus = self.trimSyllable(syllables[position],simtype,word)
                        for single in onset_nucleus:
                            try:
                                words = onset_nucleus_to_words[single]
                            except KeyError:
                                words = set()
                            words.add(word)
                            onset_nucleus_to_words[single] = words

            return onset_nucleus_to_words

        (o_n_to_words) = o_n_to_wordset(self.phonsyll,simtype)

        # creates a dict that contains dict[word] = set(similar words)
        o_n_similarity = dict()
        # first assigns all similar words
        for o_n in o_n_to_words:
            words = o_n_to_words[o_n]
            for word in words:
                wordscopy = copy(words)
                wordscopy.discard(word)
                if self.marked_syllables:
                    o_n_similarity[word] = wordscopy
                else:
                    o_n_similarity[self.syll2phon[word]] = wordscopy

        return (o_n_similarity)

class PhonemicSimilarity():
    ## traditional phoneme-based neighborhoods

    def __init__(self,phonwords):
        self.phonwords = phonwords
        ## this assignment is useless. fix to make consistent with other

    def findPhonemicSimilarity(self, lexList,stressFlag = False):
        # finds define_similar_words on a list and returns a dict with word -> similarDict
        # WITHOUT the stress marking on the vowels if stressFlag == False
        self.matchneighborhoods = defaultdict(dict)

        for word in lexList:
            if not stressFlag:
                noStress = re.sub("1", "", word)
                phonList = list(noStress)
            else:
                phonList = list(word)
            self.addNeighborhood(phonList, word)
        similar = self.assignSimilar(lexList)
        similar = self.removeSelfSimilar(similar)
        return similar

    # ------------ used for finding segment-based neighbors

    def addNeighborhood(self, wordList, phonWord):

        # this code is NOT OPTIMIZED!!!!!
        # I can go back and condense these loops foor better performance

        self.matchneighborhoods[phonWord][phonWord] = 1
        self.addition(wordList, phonWord)
        self.deletion(wordList, phonWord)
        self.substitution(wordList, phonWord)

    def addition(self, wordList, phonWord):
        # print "addition"
        for x in range(0, len(wordList) + 1):
            tempList = copy(wordList)
            tempList.insert(x, "_")
            newWord = "".join(tempList)
            self.matchneighborhoods[newWord][phonWord] = 1
            # print "ADD adding: ", newWord, "->",phonWord," =1"

    def deletion(self, wordList, phonWord):
        # print "deletion"
        if not len(wordList) == 1:
            numberList = copy(wordList)
            for x in range(0, len(wordList)):
                numberList[x] = str(x) + numberList[x]
            for x in range(0, len(wordList)):
                # print x, wordList
                tempList = copy(numberList)
                del tempList[x]
                newWord = "".join(tempList)
                self.matchneighborhoods[newWord][phonWord] = 1
                # print "DELETE adding: ", newWord, "->",phonWord," =1"
                # print newWord

    def substitution(self, wordList, phonWord):
        # print "substitution"
        if not len(wordList) == 1:
            for x in range(0, len(wordList)):
                tempList = copy(wordList)
                tempList[x] = "_"
                newWord = "".join(tempList)
                self.matchneighborhoods[newWord][phonWord] = 1
                # print "SUB adding: ", newWord, "->",phonWord," =1"
                # print newWord

    def removeSelfSimilar(self, similar):
        # this sub removes the instances where a word is a neighbor
        # of itself, which inflates the neighbor count
        for word, sims in similar.items():
            sims.pop(word, "")
        return similar

    def assignSimilar(self, lexList):
        # this sub takes the neighborhoods created previously and
        # creates a dict with word -> dictSimilar

        # create empty similar lexicon
        sim = dict()
        for word in lexList:
            sim[word] = dict()

        for _, v in self.matchneighborhoods.items():
            if len(v) > 1:
                for neighbor in v.keys():
                    toUpdate = sim[neighbor]
                    toUpdate.update(v)
                    sim[neighbor] = toUpdate

        return sim


if __name__ == "__main__":
    print('Nothing happens from __main__ when this is run.')
