#!/bin/bash

#chmod u+r+x filename.sh
#./filename.sh
#chmod +x the_file_name

Geometry="/home/andreas/Science/Software/Nuclearizer/MassModel/COSI.DetectorHead.geo.setup"
type nuclearizer >/dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "ERROR: nuclearizer must be installed"
  exit 1
fi
type revan >/dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "ERROR: revan must be installed"
  exit 1
fi
# Step zero: Create list of runs:
Runs=""
while [ $# -gt 0 ] ; do
  echo "PATHS: $1";
  ./Pipeline.sh <path to data files>
  for File in ${PATHS}; do
    cd /volumes/selene/users/yasaman/CopyData
    if [ ! -f $(basename $File) ]; then
      cp ${File} /volumes/selene/users/yasaman/CopyData
    fi
    chmod +x ${File}
    echo "RunElement#" | awk -F. '{print $2}'
    echo "${File}"
    Runs+=" $(basename ${File} .roa.gz)"
  done
done

echo "Runs: ${Runs}"

cp /volumes/selene/COSI_2016/ER/Pipeline/*.cfg /volumes/selene/users/yasaman/CopyData
# Step one: Convert everything to evta files
for Run in ${Runs}; do
  mwait -p=nuclearizer -i=cores

  InputFile="${Run}.roa.gz"
  OutputFile="${Run}.evta.gz"
  nuclearizer -a -g ${Geometry} -c Nuclearizer_ER_Data.cfg -C ModuleOptions.XmlTagMeasurementLoaderROA.FileName=${InputFile} -C ModuleOptions.XmlTagEventSaver.FileName=${OutputFile} &
done
wait

for Run in ${Runs}; do
  OutputFile="${Run}.evta.gz"
  if [ ! -f ${OutputFile} ]; then 
    echo “ERROR: Output file has not been created: ${OutputFile}”; 
    exit 1; 
   fi

done

# Step two: Run revan
#Algorithms="Classic Bayes MLP RF"
Algorithms="Classic"
for A in ${Algorithms}; do
  for Run in ${Runs}; do
    mwait -p=revan -i=cores
    # To do: for Bayes MLP & ER you have to replace the training data sets, i.e.
    # <BayesianComptonFile>/volumes/crius/users/andreas/COSI_2016/ER/Sims/Cs137/AllSky/ComptonTMVADataSets.p1.inc1.mc.goodbad.rsp</BayesianComptonFile>
    # <CSRTMVAFile>/volumes/crius/users/andreas/COSI_2016/ER/Sims/Cs137/AllSky/ComptonTMVA.v2.tmva</CSRTMVAFile>
    # <CSRTMVAMethods>MLP</CSRTMVAMethods>
    grep "TMVA" /volumes/selene/COSI_2016/ER/Pipeline/Revan_ER_MLP.cfg #Revan_ER_Bayes.cfg

    cd /volumes/selene/users/yasaman/CopyData
    ISOTOPE=$(echo ${Run} | awk -F. '{print $2}')
    if [[ ${A} == Classic ]] || [[ ${A} == Bayes ]]; then
      revan -a -n -c Revan_ER_${A}.cfg -g ${Geometry} -f ${Run}.evta.gz &
    elif [[ ${A} == MLP ]] || [[ ${A} == RF ]]; then
      revan -a -n -c Revan_ER_${A}.cfg -g ${Geometry} -f ${Run}.evta.gz #-C CSRTMVAFile==/volumes/crius/users/andreas/COSI_2016/ER/Sims/${ISOTOPE}/AllSky/ComptonTMVA.v2.tmva -C CSRTMVAMethods=${A} &
    else # replace =</volumes/crius/users/andreas/COSI_2016/ER?Sims/${ISOTOPE}/AllSky/ComptonTMVA.v2.tmva with 
      FileName=$(grep CSRTMVAFile Revan_ER_RF.cfg | awk -F'>' '{ print $2}' | awk -F'<' '{print $1}'); echo ${FileName/Cs137/Ba133}
      ${FileName/Cs137/Ba133}
      ${FileName/Cs137/${ISOTOPE}}
      echo "Error when running Revan. Check geometry, file names, or configuration."

    fi
  done
  wait
  for Run in ${Runs}; do
    mv ${Run}.tra.gz ${Run}.${A}.tra.gz
  done
done

for Run in ${Run}; do
   for A in ${Algorithms}; do
#   echo “${Run}.${A}.tra.gz}” >> ${Run}.txt
   echo "${Run}.${A}.tra.gz" >> ${Run}.txt
done
   python3 /volumes/selene/users/yasaman/COSIPrograms/ARMoutput.py -f ${Run}.txt
done

