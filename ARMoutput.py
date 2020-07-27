import ROOT as M 
import math
from math import pi
from math import log
import argparse
import ctypes
import numpy as np

#################################################################################################################################################################################

# Load MEGAlib into ROOT
M.gSystem.Load("$(MEGALIB)/lib/libMEGAlib.so")

# Initialize MEGAlib
G = M.MGlobal()
G.Initialize()

# We are good to go ...
GeometryName = "/volumes/selene/users/rhea/geomega/COSI.DetectorHead.geo.setup"

parser = argparse.ArgumentParser(description='Create comparison of ARM plots from event reconstruction files and source location.')
parser.add_argument('-f', '--filename', default='ComptonTrackIdentification.p1.sim.gz', help='txt file name used for calculating ARM. Contains paths to tra files.')
parser.add_argument('-m', '--minevents', default='1000000', help='Minimum number of events to use')
parser.add_argument('-x', '--xcoordinate', type=float, default='26.1', help='X coordinate of position in 3D Cartesian coordinates')
parser.add_argument('-y', '--ycoordinate', type=float, default='0.3', help='Y coordinate of position in 3D Cartesian coordinates')
parser.add_argument('-z', '--zcoordinate', type=float, default='64', help='Z coordinate of position in 3D Cartesian coordinates') 
parser.add_argument('-l', '--logarithmic', type=str, default='no', help='If set to yes, displays ARM plot on a logarithmic-scaled y-axis.') 
parser.add_argument('-e', '--energy', type=float, default='662', help='Peak energy value for source. Outputs ARM histograms with a +-1.5% energy window.')
parser.add_argument('-t', '--title', type=str, default='ARM Plot for Compton Events', help='Title for ARM Plot')

args = parser.parse_args()

if args.filename != "":
  FileName = args.filename

X = float(args.xcoordinate)
Y = float(args.ycoordinate)
Z = float(args.zcoordinate)

if args.logarithmic != "":
    log = args.logarithmic

low_e = 0.985 * float(args.energy)
high_e = 1.015 * float(args.energy)

if int(args.minevents) < 1000000:
  MinEvents = int(args.minevents)

if args.title != "":
    title = args.title

trafiles = [None, None, None, None]
f = open(args.filename, "r")
for x in range(0,4):
    trafiles[x] = str(f.readline()).strip()
    print(trafiles[x])

def getMaxHist(Hist):
    Max = 0
    for b in range(1, Hist.GetNbinsX()+1):
        if Hist.GetBinContent(b) > Max:
            Max = Hist.GetBinContent(b)
    return Max

def getFWHM(Hist):
    half_peak = getMaxHist(Hist)/2
    low_halfpeak, high_halfpeak = 0,0
    for c in range(1, Hist.GetNbinsX()+1):
        if Hist.GetBinContent(c) > half_peak:
            low_halfpeak = (Hist.GetXaxis().GetBinCenter(c) + Hist.GetXaxis().GetBinCenter(c+1))/2
            break
    for d in reversed(range(1, Hist.GetNbinsX()+1)):
        if Hist.GetBinContent(d) > half_peak:
            high_halfpeak = (Hist.GetXaxis().GetBinCenter(d) + Hist.GetXaxis().GetBinCenter(d+1))/2
            break
    print(low_halfpeak, high_halfpeak)
    FWHM = high_halfpeak - low_halfpeak
    return FWHM

###################################################################################################################################################################################

# Load geometry:
Geometry = M.MDGeometryQuest()
if Geometry.ScanSetupFile(M.MString(GeometryName)) == True:
  print("Geometry " + GeometryName + " loaded!")
else:
  print("Unable to load geometry " + GeometryName + " - Aborting!")
  quit()
    
#Create Histogram list and color
HistARMlist = [None, None, None, None]
for i in range(0,4):
    HistARMlist[i] = M.TH1D("ARM Plot of Compton events" + str(i), title, 501, -180, 180)
    
HistARMlist[0].SetLineColor(M.kRed)
HistARMlist[1].SetLineColor(M.kGreen)
HistARMlist[2].SetLineColor(M.kBlue)
HistARMlist[3].SetLineColor(M.kBlack)

# Load file
for y in range(0,4):
    Reader = M.MFileEventsTra()
    if Reader.Open(M.MString(trafiles[y])) == False:
        print("Unable to open file " + FileName + ". Aborting!")
        quit()
    else:
        print("File " + FileName + " loaded!")

