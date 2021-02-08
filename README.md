# Code for submission to Journal of Child Language

Please note this is a work in progress. Code is in the process of being documented and this readme file will evolve across that process. 

README for Journal of Child Language Code





This folder contains the code used for the paper: "Phonological neighborhood measures and multisyllabic word acquisition in children."
This git repository is in the process of being updated (7/1/20). Contains the code used in the paper, but may not run. Please check back to later for updates.
[-]



Contents
Creating Variables
Data
phonological_neighborhoods
R
Similarity
Transcript Processing
OVERVIEW The code contained here used used in Melissa Rajaram's 2018 dissertation. Note that this code is poorly documented. Future work will release more usable tools and code.

CONTENTS This file contains a description of how to replicate my dissertation project. However, note that the data for this project is not included.

COMPUTER REQUIREMENTS The following software was used in this project.

SALT (Systematic Analysis of Language Transcripts)
Python 3.5
PYTHON PACKAGE REQUIREMENTS

numpy
pandas
statsmodels
scipy
PRE-REQUISITES FOR DUPLICATION SALT files containing the child and adult language from the OME data set at 3, 4, and 6 years

DATA CREATION create_variables.py

STATISTICS stats-descriptive.py stats-inferrential.py

The first thing to run is create_words_PACT.py