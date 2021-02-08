"""
    Contains the code to syllabify words without any syllable
    markings.

    NOTE: Syllables are determined using a naieve maximal onset 
	algorithm. This presents with some issues, as it does not
	close the open lax vowels.

    number_syllables: when given a word in klattese, returns the number of syllables
    CV_shape: when given a word in klattese, returns the consonant-vowel shape
    syllableStructure: when given a stress-marked word in klattese, returns
     the form with underscores marking syllable boundaries

"""

import re

class Syllabifier:
    def __init__(self, stresstype):
        self.stressType = stresstype
        self.brokensylls = dict()
        self.fixbroken = {"_ksky":"k_sky"}
        self.errorflag = False

        self.twoCluster = {"sm": 1, "sn": 1, "st": 1, "sw": 1, "sk": 1, "sl": 1, "sp": 1, "sf": 1,
                           "Tw": 1, "dw": 1, "tw": 1, "Tr": 1, "dr": 1, "tr": 1, "kw": 1, "kr": 1,
                           "kl": 1, "pr": 1, "fr": 1, "br": 1, "gr": 1, "pl": 1, "fl": 1, "bl": 1,
                           "gl": 1, "Sr": 1}
        self.threeCluster = {"spl": 1, "spr": 1, "str": 1, "skr": 1, "skw": 1, "sfr": 1}

    def number_syllables(self, phonWord):
        """

        :param phonWord: phonological form in klattese
        :return: an integer containing the number of syllables
        """
        cvWord = self.CVshape(phonWord)
        matches = re.findall("v", cvWord)
        return len(matches)

    def CVshape(self, phonWord):
        """

        :param phonWord: phonological form in klattese
        :return: a string containing c-v shape, i.e. k@t = CVC
        """

        cvWord = re.sub("v", "q", phonWord)
        cvWord = re.sub("[iIeE\@aWY\^cOoUuR\|xX]", "v", cvWord)
        cvWord = re.sub("[^v1]", "c", cvWord)
        return cvWord

    def syllableStructure(self, phonWord, cvWord):
        """

        :param phonWord: phonological form in klattese, may contain stress marking
        :param cvWord: cv shape of phonological form
        :return: string containing phonological form with syllable boundaries marked
                 with underscores
        """

        def initial_boundaries():
            """

            :return: returns 'naive' syllable boundaries
            """
            # add a syllable boundary after each stressed or unstressed vowel
            maxsylcv = re.sub("v1", "q", cvWord)
            maxsylcv = re.sub("v", "v_", maxsylcv)
            maxsylcv = re.sub("q", "q_", maxsylcv)
            maxsylcv = re.sub("q", "v1", maxsylcv)
            lastScore = maxsylcv.rfind("_")
            maxsylcv = maxsylcv[:lastScore] + maxsylcv[lastScore + 1:]
            matches = re.finditer("_", maxsylcv)
            maxPhonSyl = phonWord
            # puts the syllable boundaries in the analogous position of the phonword
            for position in matches:
                maxPhonSyl = maxPhonSyl[:position.start()] + "_" + maxPhonSyl[position.start():]
            return maxPhonSyl

        def adjust_boundary(prior):
            """

            :param prior: string with boundaries to be adjusted
                   match: contains boundary start and end to adjust
            :return: string with adjusted boundary
            """
            bs = match.span()[0]  # boundary start
            be = match.span()[1]  # boundary end
            before = prior[:bs]
            middle = prior[bs:be]
            end = prior[be:]
            new = before + newOrder + end
            return new

        self.errorflag = False
        maxPhonSyl = initial_boundaries()
        # compile to find all possible consonants before vowel
        p = re.compile('_[^iIeE\@aWY\^cOoUuR\|xX1]+')
        consonants = p.finditer(maxPhonSyl)
        for match in consonants:
            lenMatch = len(match.group())
            if lenMatch == 3:  #boundary and two consonants
                if not match.group()[1:3] in self.twoCluster:
                    # if not a two-cluster, move boundary in between consonants
                    newOrder = match.group()[1:2] + "_" + match.group()[2:3]
                    maxPhonSyl = adjust_boundary(maxPhonSyl)
                else:
                    # print for examples
                    #print(maxPhonSyl)
                    pass

            elif lenMatch == 4:  # boundary and three consonants
                #self.errorflag = True
                if not match.group()[1:4] in self.threeCluster:
                    # if not a three-cluster, test if consonant + two-cluster
                    if match.group()[2:4] in self.twoCluster: # second two are a valid cluster
                        #self.errorflag = True
                        newOrder = match.group()[1:2] + "_" + match.group()[2:4]
                        maxPhonSyl = adjust_boundary(maxPhonSyl)
                        #print(maxPhonSyl)

                    elif match.group()[1:3] in self.twoCluster: # first two are a  valid cluster
                        #self.errorflag = True
                        newOrder = match.group()[1:3] + "_" + match.group()[3:4]
                        maxPhonSyl = adjust_boundary(maxPhonSyl)
                        #print(maxPhonSyl)
                        ## note, nothing prints here

                    else:
                        #self.errorflag = True
                        # does not contain three-cluster or two-cluster: hardcode solution
                        softinitial = {"_lk","_nd","_nz","_ld","_nC","_rS","_rt","_rd","_rs","_nt","_ft",
                                       "_mp","_kt","_lz","_lt","_lp","_ks","_nJ"}
                        end_y = {"y"}
                        softfinal = {"_G"}
                        if match.group()[0:3] in softinitial:
                            # treat like lk is a cluster
                            newOrder = match.group()[1:3] + "_" + match.group()[3:4]
                            maxPhonSyl = adjust_boundary(maxPhonSyl)
                            #print(maxPhonSyl)

                        elif match.group()[3:4] in end_y:
                            #self.errorflag = True
                            newOrder = match.group()[1:2] + "_" + match.group()[2:4]
                            maxPhonSyl = adjust_boundary(maxPhonSyl)
                            #print(maxPhonSyl)

                        elif match.group()[0:2] in softfinal:
                            #self.errorflag = True
                            newOrder = match.group()[1:2] + "_" + match.group()[2:4]
                            maxPhonSyl = adjust_boundary(maxPhonSyl)
                            #print(maxPhonSyl)

                        else:
                            self.errorflag = True
                            print('GO AND FIX:',maxPhonSyl,match.group())
                else:
                    # has three cluster, for illustrating
                    #print(maxPhonSyl)
                    pass

            elif lenMatch > 4:  # boundary and 4 or more consonants

                if match.group()[lenMatch - 3:lenMatch] in self.threeCluster:
                    newOrder = match.group()[1:lenMatch - 3] + "_" + match.group()[lenMatch - 3:lenMatch]
                    maxPhonSyl = adjust_boundary(maxPhonSyl)
                    #print(maxPhonSyl)

                elif match.group()[lenMatch - 2:lenMatch] in self.twoCluster:
                    newOrder = match.group()[1:lenMatch - 2] + "_" + match.group()[lenMatch - 2:lenMatch]
                    maxPhonSyl = adjust_boundary(maxPhonSyl)
                    #print(maxPhonSyl)
                    # none printed for child, some in adult

                else:
                    if match.group() in self.fixbroken:
                        #print(maxPhonSyl)
                        maxPhonSyl = maxPhonSyl.replace(match.group(),self.fixbroken[match.group()])
                        #print('fixed',maxPhonSyl)
                    else:
                        print('SYLLABIFIER ERROR:', match.group(), 'in' , maxPhonSyl)
                        if not match.group() in self.brokensylls:
                            newset = set()
                            newset.add(maxPhonSyl)
                            self.brokensylls[match.group()] = newset
                        else:
                            wordset = self.brokensylls[match.group()]
                            wordset.add(maxPhonSyl)
                            self.brokensylls[match.group()] = wordset

        # R-COLORED VOWELS
        # ensures that /r/ following stressed vowel is not broken by syllable boundary
        if "1_r" in maxPhonSyl:
            maxPhonSyl = maxPhonSyl.replace('1_r','1r_')

        # ensures the unstressed 'er' is not broken by a syllable boundary
        if 'E_r' in maxPhonSyl:
            maxPhonSyl = maxPhonSyl.replace('E_r', 'Er_')

        return maxPhonSyl


if __name__ == "__main__":
    print('Nothing happens from __main__ when this is run.')
