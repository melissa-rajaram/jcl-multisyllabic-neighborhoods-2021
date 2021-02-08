"""
    Creates the 'Distance based' neighborhood measures used in the paper.

    Phonological Levenshtein Distance:
    Phoneme Feature Distance:

    For each neighborhood measure, creates a num_words x num_words matrix,
    where matrix[word1,word2] is the pariwise similarity. Note that for the
    PLD20 and PFEAT20 measures, an additional step will be needed to determine
    which are the "top 20" words. 

"""

from collections import defaultdict
import re
from copy import copy

path  = '/home/melissa/Dropbox/experiments/python/current_projects'
import sys
sys.path.insert(0,path)

from jcl_multisyllabic_neighborhoods_2021.static.locations import Locations
from jcl_multisyllabic_neighborhoods_2021.creating_variables.neighborhoods.template_representation import Template
import pandas as pd
import numpy as np
import Levenshtein as Lev
#%%

def levensteinSimilarity(word_list):
    """
    This class relates similarity based on the Suarez paper.
    Similarity is defined based on the Levenstein distance of the 
    phonological forms.

    """
    levsim = np.zeros([len(word_list),len(word_list)])
    numwords = len(word_list)
    for row in range(0, numwords -1):
        for col in range(row+1,numwords):
            rword = word_list[row]
            cword = word_list[col]
            levdistance = Lev.distance(rword,cword)
            levsim[row,col] = levdistance
            levsim[col,row] = levdistance

    word_matrix = pd.DataFrame(index=word_list, columns=word_list, data=levsim)

    return word_matrix

#%% setSimilarity

def phonemeFeaturesSimilarity(word_list):
    """
    similarity based on phonemes differences
    
    """
    def trim_templates(temp1,temp2):
        arr1 = np.array(list(temp1))
        dashes1 = (arr1 == "-")
        arr2 = np.array(list(temp2))
        dashes2 = (arr2 == "-")
        
        not_both_dashes = np.logical_not(np.logical_and(dashes1,dashes2))
        return arr1[not_both_dashes],arr2[not_both_dashes]

    def average_differences(stemp1,stemp2):
        assert len(stemp1)==len(stemp2),"Templates not equal length"
        msk = (stemp1 == "-") + (stemp2 == "-")
        short1 = stemp1[np.logical_not(msk)]
        short2 = stemp2[np.logical_not(msk)]
        #print(f'shortened {short1},{short2}')
        diff = 4 * sum(msk)
        #print(f'{sum(msk)} dash mismatch: {diff}')
        for phon in range(0,len(short1)):
            #print(short1[phon],short2[phon])
            if short1[phon] in "a@^cWYEReIioOUu":
                #print(f'{short1[phon]},{short2[phon]},{vowels.loc[short1[phon],short2[phon]]}')
                diff += vowels.loc[short1[phon],short2[phon]]
            else:
                #print(f'{short1[phon]},{short2[phon]},{consonants.loc[short1[phon],short2[phon]]}')
                diff += consonants.loc[short1[phon],short2[phon]]
        #print(f'{diff} / {len(stemp1)} = {diff / len(stemp1)}')
        return diff / len(stemp1)

    # maybe calculate with numpy array, then change to pandas (pandas is super, super slow)
    tem = Template()
    vowel_file = l.phonsim_vowel
    vowels = pd.read_csv(vowel_file,header=0,index_col=0)
    consonant_file = l.phonsim_consonant
    consonants = pd.read_csv(consonant_file,header=0,index_col=0)
    featsim = np.zeros([len(word_list),len(word_list)])
    numwords = len(word_list)
    for row in range(0, numwords -1):
        w1 = tem.getTemplateRepresentation(word_list[row])
        for col in range(row+1,numwords):
            w2 = tem.getTemplateRepresentation(word_list[col])
            trim1,trim2 = trim_templates(w1,w2)
            diff = average_differences(trim1,trim2)
            featsim[row,col] = diff
            featsim[col,row] = diff

    word_matrix = pd.DataFrame(index=word_list, columns=word_list, data=featsim)

    return word_matrix


def get_child_vars(datapath):
    """
    Returns the child variables for each age. 
    Looks for three_vars.pickle, four_vars.pickle, six_vars.pickle
    in the datapath directory given.

    :param: datapath
    :return: threevar, fourvar, sixvar
    """

    threevars = pd.read_pickle(datapath + "pact/three_vars.pickle")
    fourvars = pd.read_pickle(datapath + "pact/four_vars.pickle")
    sixvars = pd.read_pickle(datapath + "pact/six_vars.pickle")

    return threevars, fourvars, sixvars


#%%
# TODO: load data
#       path to cv removed
l = Locations()

threeVars, fourVars, sixVars = get_child_vars(l.datapath)

# creates a list of phonological forms from the dataframe,
# and removes the "1" marking the stressed syllable stress
words_nostress = lambda var: [word.replace("1", "") for word in list(var['phonological'])]
three_words_nostress = words_nostress(threeVars)
four_words_nostress = words_nostress(fourVars)
six_words_nostress = words_nostress(sixVars)


#%%

# get levenstein similarity
three_leven_similarity = levensteinSimilarity(three_words_nostress)
pd.to_pickle(three_leven_similarity,l.distance_neighbors + "sim_3_leven.pickle")

four_leven_similarity = levensteinSimilarity(four_words_nostress)
pd.to_pickle(four_leven_similarity,l.distance_neighbors + "sim_4_leven.pickle")

six_leven_similarity = levensteinSimilarity(six_words_nostress)
pd.to_pickle(six_leven_similarity,l.distance_neighbors + "sim_6_leven.pickle")

#%%

# get phoneme feature based similarity

three_words_stress = threeVars.syllables.values
four_words_stress = fourVars.syllables.values
six_words_stress = sixVars.syllables.values

three_leven_similarity = phonemeFeaturesSimilarity(three_words_stress)
pd.to_pickle(three_leven_similarity,l.distance_neighbors + "sim_3_feature.pickle")

four_leven_similarity = phonemeFeaturesSimilarity(four_words_stress)
pd.to_pickle(four_leven_similarity,l.distance_neighbors +"sim_4_feature.pickle")

six_leven_similarity = phonemeFeaturesSimilarity(six_words_stress)
pd.to_pickle(six_leven_similarity,l.distance_neighbors + "sim_6_feature.pickle")
