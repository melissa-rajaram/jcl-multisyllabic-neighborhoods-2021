""" 
    Contains the code for creating a template-based representation
    of a phonological word form 
    
    The representation consists of a sequence of syllables, where each syllable
    consists of a possible CCCVCCCC (8) phoneme combination. This is constructed to
    work on words that are 6 syllables or less. The stressed syllable is placed 
    in the middle, so that requires 11 possible syllables to cover all possible
    places where the stressed syllable could be.
    
    CCCVCCCC CCCVCCCC CCCVCCCC CCCVCCCC CCCVCCCC CCCVCCCC CCCVCCCC CCCVCCCC CCCVCCCC CCCVCCCC CCCVCCCC


"""
# ! /usr/bin/python
import sys
from collections import defaultdict
import re

sys.path.append('/home/melissa/Dropbox/experiments/python/')


class Template():

    def __init__(self):
        pass

    def getTemplateRepresentation(self, word):

        def findSyllableStructure(syllList):
            numSyllables = len(syllList)
            x = '1'
            res = [y for y in syllList if x in y]
            if len(res) != 1:
                print
                "Malformed word token!, go fix: ", syllList
                # quit()
                return (0, 0)
            else:
                stressedSyll = syllList.index(res[0])

            return (numSyllables, stressedSyll)

        syllList = word.split("_")

        (numSyllables, stressedSyll) = findSyllableStructure(syllList)
        if numSyllables > 0:
            # print word,"numsyll:",numSyllables,"stress",stressedSyll
            tempRep = self.fitToTemplate(syllList, numSyllables, stressedSyll)
            return tempRep
        else:
            return "MALFORMED TOKEN: NEEDS KLATTESE, STRESS AND SYLLABLE"

    # finds neighbors in a template-based representation

    def fitToTemplate(self, syllList, numSyllables, stressedSyll):

        def flattenTemplate(template):
            flat = ""
            for syll in template:
                for phon in syll:
                    flat = flat + phon
            # flat = flat + "|"
            return flat

        def loadSyllable(syll):
            # create blank syllable template; position 4 is vowel
            syllable = ["-" for i in range(8)]
            # remove 1 from syll if there
            syll = re.sub("1", "", syll)
            vowelPos = re.findall('[a@^cWYEReIioOUu]', syll)
            assert len(vowelPos) == 1, "BROKEN SYLLABLE SHAPE: either no vowel, or more than one"
            vowelidx = syll.index(vowelPos[0])
            
            syllable[3:3+len(syll)-vowelidx] = syll[vowelidx:len(syll)]
            syllable[0:vowelidx] = syll[0:vowelidx]
        
            return syllable

        def loadTemplate(syllList, numSyllables, stressedSyll):
            # loads a word into the template representation

            # initialize blank template
            syllable = ["-" for i in range(8)]
            template = [syllable for i in range(11)]
            # load syllables into templates
            tempList = list()
            for syll in syllList:
                syllTemp = loadSyllable(syll)
                tempList.append(syllTemp)
            # assigns filled syllables to template
            start = 5 - stressedSyll
            end = start + len(syllList)
            # print "start,end",start,end
            count = 0
            for x in range(start, end):
                template[x] = tempList[count]
                count = count + 1
            return template

        template = loadTemplate(syllList, numSyllables, stressedSyll)
        template = flattenTemplate(template)
        return template


if __name__ == "__main__":
    print('Nothing happens from __main__ when this is run.')
