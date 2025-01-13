#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 08:48:52 2015

@author: tlieber
"""

import sys,os,glob
import multiprocessing
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.uic import *
from analysis import interval_distribution as intdist
from analysis import binomial_distribution as bindist
from audiograb import recording
import numpy as np, math
#from matplotlib.backends import qt4_compat
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

def MakeCanvas():
    w.widgetBin.canvas=MplCanvas()
    w.widgetBin.mpltoolbar = NavigationToolbar(w.widgetBin.canvas, w.widgetBin) 
    w.widgetBin.vbl = QVBoxLayout()
    w.widgetBin.vbl.addWidget(w.widgetBin.canvas)
    w.widgetBin.vbl.addWidget(w.widgetBin.mpltoolbar)
    w.widgetBin.setLayout(w.widgetBin.vbl)
    w.widgetInt.canvas=MplCanvas()
    w.widgetInt.mpltoolbar = NavigationToolbar(w.widgetInt.canvas, w.widgetInt) 
    w.widgetInt.vbl = QVBoxLayout()
    w.widgetInt.vbl.addWidget(w.widgetInt.canvas)
    w.widgetInt.vbl.addWidget(w.widgetInt.mpltoolbar)
    w.widgetInt.setLayout(w.widgetInt.vbl)


class MplCanvas(FigureCanvas):
    def __init__(self):      
        self.fig = Figure( facecolor='white')
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.09,bottom=0.09,right=0.98,top=0.98)
        self.ax.grid(color='r')
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

 
def PlotInt():
    bin_length=w.lineEditIntLength.text()
    steps=w.lineEditIntStep.text()
    times = np.load('times_data.npy')
    w.labelTimeExpiredOut.setText(str(math.ceil(times[-1])))
    w.labelPeaksfoundOut.setText(str(len(times[:-1])))
    w.labelPeaksperSecondOut.setText(str(round(len(times)/math.ceil(times[-1]),2)))
    bins,histogram=intdist(times,float(bin_length),int(steps)+1)
    w.widgetInt.canvas.ax.clear()
    w.widgetInt.canvas.ax.grid(color='r')
    w.widgetInt.canvas.ax.set_xlabel('$\Delta$ t', fontsize=24)
    w.widgetInt.canvas.ax.set_ylabel('Anzahl', fontsize=24)
    w.widgetInt.canvas.ax.plot(bins , histogram , drawstyle='steps', color='blue', linewidth=1.1)  
    w.widgetInt.canvas.draw()
    
 
def PlotBin():
    bin_length=w.lineEditBinLength.text()
    binning=w.lineEditBinBinning.text()
    times =np.load('times_data.npy')
    binomialsx,binomialsy,xticks= bindist(times,float(bin_length),int(binning))
    w.widgetBin.canvas.ax.clear()
    w.widgetBin.canvas.ax.grid(color='r')
    w.widgetBin.canvas.ax.set_xlabel('Ereignisse pro Binomial Laenge', fontsize=24)
    w.widgetBin.canvas.ax.set_ylabel('Anzahl', fontsize=24)
    if int(binning)>1:
        w.widgetBin.canvas.ax.set_xticks(binomialsx)
        w.widgetBin.canvas.ax.set_xticklabels(xticks)
    #w.widgetBin.canvas.ax.set_xlim([maxy+1-5*maxy**0.5,maxy+1+5*maxy**0.5])
    w.widgetBin.canvas.ax.set_ylim([0,max(binomialsy)*1.1])
    w.widgetBin.canvas.ax.bar(binomialsx, binomialsy, align='center', alpha=0.5, width=float(binning)*0.8)
    w.widgetBin.canvas.draw()



def selectfolder():
    global foldername
    foldername = str(QFileDialog.getExistingDirectory(w, "Select Folder"))    
    importfiles()

def importfiles():
    folderlist=sorted(glob.glob(foldername+"/*"))
    filelist=[]
    for x in folderlist:
        filelist.append(os.path.basename(x))
    w.comboBox.addItems(filelist)
    
def rec():
    global p
    w.pushButtonGo.setEnabled(0)
    w.pushButtonStop.setEnabled(1)
    #outfile='blub.txt'
    reclength=int(w.lineEditRecLength.text())
    p=multiprocessing.Process(target=recording, args=(reclength,))#,outfile))
    p.start()
def stop():
    w.pushButtonGo.setEnabled(1)
    w.pushButtonStop.setEnabled(0)
    p.terminate()

def SaveFile():
    filename = QFileDialog.getSaveFileName(w, "Open File")
    times =np.load('times_data.npy')
    with open(filename,'w') as f_handle:
        np.savetxt(f_handle, times[:-1], fmt='%.6f')

def SaveInt():
    bin_length=w.lineEditIntLength.text()
    steps=w.lineEditIntStep.text()
    times = np.load('times_data.npy')
    bins,histogram=intdist(times,float(bin_length),int(steps)+1)
    filename = QFileDialog.getSaveFileName(w, "Open File")
    with open(filename,'w') as f_handle:
        np.savetxt(f_handle, np.c_[bins,histogram], fmt='%.5f')

def SaveBin():
    bin_length=w.lineEditBinLength.text()
    binning=w.lineEditBinBinning.text()
    times =np.load('times_data.npy')
    binomialsx,binomialsy,maxy= bindist(times,float(bin_length),float(binning))
    filename = QFileDialog.getSaveFileName(w, "Open File")
    with open(filename,'w') as f_handle:
        for i in range(0,len(binomialsx)):
            f_handle.write("%.5f\t %.5f\n" %(binomialsx[i],binomialsy[i]))



app = QApplication(sys.argv)
#w = loadUi("MainWindowtest.ui")
w = loadUi("MainWindowtest.ui")
w.pushButtonStop.setEnabled(0)
w.pushButtonReplot.clicked.connect(PlotInt)
w.pushButtonReplot.clicked.connect(PlotBin)
w.pushButtonGo.clicked.connect(rec)
w.pushButtonStop.clicked.connect(stop)
w.pushButtonSaveFile.clicked.connect(SaveFile)
w.pushButtonSaveInt.clicked.connect(SaveInt)
w.pushButtonSaveBin.clicked.connect(SaveBin)
w.pushButtonFolder.clicked.connect(selectfolder)

MakeCanvas()

w.show()
sys.exit(app.exec_())
