"""
    Extracts the orthographic word and frequency data from the raw SALT 
    files, transforms the words into phonological forms, calculates the 
    PACT values, and the traditional neighborhood density and Stress:
    Onset Nucleus density neighborhood measures. Saves the variables
    to pandas pickle files.

"""

path  = '/home/melissa/Dropbox/experiments/python/current_projects'
import sys
sys.path.insert(0,path)

import numpy as np
import pandas as pd

from jcl_multisyllabic_neighborhoods_2021.creating_variables.neighborhoods.similarity import PhonemicSimilarity
from jcl_multisyllabic_neighborhoods_2021.creating_variables.neighborhoods.syllabifier import Syllabifier
from jcl_multisyllabic_neighborhoods_2021.creating_variables.neighborhoods.similarity import SONSimilarity
from jcl_multisyllabic_neighborhoods_2021.creating_variables.transcript_processing.create_lexicons import CreateLexicons
from jcl_multisyllabic_neighborhoods_2021.static.locations import Locations


class CreateVariables:
    """ Only class in module; see header for complete documentation """

    def __init__(self):

        # project specific file locations and variable names
        self.l = Locations()
        self.findShape = Syllabifier('STRESS')        

        # labels for columns in pandas
        self.orthographic = 'orthographic'
        self.phonological = 'phonological'
        self.syllables = 'syllables'

        # indexes for numeric variables
        self.length_syllables = 'length_syllables'
        self.length_phonemes = 'length_phonemes'
        self.str_pos = 'stressed_syll_position'
        self.pct_child = 'percent_child'
        self.pct_adult = 'percent_adult'

        # adding back in neighborhood density
        self.phon_n_density = 'ND'
        self.onset_nucleus_density = 'SOND'

        # Proxy for Acquisition from Conversational Transripts
        self.fau_pct_pct_p2 = 'PACT'


    def create_experimental_vars(self):
        lex = CreateLexicons()
        # OME child with OME adult as frequency
        print('writing child lexicons')
        self.serialize_experimental_vars(lex.child3, lex.adult3, T.l.datapath +'pact/' + T.l.threename)
        self.serialize_experimental_vars(lex.child4, lex.adult4, T.l.datapath +'pact/' + T.l.fourname)
        self.serialize_experimental_vars(lex.child6, lex.adult6, T.l.datapath +'pact/' + T.l.sixname)
        
        print('finished.')

    def serialize_experimental_vars(self, child, adult, filebase):

        def find_orthographic(phon):
            return child[phon]['ORTH']

        def find_length_syllables(phon):
            if self.findShape.number_syllables(phon) > 1:
                return self.findShape.number_syllables(phon)
            else:
                if self.findShape.CVshape(phon) == 'cv1c':
                    return 0
                return 1

        def find_length_phonemes(phon):
            nounder = phon.replace("_","")
            nounder = nounder.replace("1","")
            return len(nounder)

        def find_stressed_syllable(phon):
            pieces = phon.split("_")
            for pos in range(0, len(pieces)):
                if "1" in pieces[pos]:
                    return pos + 1
            print(phon, 'no stress')
            return -1

        def find_log_pct_child(phon):
            return np.log(child[phon]['NUMCHILD'])

        def find_log_pct_adult(phon):
            if phon in adult.keys():
                return np.log(adult[phon]['NUMCHILD'])
            else:
                return np.nan

        def find_syllable_representation(phon):
            return child_SON_sim.phon2syll[phon]

        def adjusted_use(ause,cuse,poly):

            def poly_residual(x_vars, y, poly_order):
                """

                :param x_vars:
                :param y:
                :param poly_order:
                :return:
                """

                x1 = x_vars
                y1 = y

                p = np.polyfit(x1, y1, poly_order)
                yprime = np.polyval(p, x1)
                return y - yprime

            blank = np.zeros(len(vars))
            blank.fill(np.nan)

            adjusted = poly_residual(ause[mask], cuse[mask], poly)
            blank[mask] = adjusted
            return blank

        def find_child_PHON_density(phon):
            return len(current_all_sim[phon])

        def find_child_SON_density(phon):
            return len(child_SON[phon])

        vars = pd.DataFrame()
        vars[self.phonological] = child.keys()
        # variables straight from SALT files
        vars[self.orthographic] = vars.phonological.apply(find_orthographic)
        vars[self.pct_child] = vars.phonological.apply(find_log_pct_child)
        vars[self.pct_adult] = vars.phonological.apply(find_log_pct_adult)

        # relating to word characteristics
        child_SON_sim = SONSimilarity(child.keys()) # for syllable repr.
        vars[self.syllables] = vars.phonological.apply(find_syllable_representation)
        vars[self.length_syllables] = vars.syllables.apply(find_length_syllables)
        vars[self.length_phonemes] = vars.phonological.apply(find_length_phonemes)
        vars[self.str_pos] = vars.syllables.apply(find_stressed_syllable)

        # Neighborhood density
        child_SAD_sim = PhonemicSimilarity(child.keys())
        current_all_sim = child_SAD_sim.findPhonemicSimilarity(child.keys(), True)
        vars[self.phon_n_density] = vars.phonological.apply(find_child_PHON_density)

        # creating stressed syllable based similarity metrics
        child_SON_sim = SONSimilarity(child.keys())
        child_SON = child_SON_sim.stress_onset_nucleus_similarity_word(simtype='onset-nucleus')
        vars[self.onset_nucleus_density] = vars.phonological.apply(find_child_SON_density)

        # calculate PACT values
        mask = np.isfinite(vars[self.pct_adult])
        vars[self.fau_pct_pct_p2] = adjusted_use(vars[self.pct_adult], vars[self.pct_child], 2)

        print('serializing:',filebase)
        vars.to_pickle(filebase + '_vars.pickle')

if __name__ == "__main__":
    # see file header for usage examples
    T = CreateVariables()
    T.create_experimental_vars()