#####################################################################################################################################################################
#Written by Rhea Senthil Kumar
######################################################################################################################################################################
import ROOT as M
import statistics
######################################################################################################################################################################
#Secondary Functions for Main ARM Output Program
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
    return round(FWHM, 2)

#Bootstrap Functions
def bootstrapFWHM(Hist, FWHMs, R=1000):
    #FWHMs = []
    Sample = []
    for i in range(R):
        ARMSample = M.TH1D("Sample", "", 501, -180, 180)
        for w in range(1, int(Hist.GetEntries())):
            event = Hist.GetRandom()
            ARMSample.Fill(event)
        fwhm = getFWHM(ARMSample)
        FWHMs.append(fwhm)
    stderror = statistics.stdev(FWHMs)
    print(round(stderror, 2))
    return round(stderror, 2)


def bootstrapRMS(Hist, R=1000):
    RMSs = []
    Sample = []
    for i in range(R):
        ARMSample = M.TH1D("Sample", "", 501, -180, 180)
        for w in range(1, int(Hist.GetEntries())):
            event = Hist.GetRandom()
            ARMSample.Fill(event)
        rms = ARMSample.GetRMS()
        RMSs.append(rms)
    stderror = statistics.stdev(RMSs)
    print(round(stderror, 2))
    return round(stderror, 2)

def bootstrapPeak(Hist, R=1000):
    Peaks = []
    Sample = []
    for i in range(R):
        ARMSample = M.TH1D("Sample", "", 501, -180, 180)
        for w in range(1, int(Hist.GetEntries())):
            event = Hist.GetRandom()
            ARMSample.Fill(event)
        peak = getMaxHist(ARMSample)
        Peaks.append(peak)
    stderror = statistics.stdev(Peaks)
    print(round(stderror, 2))
    return round(stderror, 2)

