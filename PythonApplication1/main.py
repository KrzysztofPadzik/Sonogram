from Frame import Ui_MainWindow
import PyQt5
from PyQt5 import  QtWidgets,QtCore
import sys
from PyQt5.QtWidgets import QApplication,QFileDialog,QDialog,QLabel
import time
import pygame
from scipy.io import wavfile
import ctypes

class GuiClass:
    def Alter(self):
        dialogWindow=QDialog()
        ok_button=QLabel("Błąd wyświetlania",dialogWindow)
        dialogWindow.resize(1000,400)
        dialogWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        dialogWindow.setWindowTitle("Error")
        dialogWindow.exec_()
    def __init__(self,Window):
        self.startTime = time.time()
        self.ui = Ui_MainWindow()
        filePath: str
        filePath, _= QFileDialog.getOpenFileName()
        while filePath.find("wav")==-1:
            self.Alter()
            filePath, _ = QFileDialog.getOpenFileName()
        self.ui.Setup(Window,filePath)
        self.ui.linearRegionItem.sigRegionChanged.connect(self.UpdatePlot)
        self.ui.plot2.sigXRangeChanged.connect(self.UpdateRegion)
        self.ui._openFile.triggered.connect(self.Open)
        self.ui._ov20.triggered.connect(lambda x:self.SetOverlap(0.1))
        self.ui._ov30.triggered.connect(lambda x:self.SetOverlap(0.2))
        self.ui._ov40.triggered.connect(lambda x:self.SetOverlap(0.4))
        self.ui._ov50.triggered.connect(lambda x:self.SetOverlap(0.5))
        self.ui._segment256.triggered.connect(lambda x:self.SetSegments(256))
        self.ui._segment512.triggered.connect(lambda x:self.SetSegments(512))
        self.ui._segment1024.triggered.connect(lambda x:self.SetSegments(1024))
        self.ui._segment32.triggered.connect(lambda x:self.SetSegments(32))
        self.ui._blackman.triggered.connect(lambda x: self.SetWindow("blackman"))
        self.ui._flattop.triggered.connect(lambda x: self.SetWindow("flattop"))
        self.ui._hamming.triggered.connect(lambda x: self.SetWindow("hamming"))
        self.ui._hann.triggered.connect(lambda x: self.SetWindow("hann"))
        self.ui._parzen.triggered.connect(lambda x: self.SetWindow("parzen"))
        self.ui._triang.triggered.connect(lambda x: self.SetWindow("triang"))
        self.ui._openAll.triggered.connect(self.PlayFullFile)
        self.ui._section.triggered.connect(self.PlaySelectedPart)
        self.UpdatePlot()
        self.Window=Window
    def Open(self):
        filePath, _ = QFileDialog.getOpenFileName()
        while filePath.find("wav")==-1:
            self.Alter()
            filePath, _ = QFileDialog.getOpenFileName()
        try:
            self.UpdateState(filePath,Window)
        except ValueError:
            self.Alter()
    def UpdateState(self,newPath,Window):
        self.ui.Update(newPath,Window)
        self.ui.linearRegionItem.sigRegionChanged.connect(self.UpdatePlot)
        self.ui.plot2.sigXRangeChanged.connect(self.UpdateRegion)
        self.UpdatePlot()
    def UpdatePlot(self):
        if(self.startTime-time.time()<1):
            item=self.ui.plot2.getPlotItem()
            item.plot(y=self.ui._data,x=self.ui._time)
            self.startTime=time.time()
        self.UpdateSonogram()
    def UpdateRegion(self):
        pass
    def UpdateSonogram(self):
        self.ui.plot2.setXRange(*self.ui.linearRegionItem.getRegion(), padding=0)
        range = self.ui.linearRegionItem.getRegion()
        SonogramTime = (self.ui._time > range[0]) & (self.ui._time < range[1])
        SonogramData = self.ui._data[SonogramTime]
        self.ui.plot3.setXRange(*self.ui.linearRegionItem.getRegion(), padding=0)
        wavfile.write("temp.wav",self.ui.fs,SonogramData)
    def PlayFullFile(self):
        pygame.mixer.music.load(self.ui.fileName)
        pygame.mixer.music.play()
    def PlaySelectedPart(self):
        pygame.mixer.music.load("temp.wav")
        pygame.mixer.music.play()
    def SetOverlap(self,_newOverlap):
        self.ui._ov=_newOverlap
        self.UpdateState(self.ui.fileName,self.Window)
    def SetSegments(self, _newSegements):
        self.ui.nperseg = _newSegements
        self.UpdateState(self.ui.fileName, self.Window)
    def SetWindow(self,_newWindow):
        self.ui.Window=_newWindow
        self.UpdateState(self.ui.fileName,self.Window)
    
if __name__ == "__main__":
    try:
        pygame.init()
        user32 = ctypes.windll.user32
        application = QApplication(sys.argv)
        Window=QtWidgets.QMainWindow()
        dialogWindow = QDialog()
        ok_button = QLabel("Witam, wybierz plik do zbadania, aby przejść dalej zamknij to okno.", dialogWindow)
        dialogWindow.resize(user32.GetSystemMetrics(0),  user32.GetSystemMetrics(1))
        dialogWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        dialogWindow.setWindowTitle("Sonogram - Okno powitalne")
        dialogWindow.exec_()
        graphicInterface=GuiClass(Window)
        b=graphicInterface.ui._menuBar.actions()
        Window.show()
        sys.exit(application.exec_())
    except ValueError:
        dialogWindow = QDialog()
        ok_button = QLabel("Błąd wyświetlania", dialogWindow)
        dialogWindow.resize(1000, 400)
        dialogWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        dialogWindow.setWindowTitle("Error")
        dialogWindow.exec_()
