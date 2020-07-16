# Loop over all the data available

import ROOT as M
from pathlib import Path 
from math import pi
import argparse

#################################################################################################################################################################################

# Load MEGAlib into ROOT
M.gSystem.Load("$(MEGALIB)/lib/libMEGAlib.so")

# Initialize MEGAlib
G = M.MGlobal()
G.Initialize()

GeometryName = "/volumes/data/users/olivia/COSI.DetectorHead.geo.setup"

# 1. Convert the roa files to evta files with nuclearizer
a) In root : nuclearizer -c /volumes/selene/COSI_2016/ER/Data/Nuclearizer_ER_Data.cfg
b) Go to "options" in the top left corner and then click "geometry file" : geometry file = /volumes/data/users/olivia/COSI.DetectorHead.geo.setup
c) In "Measurement loader for ROA files" go to options and put specfic isotope.roa.gz file as /volumes/selene/COSI_2016/ER/Data/Run###.Isotope.roa.gz
-- saves output file as output.evta.gz


# 2. Create the 4 tra files for the different event reconstructions with revan
a) In root : revan -c /volumes/selene/COSI_2016/ER/Sims/Revan_ER_TECHNIQUE.cfg #where TECHNIQUE = Bayes, Classic, MLP, or RF 
b) click 'File', 'Load geometry', and input geometry: volumes/data/users/olivia/COSI.DetectorHead.geo.setup
c) click 'File', 'load configuration', and in Root got to /volumes/selene/COSI_2016/ER/Sims/Revan_ER_TECHNIQUE.cfg #where TECHNIQUE = Bayes, Classic, MLP, or RF 
d) click 'File', 'Open', and input: output.evta.gz
e) click 'Reconstruction', 'Start Event Reconstruction'

#How to Run in parallel in Revan step
-- use for loop
TECHNIQUE = [Bayes, Classic, MLP, RF]
for i in TECHNIQUE:
  revan -c /volumes/selene/COSI_2016/ER/Sims/Revan_ER_i.cfg
  b) click 'File', 'Load geometry', and input geometry: volumes/data/users/olivia/COSI.DetectorHead.geo.setup
  c) click 'File', 'load configuration', and in Root got to /volumes/selene/COSI_2016/ER/Sims/Revan_ER_TECHNIQUE.cfg #where TECHNIQUE = Bayes, Classic, MLP, or RF 
  d) click 'File', 'Open', and input: output.evta.gz
  e) click 'Reconstruction', 'Start Event Reconstruction'

# 3. Input those to Rhea's ARM program

# Do it all in parallel.
-- look at MEGAlib: 
mnuclearizer is also an option if you want to run parallel threads. An example of an mnuclearizer command is:
$ mnuclearizer -c Nuclearizer.cfg -n 19 -f RunTest*.sim
Always set the nice level to 19 if you’d like to continue working on that computer and not have it heavily slowed down.


# From Forwarded email: I think using a consistent amount of events should be OK, for example
  this extracts a file with 100,000 events, which might be OK:
  FILE=Large.evta; LINE=$(awk '/SE/{c++} c==100001{print NR;exit}'
  ${FILE}); head -n ${LINE} ${FILE} > Small.evta
