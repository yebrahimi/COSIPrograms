# Loop over all the data available

#import ROOT as M
#from pathlib import Path 
#from math import pi
#import argparse

# Load MEGAlib into ROOT
#M.gSystem.Load("$(MEGALIB)/lib/libMEGAlib.so")

# Initialize MEGAlib
#G = M.MGlobal()
#G.Initialize()

#################################################################################################################################################################################
#!/bin/bash
Geometry = "/home/olivia/volumes/data/users/olivia/COSI.DetectorHead.geo.setup"

# Step zero: Create list of runs:
Runs=""
#for File in `ls ../Data/*.roa.gz`; do #includes all runs
for File in `ls ../Data/Cs*.roa.gz`; do 
  Runs+=" $(basename ${File} .roa.gz)"
done

echo "Runs: ${Runs}"

# Step one: Convert everything to evta files
for Run in ${Runs}; do
  mwait -p=nuclearizer -i=cores

  InputFile="../Data/${Run}.roa.gz"
  OutputFile="${Run}.evta.gz"
  nuclearizer -a -g ${Geometry} -c Nuclearizer_ER_Data.cfg -C ModuleOptions.XmlTagMeasurementLoaderROA.FileName=${InputFile} -C ModuleOptions.XmlTagEventSaver.FileName=${OutputFile} &
done
wait

# Step two: Run revan
Algorithms="Classic Bayes MLP RF"
#Algorithms="Classic"
for A in ${Algorithms}; do
  for Run in ${Runs}; do
    mwait -p=revan -i=cores
    # To do: for Bayes MLP & ER you have to replace the training data sets, i.e.
    # <BayesianComptonFile>/volumes/crius/users/andreas/COSI_2016/ER/Sims/Cs137/AllSky/ComptonTMVADataSets.p1.inc1.mc.goodbad.rsp</BayesianComptonFile>
    # <CSRTMVAFile>/volumes/crius/users/andreas/COSI_2016/ER/Sims/Cs137/AllSky/ComptonTMVA.v2.tmva</CSRTMVAFile>
    # <CSRTMVAMethods>MLP</CSRTMVAMethods>
    if A in ${Algorithms} == Bayes, MLP, or RF; do
     revan -a -n -c Revan_ER_${A}.cfg -g ${Geometry} -f ${Run}.evta.gz -C BayesianComptonFile=volumes/crius/users/andreas/COSI_2016/ER/Sims/Cs137/AllSky/ComptonTMVADataSets.p1.inc1.mc.goodbad.rsp
     -C CSRTMVAFile=/volumes/crius/users/andreas/COSI_2016/ER/Sims/Cs137/AllSky/ComptonTMVA.v2.tmva  -C CSRTMVAMethods=MLP 
      
 #What I see in the revan configuration xml file:
#<BayesianComptonFile>/home/andreas/Home/Science/Projects/NCT/NCT_2009/Bayesian/Response.rsp.mc.goodbad.rsp</BayesianComptonFile>
#<CSRTMVAFile />
#<CSRTMVAMethods>BDTD</CSRTMVAMethods>

   else:  if A in ${Algorithms} == Classic
    revan -a -n -c Revan_ER_${A}.cfg -g ${Geometry} -f ${Run}.evta.gz &
  done
  wait
  for Run in ${Runs}; do
    mv ${Run}.tra.gz ${Run}.${A}.tra.gz
  done
done

for Run in ${Runs}; do
  # Run Rhea's program
done

###############################################################################################################################################################################
# 1. Convert the roa files to evta files with nuclearizer
#nuclearizer -c /home/olivia/volumes/selene/COSI_2016/ER/Data/Nuclearizer_ER_Data.cfg -C
#ModuleOptions.XmlTagMeasurementLoaderROA.FileName=RunNum.Isotope.roa.gz -C ModuleOptions.XmlTagEventSaver.FileName=output.RunNum.Isotope.evta.gz
# -g [/home/olivia/volumes/data/users/olivia/COSI.DetectorHead.geo.setup] -a

# 2. Create the 4 tra files for the different event reconstructions with revan
#How to Run in parallel in Revan step
#-- use for loop
#TECHNIQUE = [Bayes, Classic, MLP, RF]
#for i in TECHNIQUE:
#  revan -c /home/olivia/volumes/selene/COSI_2016/ER/Sims/Revan_ER_Bayes.cfg 
#  - f [/home/olivia/output.RunNum.Isotope.evta.gz] -C =/home/olivia/output.RunNum.Isotope.TECHNIQUE.tra.gz
#  -g [/home/olivia/volumes/data/users/olivia/COSI.DetectorHead.geo.setup]  -oi -s -a -n
  
#      --the options to set the save file = ''
# *****Add code for naming tra files (4) uniquely; not "output.tra" -add technique in name; must be done after each tra file is created
# 3. Input those to Rhea's ARM program
# Do it all in parallel.
#'-- look at MEGAlib: 
#mnuclearizer is also an option if you want to run parallel threads. An example of an mnuclearizer command is:
#$ mnuclearizer -c Nuclearizer.cfg -n 19 -f RunTest*.sim
#'Always set the nice level to 19 if you’d like to continue working on that computer and not have it heavily slowed down.
