import glob
import os
import numpy as np
import netCDF4
from matplotlib import pyplot as plt



def plotEVA(flpth, ptx, pty, outPngFilePath):
    ds = netCDF4.Dataset(flpth)
    
    rp = ds.variables["return_period"][:]
    
    yr = ds.variables["year"][:]
    
    bslnIndx = np.where(yr == 1995)[0][0]
    
    rl = ds.variables["rl_min_ws"][:, bslnIndx, ptx, pty]
    
    yr_min = ds.variables["year_min_ws"][:, ptx, pty]
    
    yr_all = ds.variables["year_all"][:]

    plt.figure(figsize=[18, 9])
    
    plt.plot(yr_all[:30], yr_min[:30])
    for rpi, rli in zip(rp, rl):
        plt.plot([yr_all[0], yr_all[29]], [rli, rli], label=f"ret. lev. {rpi}")
        if rpi <= 100:
            plt.text(yr_all[28], rli, f"{rpi} yr.")
    mnmin = np.mean(yr_min[:30])
    rpmn = np.interp(mnmin, rl[::-1], rp[::-1])
    plt.plot([yr_all[0], yr_all[29]], [mnmin, mnmin], linewidth=3, color="red")
    plt.text(yr_all[1], mnmin, "mean", fontsize=15)
    plt.xlim([yr_all[0], yr_all[29]])
    plt.ylim([np.min(rl) - .1, np.max(rl) + 1])

    plt.title(f"year minima (ws), point: {ptx}, {pty},\n file {flpth}")

    plt.savefig(outPngFilePath)
    return rpmn


def testPlotEva():
    flpth = "/mnt/d/peseta4/examplePeseta4RiverFile/projection_dis_rcp45_DMI-HIRHAM5-ICHEC-EC-EARTH_BC_wuConst_statistics.nc"
    flpth = "/eos/jeodpp/data/projects/CLIMEX/ADAPTATION/ClimateRuns/EVA/eva_discharge_europe/projection_dis_rcp85_CLMcom-CCLM4-8-17_BC_CNRM-CERFACS-CNRM-CM5_wuConst_statistics.nc"
    ptx, pty = 34, 871
    ptx, pty = 94, 748
    plotEVA(flpth, ptx, pty, "test.png")
    plt.show()


def plotFilesFromPattern():
    flpattern = "/eos/jeodpp/data/projects/CLIMEX/ADAPTATION/ClimateRuns/EVA/eva_discharge_europe/projection_dis_rcp*5_*_wuConst_statistics.nc"
    ptx, pty = 94, 748
   #ptx, pty = 34, 871
    ptx, pty = 34, 734
    ptx, pty = 77, 697
    ptx, pty = 95, 748
    ptx, pty = 95, 749
    fls = glob.glob(flpattern)
    fls.sort()
    outdir = f"ptx,pty={ptx},{pty}"
    os.system("mkdir " + outdir)
    allMeanRetPers = []
    for flpth in fls:
        print(f"plotting file {flpth}")
        pngfl = os.path.join(outdir, os.path.basename(flpth) + ".png")
        mnrpi = plotEVA(flpth, ptx, pty, pngfl)
        allMeanRetPers.append(mnrpi)
    mdn = np.median(allMeanRetPers)
    txtfl = os.path.join(outdir, "median.txt")
    fl = open(txtfl, "w")
    fl.write(f"median return period = {mdn}")



if __name__ == "__main__":
   #testPlotEva()
    plotFilesFromPattern()



