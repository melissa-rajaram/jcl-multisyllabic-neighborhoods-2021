""" Translates tthe CMU pronounciation dictionary into a dictionary
     containing the word as key pointing to the klatteese translation

    ARGUMENTS:
	a. base path to /experiments/
	b. type of stress pattern used when calculating the phonological
	   forms. Options:
	    - NAIVE: no stress marking used
	    - STRESS: marks vowel with most lexical stress
	c. direction to load dict
	    - ORTH_TO_PHON: orthographic to phonological
	    - PHON_TO_ORTH: phonological to orthographic

	LAST EXAMINED: 10-07-18
	LAST CODED: unknown
    STATUS: - frequently used across projects
            - works as desired

 """
path  = '/home/melissa/Dropbox/experiments/python/current_projects'
import sys
sys.path.insert(0,path)

import re
from current_projects.jcl_multisyllabic_neighborhoods_2021.static.locations import Locations


class CMUTranslator():
    def __init__(self, stressType, dictDirection="ORTH_TO_PHON"):
        self.l = Locations()
        self.myBASE = self.l.mybase
        self.stressType = stressType
        self.CMUDict = {}
        self.arpaToKlatt = {}
        self.loadArpaToKlatt()
        # print "loading CMU Pronounciation dict"
        self.translateDictToKlatt(dictDirection)
        # print "finished loading dict."

    def loadArpaToKlatt(self):
        if self.stressType == "NAIVE":
            aToKFile = self.l.cmu_naive
        elif self.stressType == "STRESS":
            aToKFile = self.l.cmu_stress
        else:
            print("Invalid stress type, no file selected, program will die.")
            quit()
        f = open(aToKFile, "r")
        aToKLines = f.readlines()
        f.close()
        for line in aToKLines:
            # print line.split()[0] + " to " + line.split()[1].strip()
            self.arpaToKlatt[line.split()[0]] = line.split()[1].strip()

    def translateDictToKlatt(self, dictDirection):
        CMUFile = self.l.cmutranslator
        f = open(CMUFile, "r")
        CMULines = f.readlines()
        f.close()
        for line in CMULines:
            if not re.search(";", line):
                phonetic = self.getKlattFromArpa(line.split("  ")[1].strip())
                # print line.split("  ")[0].lower() + " to " + phonetic
                if dictDirection == "PHON_TO_ORTH":
                    self.CMUDict[phonetic] = line.split("  ")[0].lower()
                elif dictDirection == "ORTH_TO_PHON":
                    self.CMUDict[line.split("  ")[0].lower()] = phonetic
                else:
                    print("bad dict direction, quitting")
                    quit()

    def getKlattFromArpa(self, arpaWord):
        phonetic = ""
        # print "arpa: " + arpaWord
        for phoneme in arpaWord.split():
            phonetic = phonetic + self.arpaToKlatt[phoneme]
            # print phonetic
        return phonetic
