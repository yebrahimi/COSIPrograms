# Loop over all the data available

import ROOT as M
from pathlib import Path 
from math import pi
import argparse

# Load MEGAlib into ROOT
M.gSystem.Load("$(MEGALIB)/lib/libMEGAlib.so")

# Initialize MEGAlib
G = M.MGlobal()
G.Initialize()

"Your geometry" = GeometryName = "/volumes/data/users/olivia/COSI.DetectorHead.geo.setup"

################################################################################################################################################################################

#Email tips from Andreas

" -C is part of nuclearizer command line options, i.e. using nuclearizer without the UI. See "nuclearizer --help":

'   Usage: nuclearizer <options>

 '      -c --configuration <filename>.xml.cfg:
 '             Use this file as configuration file.
 '             If no configuration file is give ~/.nuclearizer.xml.cfg is used
 '      -C --change-configuration <pattern>:
 '             Replace any value in the configuration file (-C can be used multiple times)
 '             E.g. to change the roa file, one would set pattern to:
 '             -C ModuleOptions.XmlTagMeasurementLoaderROA.FileName=My.roa
 '      -a --auto:
 '             Automatically start analysis without GUI
 '      -m --multithreading:
'              0: false (default), else: true
'       -g --geometry:
'              Use this geometry file
'       -v --verbosity:
'              Verbosity: 0: Quiet, 1: Errors, 2: Warnings, 3: Info
'       -h --help:
'              You know the answer...

'So in the pipeline you would do:

nuclearizer -c MyConfig.cfg -C
ModuleOptions.XmlTagMeasurementLoaderROA.FileName=My.roa -C [the options
to set the save file] -g [Your geometry] -a


revan -c MyConfig.cfg -C
ModuleOptions.XmlTagMeasurementLoaderROA.FileName=My.evta -C [the options
to set the save file] -g [Your geometry] -a

 Usage: Revan <options>

      -f --filename <filename>:
             Use this file as evta- or sim-file
      -g --geometry <filename>:
             Use this file as geometry-file
      -c --configuration <filename>.cfg:
             Use this file as parameter file.
             All other given infromations such as -f and -g overwrite information in the configuration file.
             If no configuration file is give ~/.revan.cfg is used
      -C --change-configuration <pattern>:
             Replace any value in the configuration file (-C can be used multiple times)
             E.g. to change the coincidence window, one would set pattern to:
             -C CoincidenceWindow=1e-06
         --oi:
             Save the OI information, in case tra files are generated
      -a --analyze:
             Analyze the evta-file given with the -f option, otherwise the file in the configuration file
      -s --generate spectra:
             Generate spectra using the options previously set in the GUI and stored in the configuration file
      -d --debug:
             Use debug mode
      -n --no-gui:
             Do not use a graphical user interface
      -h --help:
             You know the answer...


#################################################################################################################################################################################

# 1. Convert the roa files to evta files with nuclearizer
a) In root : nuclearizer -c /volumes/selene/COSI_2016/ER/Data/Nuclearizer_ER_Data.cfg
b) Go to "options" in the top left corner and then click "geometry file" : geometry file = /volumes/data/users/olivia/COSI.DetectorHead.geo.setup
c) In "Measurement loader for ROA files" go to options and put specfic isotope.roa.gz file as /volumes/selene/COSI_2016/ER/Data/Run###.Isotope.roa.gz
-- saves output file as output.evta.gz
"-- such that ### = 3 digit run number shown on DataSets.txt and Isotope = Na22, Ba133, 
**Add code to read DataSets.txt to get Run### and Isotope name

"Example:"
RunNumBa133 = [Run109, Run110, Run111] #add .Ba133
RunNumCo60 = [Run148] #add .Co60
RunNumCs137 = [Run150, Run043, Run044, Run046, Run047] # add .Cs137
RunNumNa22 = [Run100, Run102, Rnu186, Run098, Run099] #add .Na22
RunNumY88 = [Run104, Run105, Run106, Run107, Run152] #add .Y88
RunNumIsotope= [Run109.Ba133, Run110.Ba133, Run111.Ba133, Run148.Co60, Run150.Cs137, Run043.Cs137,  Run044.Cs137, ...]
for i in RunNumIsotope: 
nuclearizer -c /volumes/selene/COSI_2016/ER/Data/Nuclearizer_ER_Data.cfg -C
ModuleOptions.XmlTagMeasurementLoaderROA.FileName=volumes/selene/COSI_2016/ER/Data/Run###.Isotope.roa.gz -C [the options
to set the save file] -g [volumes/data/users/olivia/COSI.DetectorHead.geo.setup] -a

    --the options to set the save file =''
 
# *****Add code for naming evta file uniquely; not "output.evta"

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
  
  
"Example:"
TECHNIQUE = [Bayes, Classic, MLP, RF]
for i in TECHNIQUE:
  revan -c /volumes/selene/COSI_2016/ER/Sims/Revan_ER_i.cfg -C
  ModuleOptions.XmlTagMeasurementLoaderROA.FileName=output.evta -C [the options
  to set the save file] -g [volumes/data/users/olivia/COSI.DetectorHead.geo.setup] -f -s -n -a
  
      --the options to set the save file = ''
# *****Add code for naming tra files (4) uniquely; not "output.tra" -add technique in name

# 3. Input those to Rhea's ARM program

# Do it all in parallel.
'-- look at MEGAlib: 
mnuclearizer is also an option if you want to run parallel threads. An example of an mnuclearizer command is:
$ mnuclearizer -c Nuclearizer.cfg -n 19 -f RunTest*.sim
'Always set the nice level to 19 if you’d like to continue working on that computer and not have it heavily slowed down.


# From Forwarded email: 
'I think using a consistent amount of events should be OK, for example this extracts a file with 100,000 events, which might be OK:
  FILE=Large.evta; LINE=$(awk '/SE/{c++} c==100001{print NR;exit}'
  ${FILE}); head -n ${LINE} ${FILE} > Small.evta
  
# Automation possibilities:
   'look at for pyautogui help:' https://automatetheboringstuff.com/chapter18/ 
                                 https://github.com/asweigart/pyautogui 
