"""
    Create two comma separated value files that can be read easily 
    in R for the mixed model analyses. Combines data across ages
    three, four and six years.
        - CVC words
        - Multisyllabic words

"""
path  = '/home/melissa/Dropbox/experiments/python/current_projects'
import sys
sys.path.insert(0,path)

import pandas as pd
import numpy as np
from jcl_multisyllabic_neighborhoods_2021.static.locations import Locations


l = Locations()

class CombineAcrossAges():

    """
    phonological,ND,SON,PACT,PLD20,PFEAT20,SFEAT20,len_sylls,len_phons,word,age

    """ 

    def combine_across_ages(self):
        """
        Creates two comma separated value files that combine all of the data across
        three, four, and six into one .csv file that is easily read within R

        """
        combined = l.combined

        # AGE 3
        threenew = pd.read_pickle(combined +"data3.pickle")
        threenew['age'] = 'three'
        cvc3 = threenew['iscvc'].values
        mul3 = threenew['ismulti'].values

        # AGE 4
        fournew = pd.read_pickle(combined +"data4.pickle")
        fournew['age'] = 'four'
        cvc4 = fournew['iscvc'].values
        mul4 = fournew['ismulti'].values
        
        # AGE 6
        sixnew = pd.read_pickle(combined+"data6.pickle")
        sixnew['age'] = 'six'
        cvc6 = sixnew['iscvc'].values
        mul6 = sixnew['ismulti'].values

        new_all_cvc = pd.concat([threenew[cvc3],fournew[cvc4],sixnew[cvc6]])
        new_all_multi = pd.concat([threenew[mul3],fournew[mul4],sixnew[mul6]])
        new_all_cvc.to_csv(combined+"cvc_mixed_nomelt.csv")
        new_all_multi.to_csv(combined+"multi_mixed_nomelt.csv")
        print('len cvc',len(new_all_cvc),'len mul',len(new_all_multi))


if __name__ == "__main__":
    # see file header for usage examples
    MA  = CombineAcrossAges()
    MA.combine_across_ages()
    print('finished.')