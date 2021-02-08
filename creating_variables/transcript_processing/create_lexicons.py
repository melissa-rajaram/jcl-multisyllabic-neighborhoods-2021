# ! /usr/bin/python
"""
    Creates the lexicons that will be used for the multisyllabic acquisition experiment.
    Creates six lexicons: child at 3, 4 and 6 years, and adult at 3,4, and 6 years

    In its simplest form, a "lexicon" is merely a collection of words. In this work,
    lexicons are constructed as a collection of phonological_transformation forms said by either children
    or adults at either 3, 4, or 6 years. Each phonological_transformation form has two associated variables: the
    number of transcripts that the phonological_transformation form appeared in, and the total number of
    times that the form was used across all transcripts.

    Examples:

        $ python create_lexicons.py
            When run from command line, the total number of words from each lexicon are printed.

            child 3:  1557
            child 4:  1687
            child 6:  2260 

            adult 3:  2073
            adult 4:  2220
            adult 6:  2822

        lex = CreateLexicons()
            When called from other modules,

"""

path  = '/home/melissa/Dropbox/experiments/python/current_projects'
import sys
sys.path.insert(0,path)

from collections import defaultdict

from jcl_multisyllabic_neighborhoods_2021.static.locations import Locations
from jcl_multisyllabic_neighborhoods_2021.creating_variables.transcript_processing.word_evaluation.word_eval import WordEvaluation
from jcl_multisyllabic_neighborhoods_2021.creating_variables.transcript_processing.word_transformation.transform_orth_to_klattese import PhonologicalFromOrthographic


class CreateLexicons():
    """ Only class in module; see header for complete documentation """

    def __init__(self):
        """ Initializes needed modules, and creates child and adult lexicons"""

        # project specific file locations and variable names
        self.loc = Locations()
        self.we = WordEvaluation()
        self.we.load_evaluated_words()
        self.phon = PhonologicalFromOrthographic()

        # number of transcripts at each age
        self.n3 = 747
        self.n4 = 683
        self.n6 = 696

        # creating child lexicons from RWL and word evaluation
        self.child3 = self.apply_word_evaluation(self.loc.threeChildSALT)
        self.child4 = self.apply_word_evaluation(self.loc.fourChildSALT)
        self.child6 = self.apply_word_evaluation(self.loc.sixChildSALT)

        # creating adult lexicons from RWL and word evaluation
        self.adult3 = self.apply_word_evaluation(self.loc.threeAdultSALT)
        self.adult4 = self.apply_word_evaluation(self.loc.fourAdultSALT)
        self.adult6 = self.apply_word_evaluation(self.loc.sixAdultSALT)

    def apply_word_evaluation(self, rwl_file):
        """
        Takes a SALT root word list, and transforms it into a 'lexicon' with
        the number of individuals to use a word, and the number of

        :param rwl_file: SALT Root Word List file
        :param collapse: flag to collapse words to root form
        :return: collection of words with token and numchild information
        """

        def add_token():
            """

            :return: null; acts on current lexicon being created
            """
            if word in newlex:
                oldtoken = newlex[word]['TOKEN']
                newlex[word]['TOKEN'] = token + oldtoken
                newlex[word]['NUMCHILD'] = max([pctchild, newlex[word]['NUMCHILD']])
                newlex[word]['NUMBER'] = newlex[word]['NUMBER'] + nchild
                oldorth = newlex[word]['ORTH']
                newlex[word]['ORTH'] = oldorth + '|' + orth
            else:
                newlex[word]['TOKEN'] = token
                newlex[word]['NUMCHILD'] = pctchild
                newlex[word]['ORTH'] = orth
                newlex[word]['NUMBER'] = nchild

        newlex = defaultdict(dict)

        f = open(rwl_file, "r")
        f.readline()
        for line in f.readlines():
            wordInfo = line.strip()
            wordInfo = wordInfo.split(",")
            orth = wordInfo[0].lower()
            token = int(wordInfo[3])
            pctchild = float(wordInfo[2].rstrip('%'))
            nchild = int(wordInfo[1])
            if orth in self.we.keep_as_is:
                # translate to phonological from orthographic
                word = self.phon.orth_to_phon(orth)
                add_token()
            elif orth in self.we.keep_to_root:
                # reduce orthographic form to root word, then
                # translate to phonological
                word = self.phon.orth_to_phon(self.we.inflect_to_root[orth])
                orth = self.we.inflect_to_root[orth] + ':' + orth
                add_token()
            elif orth in self.we.remove_not_representative:
                # do nothing because word is not representative
                pass


        f.close()

        return newlex


if __name__ == "__main__":
    # see file header for usage examples
    TEST_CASE = CreateLexicons()
    #quit()
    print('child 3: ',len(TEST_CASE.child3))
    print('child 4: ',len(TEST_CASE.child4))
    print('child 6: ',len(TEST_CASE.child6),'\n')
    print('adult 3: ',len(TEST_CASE.adult3))
    print('adult 4: ',len(TEST_CASE.adult4))
    print('adult 6: ',len(TEST_CASE.adult6))

