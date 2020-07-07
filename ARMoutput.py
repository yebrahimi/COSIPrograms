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

# We are good to go ...
GeometryName = "/volumes/selene/users/rhea/geomega/COSI.DetectorHead.geo.setup"

parser = argparse.ArgumentParser(description='Create comparison of ARM plots from event reconstruction files and source location.')
parser.add_argument('-f', '--filename', default='ComptonTrackIdentification.p1.sim.gz', help='File name used for calculating ARM')
parser.add_argument('-m', '--minevents', default='1000000', help='Minimum number of events to use')
parser.add_argument('-x', '--xcoordinate', type=float, default='26.1', help='X coordinate of position in 3D Cartesian coordinates')
parser.add_argument('-y', '--ycoordinate', type=float, default='0.3', help='Y coordinate of position in 3D Cartesian coordinates')
parser.add_argument('-z', '--zcoordinate', type=float, default='64', help='Z coordinate of position in 3D Cartesian coordinates') 

args = parser.parse_args()

FileName = ""
if args.filename != "":
  FileName = args.filename

if int(args.minevents) < 1000000:
  MinEvents = int(args.minevents)

trafiles = [None, None, None, None]
print(args.filename)
f = open(args.filename, "r")
for x in range(0,4):
    trafiles[x] = f.readline()
    print(trafiles[x])


trafiles[0] = "/volumes/selene/users/rhea/revan/Run043.Cs137/Run043.Cs137_Classic.tra"
trafiles[1] = "/volumes/selene/users/rhea/revan/Run043.Cs137/Run043.Cs137_Bayes.tra"
trafiles[2] = "/volumes/selene/users/rhea/revan/Run043.Cs137/smaller.Run043.Cs137_MLP.tra"
trafiles[3] = "/volumes/selene/users/rhea/revan/Run043.Cs137/Run043.Cs137_RF.tra"



###################################################################################################################################################################################

# Load geometry:
Geometry = M.MDGeometryQuest()
if Geometry.ScanSetupFile(M.MString(GeometryName)) == True:
  print("Geometry " + GeometryName + " loaded!")
else:
  print("Unable to load geometry " + GeometryName + " - Aborting!")
  quit()
    
#Create Histogram list 
HistARMlist = [None, None, None, None]
for i in range(0,4):
    HistARMlist[i] = M.TH1D("ARM Plot of Compton events" + str(i), "ARM Plot of Compton Events", 200, -180, 180)
    
# Load file
for y in range(0,4):
    Reader = M.MFileEventsTra()
    if Reader.Open(M.MString(trafiles[y])) == False:
        print("Unable to open file " + FileName + ". Aborting!")
        quit()
    else:
        print("File " + FileName + " loaded!")

#Fill Histogram values
    while True:
        Event = Reader.GetNextEvent()
    if not Event:
        break

    if Event.GetType() == M.MPhysicalEvent.c_Compton:
      ARM_value = Event.GetARMGamma(((M.MVector(args.xcoordinate, args.ycoordinate, args.zcoordinate)), M.MCoordinateSystem.c_Cartesian3D)*(180/pi));
      print(ARM_value)
      HistARMlist[y].Fill(Event.GetARMGamma(M.MVector(args.xcoordinate, args.ycoordinate, args.zcoordinate), M.MCoordinateSystem.c_Cartesian3D)*(180/pi));
    elif Event.GetType() == M.MPhysicalEvent.c_Photo:
      pass

#############################################################################################################################################################################

#Draw Histogram
CanvasARM = M.TCanvas()
#HistARMlist[m].Draw()
HistStack = M.THStack("ID", "ARM Plot of Compton Events")
for m in range(0,4):
    HistStack.Add(HistARMlist[m])
CanvasARM.cd()
HistStack.Draw()
CanvasARM.Update()


# Prevent the canvases from being closed
import os
print("ATTENTION: Please exit by clicking: File -> Close ROOT! Do not just close the window by clicking \"x\"")
print("           ... and if you didn't honor this warning, and are stuck, execute the following in a new terminal: kill " + str(os.getpid()))
M.gApplication.Run()
