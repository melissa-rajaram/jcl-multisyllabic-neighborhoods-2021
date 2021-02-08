"""
    Merges the dataframes that contain the PACT values, and the distance-
    based neighborhood measures. Note that the distance-based neighborhood
    measures (i.e., PLD20, PFEAT20) need to be calculated beforehand because 
    the 'neighbor' matricies only contain word-to-word distance values.
"""

path  = '/home/melissa/Dropbox/experiments/python/current_projects'
import sys
sys.path.insert(0,path)

from jcl_multisyllabic_neighborhoods_2021.static.locations import Locations

from pathlib import Path
import pandas as pd
import numpy as np

l = Locations()

data = Path(l.datapath)

# load the PACT data

c3 = pd.read_pickle(data/'pact/three_vars.pickle')
c4 = pd.read_pickle(data/'pact/four_vars.pickle')
c6 = pd.read_pickle(data/'pact/six_vars.pickle')

# convienience columns for marking CVC and multisyllabic words
iscvc3 = (c3['length_syllables']==0).values & np.isfinite(c3['percent_adult']).values
iscvc4 = (c4['length_syllables']==0).values & np.isfinite(c4['percent_adult']).values
iscvc6 = (c6['length_syllables']==0).values & np.isfinite(c6['percent_adult']).values

ismulti3 = (c3['length_syllables']>=2).values & np.isfinite(c3['percent_adult']).values
ismulti4 = (c4['length_syllables']>=2).values & np.isfinite(c4['percent_adult']).values
ismulti6 = (c6['length_syllables']>=2).values & np.isfinite(c6['percent_adult']).values

#print(c3.columns)

###############################################################################
# load Levenshtein neighbors (PLD)
###############################################################################

lev3 = pd.read_pickle(l.distance_neighbors + 'sim_3_leven.pickle')
lev4 = pd.read_pickle(l.distance_neighbors + 'sim_4_leven.pickle')
lev6 = pd.read_pickle(l.distance_neighbors + 'sim_6_leven.pickle')

#check to see if the words are in the same order
assert list(c3.phonological.apply(lambda x: x.replace("1",""))) == \
            list(lev3.index),"Age 3 are not equal!"
assert list(c4.phonological.apply(lambda x: x.replace("1",""))) == \
            list(lev4.index),"Age 4 are not equal!"
assert list(c6.phonological.apply(lambda x: x.replace("1",""))) == \
            list(lev6.index),"Age 6 are not equal!"

# Find the mean of the 20 top words, sorted by smallest. 
# Note that this is summing from the [1:20+1] range because
# the distance of a word to itself is always 0.

top = 20
def get_pld20(child):
    newl = pd.DataFrame(data=child.index,index=child.index,columns=['phon'])
    newl['PLD20'] = newl.phon.apply(lambda x: np.mean(np.sort(child.loc[x].values)[1:top+1]))
    newl = newl.drop(['phon'],axis=1)
    return newl

pld20_3 = get_pld20(lev3)
pld20_4 = get_pld20(lev4)
pld20_6 = get_pld20(lev6)

pld20_3 = pld20_3['PLD20'].values
pld20_4 = pld20_4['PLD20'].values
pld20_6 = pld20_6['PLD20'].values

###############################################################################
# Phoneme Feature Discrepancy (PhDis 20)
###############################################################################

phdis3 = pd.read_pickle(l.distance_neighbors + 'sim_3_feature.pickle')
phdis4 = pd.read_pickle(l.distance_neighbors + 'sim_4_feature.pickle')
phdis6 = pd.read_pickle(l.distance_neighbors + 'sim_6_feature.pickle')


# double check words are in same order
assert list(c3.syllables) == list(phdis3.index),"Age 3 are not equal!"
assert list(c4.syllables) == list(phdis4.index),"Age 4 are not equal!"
assert list(c6.syllables) == list(phdis6.index),"Age 6 are not equal!"


# Find the mean of the 20 top words, sorted by smallest. Note that this is summing 
# from the [1:20+1] range because the difference of a word to itself is always 0.
top = 20
def get_phdis20(child):
    newl = pd.DataFrame(data=child.index,index=child.index,columns=['phon'])
    newl['PFEAT20'] = newl.phon.apply(lambda x: np.mean(np.sort(child.loc[x].values)[1:top+1]))
    newl = newl.drop(['phon'],axis=1)
    return newl

phdis20_3 = get_phdis20(phdis3)
phdis20_4 = get_phdis20(phdis4)
phdis20_6 = get_phdis20(phdis6)

phdis20_3 = phdis20_3['PFEAT20'].values
phdis20_4 = phdis20_4['PFEAT20'].values
phdis20_6 = phdis20_6['PFEAT20'].values

#############################################################
# combining into one dataframe
############################################################

from_pact = ['PACT','percent_child', 'percent_adult',
            'syllables', 'length_syllables', 'length_phonemes',
            'stressed_syll_position', 'orthographic', 
            'ND','SOND']

cols = ['PACT','Pct Child', 'Pct Adult', 
        'syllables', 'len_syllables','len_phonemes',
        'stress_syl_pos','orthographic',
        'ND','SOND']


# rearrange the data from the pact dataframe
fromall3 = pd.DataFrame(data=c3[from_pact].values,index=c3.phonological,columns=cols)
fromall4 = pd.DataFrame(data=c4[from_pact].values,index=c4.phonological,columns=cols)
fromall6 = pd.DataFrame(data=c6[from_pact].values,index=c6.phonological,columns=cols)

# add neighbors and cvc and multi flags
d3 = fromall3.assign(PLD20=pld20_3,PFEAT20=phdis20_3,iscvc=iscvc3,ismulti=ismulti3)
d4 = fromall4.assign(PLD20=pld20_4,PFEAT20=phdis20_4,iscvc=iscvc4,ismulti=ismulti4)
d6 = fromall6.assign(PLD20=pld20_6,PFEAT20=phdis20_6,iscvc=iscvc6,ismulti=ismulti6)


d3.to_pickle(l.combined + 'data3.pickle')
d4.to_pickle(l.combined + 'data4.pickle')
d6.to_pickle(l.combined + 'data6.pickle')

print("finished.")

