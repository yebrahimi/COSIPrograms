###############################################################################################################################################################################
#Written by Olivia Salaben and Andreas Zoglauer
#################################################################################################################################################################################
"To run: cd COSIPrograms"
" python3 Pipeline.py"

#!/bin/bash
Geometry = "/home/olivia/volumes/data/users/olivia/COSI.DetectorHead.geo.setup"

# Step zero: Create list of runs:
Runs=""
for File in 'ls ../Data/*.roa.gz': #includes all runs
#for File in 'ls ../Data/Cs*.roa.gz': do 
  Runs+=" $(basename ${File} .roa.gz)"
done

#echo [Runs: ${Runs}]

# Step one: Convert everything to evta files
for Run in ${Runs}:
  mwait -p=nuclearizer -i=cores

  InputFile="../Data/${Run}.roa.gz"
  OutputFile="${Run}.evta.gz"
  nuclearizer -a -g ${Geometry} -c Nuclearizer_ER_Data.cfg -C ModuleOptions.XmlTagMeasurementLoaderROA.FileName=${InputFile} -C ModuleOptions.XmlTagEventSaver.FileName=${OutputFile} &
done
wait

# Step two: Run revan
Algorithms="Classic Bayes MLP RF"
#Algorithms="Classic"
for A in ${Algorithms}: 
  for Run in ${Runs}: 
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

for Run in ${Runs}:
  python3 ARMoutput.py # Run Rhea's program
done