#Fill Histogram values
    counter = 0 
    while counter <= 1000000:
        Event = Reader.GetNextEvent()
        counter = counter + 1
        if not Event:
            break

        if (Event.GetType() == M.MPhysicalEvent.c_Compton) and (low_e <= Event.Ei() <= high_e):
            ARM_value = Event.GetARMGamma((M.MVector(X, Y, Z)), M.MCoordinateSystem.c_Cartesian3D)*(180/pi);
            print(ARM_value)
            HistARMlist[y].Fill(Event.GetARMGamma(M.MVector(X, Y, Z), M.MCoordinateSystem.c_Cartesian3D)*(180/pi));
        elif Event.GetType() == M.MPhysicalEvent.c_Photo:
            pass

#############################################################################################################################################################################

#Draw Histogram, Set Up Canvas
CanvasARM = M.TCanvas("CanvasARM", title, 650, 800)
print("Drawing ARM histograms for each method...")
for m in range(0,4):
    if log == 'yes':
        M.gPad.SetLogy()
        HistARMlist[0].GetYaxis().SetTitle("Counts [logarithmic]")
        HistARMlist[m].Draw("same")
    else:
        HistARMlist[0].GetYaxis().SetTitle("Counts")
        HistARMlist[m].Draw("same")
HistARMlist[0].SetTitle(title)
HistARMlist[0].GetXaxis().SetTitle("ARM [deg]")
HistARMlist[0].GetXaxis().CenterTitle()
HistARMlist[0].GetYaxis().CenterTitle()

CanvasARM.cd()
CanvasARM.SetGridx()
CanvasARM.SetBottomMargin(0.5)

#Create Legend [Method, RMS Value, Peak Height, Total Count, FWHM]
print("Creating legend...")
#x, y, z = ctypes.c_int, ctypes.c_int, ctypes.c_int
#HistARMlist[0].GetBinXYZ(HistARMlist[0].GetMaximumBin(), ctypes.byref(x), ctypes.byref(y), ctypes.byref(z))
#print(x, y, z)
legend = M.TLegend(0.15, 0.35, 0.85, 0.1)
legend.SetHeader("Analysis Methods, RMS Values, Peak Height, Total Count, FWHM", "C")
legend.SetTextSize(0.017)
legend.SetNColumns(5)

legend.AddEntry(HistARMlist[0], "Classic Method", "l")
legend.AddEntry(HistARMlist[0], str(HistARMlist[0].GetRMS()), "l")
legend.AddEntry(HistARMlist[0], str(getMaxHist(HistARMlist[0])), "l")
legend.AddEntry(HistARMlist[0], str(HistARMlist[0].GetEntries()), "l") 
legend.AddEntry(HistARMlist[0], str(getFWHM(HistARMlist[0])), "l")

legend.AddEntry(HistARMlist[1], "Bayes Method", "l")
legend.AddEntry(HistARMlist[1], str(HistARMlist[1].GetRMS()), "l")
legend.AddEntry(HistARMlist[1], str(getMaxHist(HistARMlist[1])), "l")
legend.AddEntry(HistARMlist[1], str(HistARMlist[1].GetEntries()), "l")
legend.AddEntry(HistARMlist[1], str(getFWHM(HistARMlist[1])), "l")

legend.AddEntry(HistARMlist[2], "MLP Method", "l")
legend.AddEntry(HistARMlist[2], str(HistARMlist[2].GetRMS()), "l")
legend.AddEntry(HistARMlist[2], str(getMaxHist(HistARMlist[2])), "l")
legend.AddEntry(HistARMlist[2], str(HistARMlist[2].GetEntries()), "l")
legend.AddEntry(HistARMlist[2], str(getFWHM(HistARMlist[2])), "l")

legend.AddEntry(HistARMlist[3], "RF Method", "l")
legend.AddEntry(HistARMlist[3], str(HistARMlist[3].GetRMS()), "l")
legend.AddEntry(HistARMlist[3], str(getMaxHist(HistARMlist[3])), "l")
legend.AddEntry(HistARMlist[3], str(HistARMlist[3].GetEntries()), "l")
legend.AddEntry(HistARMlist[3], str(getFWHM(HistARMlist[3])), "l")

legend.Draw()

CanvasARM.Update()

# Prevent the canvases from being closed
import os
print("ATTENTION: Please exit by clicking: File -> Close ROOT! Do not just close the window by clicking \"x\"")
print("           ... and if you didn't honor this warning, and are stuck, execute the following in a new terminal: kill " + str(os.getpid()))
M.gApplication.Run()
