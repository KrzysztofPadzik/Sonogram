import pyqtgraph
from scipy.io import wavfile
from PyQt5 import uic
from PyQt5 import QtCore, QtWidgets
import numpy
from scipy import fftpack
from scipy.signal import signaltools
from scipy.signal.windows import get_window
import ctypes

class Ui_MainWindow(object):
    def CreatePlots(self):
        self.plot = pyqtgraph.PlotWidget(y=self._data, x=self._time)
        self.plot2 = pyqtgraph.PlotWidget(y=self._data, x=self._time)
        self.plot.setLabel('bottom', "Czas", units='s')
        self.plot.setLabel('left', "Amplituda", units='')
        self.plot2.setLabel('bottom', "Czas", units='s')
        self.plot2.setLabel('left', "Amplituda", units='')
        f, t, amplitude = self.STFT(self._data, self.fs, nperseg=self.nperseg, noverlap=abs(self.nperseg*self._ov), Window=self.Window)
        self.plot3 = pyqtgraph.PlotWidget()
        amplitude = numpy.abs(amplitude)
        amplitude[amplitude==0]=numpy.min(amplitude[amplitude!=0])
        amplitude = 20 * numpy.log10(amplitude)
        pyqtgraph.setConfigOptions(imageAxisOrder='row-major')
        pyqtgraph.mkQApp()
        Window = pyqtgraph.GraphicsLayoutWidget()
        self._image = pyqtgraph.ImageItem()
        self.plot3.addItem(self._image)
        hist = pyqtgraph.HistogramLUTItem()
        hist.autoHistogramRange = True;
        hist.setImageItem(self._image)
        Window.addItem(hist)
        Window.show()
        hist.setLevels(numpy.min(amplitude), numpy.max(amplitude))
        hist.gradient.restoreState(
            {'mode': 'hsv',
             'ticks': [(0.5, (120, 120, 120, 255)),
                       (1.0, (255, 255, 255, 255)),
                       (0.0, (0, 0, 0, 255))]})
        self._image.setImage(amplitude)
        self._image.scale(t[-1] / numpy.size(amplitude, axis=1),
                  f[-1] / numpy.size(amplitude, axis=0))
        self.plot3.setLabel('bottom', "Czas", units='s')
        self.plot3.setLabel('left', "Częstotliwość", units='Hz')
    def CreateSegments(self,Window, nperseg,inputLenght):
        if nperseg > inputLenght:
            nperseg = inputLenght
        Window = get_window(Window, nperseg)
        return Window, nperseg
    def DetrendFunc(self,d):
        return signaltools.detrend(d, type='constant', axis=-1)
    def FFT(self,x, Window, DetrendFunc, nperseg, noverlap, sides):
        if nperseg == 1 and noverlap == 0:
            result = x[..., numpy.newaxis]
        else:
            step = nperseg - noverlap
            shape = x.shape[:-1]+((x.shape[-1]-noverlap)//step, nperseg)
            strides = x.strides[:-1]+(step*x.strides[-1], x.strides[-1])
            result = numpy.lib.stride_tricks.as_strided(x, shape=shape,strides=strides)
        result = DetrendFunc(result)
        result = Window * result
        if sides == 'twosided':
            func = fftpack.fft
        else:
            result = result.real
            func = numpy.fft.rfft
        result = func(result, n=nperseg)
        return result
    def ReadData(self,filePath:str):
        _data: numpy.ndarray
        samplerate, _data = wavfile.read(filePath)
        self._data=_data
        if len(_data.shape)==2:
            self._data=self._data[:,0]
        self.sekundy = len(_data) / float(samplerate)
        self._time = numpy.arange(len(_data)) / float(samplerate)
        self.fs=samplerate
        self.fileName=filePath
    def RemakeGui(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Piorun"))
        self._menuFile.setTitle(_translate("MainWindow", "Plik"))
        self.overlap40.setTitle(_translate("MainWindow", "Długość zakładki"))
        self._menuSegments.setTitle(_translate("MainWindow", "Długość próbki"))
        self._menuWinows.setTitle(_translate("MainWindow", "Okna"))
        self._openFile.setText(_translate("MainWindow", "otwórz"))
        self._ov10.setText(_translate("MainWindow", "10%"))
        self._ov20.setText(_translate("MainWindow", "20%"))
        self._ov30.setText(_translate("MainWindow", "30%"))
        self._ov40.setText(_translate("MainWindow", "40%"))
        self._ov50.setText(_translate("MainWindow", "50%"))
        self._segment256.setText(_translate("MainWindow", "256"))
        self._segment512.setText(_translate("MainWindow", "512"))
        self._segment1024.setText(_translate("MainWindow", "1024"))
        self._segment32.setText(_translate("MainWindow", "32"))
        self._triang.setText(_translate("MainWindow", "triang"))
        self._blackman.setText(_translate("MainWindow", "blackman"))
        self._hamming.setText(_translate("MainWindow", "hamming"))
        self._hann.setText(_translate("MainWindow", "hann"))
        self._flattop.setText(_translate("MainWindow", "flattop"))
        self._parzen.setText(_translate("MainWindow", "parzen"))
        self._openAll.setText(_translate("MainWindow", "Całość"))
        self._section.setText(_translate("MainWindow", "Przedział"))
        self._menuOpen.setTitle(_translate("MainWindow", "Odtwórz"))
    def Setup(self, MainWindow,dataPath):
        self._ov = 0.1
        self.nperseg = 256
        self.Window = 'hamming'
        self.ReadData(dataPath)
        MainWindow.setObjectName("MainWindow")
        user32 = ctypes.windll.user32
        MainWindow.resize( user32.GetSystemMetrics(0),  user32.GetSystemMetrics(1))
        self.CreatePlots()
        self._mainWidget = QtWidgets.QWidget(MainWindow)
        self._mainWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self._mainWidget.setObjectName("MainWidget")
        self._vertical = QtWidgets.QVBoxLayout(self._mainWidget)
        self._vertical.setObjectName("_vertical")
        self._amplituda = self.plot
        self._amplituda.setObjectName("Amlituda")
        self._vertical.addWidget(self._amplituda)
        self._choice = self.plot2
        self._choice.setObjectName("Wybor")
        self._vertical.addWidget(self._choice)
        self.widgetSpektogram = self.plot3
        self.widgetSpektogram.setObjectName("Spektogram")
        self._vertical.addWidget(self.widgetSpektogram)
        MainWindow.setCentralWidget(self._mainWidget)
        self._menuBar = QtWidgets.QMenuBar(MainWindow)
        self._menuBar.setGeometry(QtCore.QRect(0, 0, 723, 22))
        self._menuBar.setObjectName("menu_Bar")
        self._menuFile = QtWidgets.QMenu(self._menuBar)
        self._menuFile.setObjectName("menu_Plik")
        self._menuOpen = QtWidgets.QMenu(self._menuBar)
        self._menuOpen.setObjectName("menu_Otwórz")
        self._menuSegments = QtWidgets.QMenu(self._menuBar)
        self._menuSegments.setObjectName("_menuSegments")
        self._menuWinows = QtWidgets.QMenu(self._menuBar)
        self._menuWinows.setObjectName("menu_Okna")
        self.overlap40 = QtWidgets.QMenu(self._menuBar)
        self.overlap40.setObjectName("overlap40")
        MainWindow.setMenuBar(self._menuBar)
        self._statusBar = QtWidgets.QStatusBar(MainWindow)
        self._statusBar.setObjectName("_statusBar")
        MainWindow.setStatusBar(self._statusBar)
        self._openFile = QtWidgets.QAction(MainWindow)
        self._openFile.setObjectName("OpenFile")
        self._triang = QtWidgets.QAction(MainWindow)
        self._triang.setObjectName("_triang")
        self._blackman = QtWidgets.QAction(MainWindow)
        self._blackman.setObjectName("_blackman")
        self._hamming = QtWidgets.QAction(MainWindow)
        self._hamming.setObjectName("_hamming")
        self._hann = QtWidgets.QAction(MainWindow)
        self._hann.setObjectName("_hann")
        self._flattop = QtWidgets.QAction(MainWindow)
        self._flattop.setObjectName("_flattop")
        self._parzen = QtWidgets.QAction(MainWindow)
        self._parzen.setObjectName("_parzen")
        self._ov10 = QtWidgets.QAction(MainWindow)
        self._ov10.setObjectName("Overlap10")
        self._ov20 = QtWidgets.QAction(MainWindow)
        self._ov20.setObjectName("Overlap20")
        self._ov30 = QtWidgets.QAction(MainWindow)
        self._ov30.setObjectName("Overlap30")
        self._ov40 = QtWidgets.QAction(MainWindow)
        self._ov40.setObjectName("Overlap40")
        self._ov50 = QtWidgets.QAction(MainWindow)
        self._ov50.setObjectName("Overlap50")
        self._segment32 = QtWidgets.QAction(MainWindow)
        self._segment32.setObjectName("segment32")
        self._segment256 = QtWidgets.QAction(MainWindow)
        self._segment256.setObjectName("segment256")
        self._segment512 = QtWidgets.QAction(MainWindow)
        self._segment512.setObjectName("segment512")
        self._segment1024 = QtWidgets.QAction(MainWindow)
        self._segment1024.setObjectName("segment1024")
        self._openAll = QtWidgets.QAction(MainWindow)
        self._openAll.setObjectName("OtworzCalosc")
        self._section = QtWidgets.QAction(MainWindow)
        self._section.setObjectName("_section")
        self._menuFile.addAction(self._openFile)
        self.overlap40.addAction(self._ov10)
        self.overlap40.addAction(self._ov20)
        self.overlap40.addAction(self._ov40)
        self.overlap40.addAction(self._ov50)
        self._menuSegments.addAction(self._segment32)
        self._menuSegments.addAction(self._segment256)
        self._menuSegments.addAction(self._segment512)
        self._menuSegments.addAction(self._segment1024)
        self._menuWinows.addAction(self._triang)
        self._menuWinows.addAction(self._blackman)
        self._menuWinows.addAction(self._hamming)
        self._menuWinows.addAction(self._hann)
        self._menuWinows.addAction(self._flattop)
        self._menuWinows.addAction(self._parzen)
        self._menuBar.addAction(self._menuFile.menuAction())
        self._menuBar.addAction(self.overlap40.menuAction())
        self._menuBar.addAction(self._menuSegments.menuAction())
        self._menuBar.addAction(self._menuWinows.menuAction())
        self._menuOpen.addAction(self._openAll)
        self._menuOpen.addAction(self._section)
        self._menuBar.addAction(self._menuOpen.menuAction())
        self.RemakeGui(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.linearRegionItem = pyqtgraph.LinearRegionItem([0, self._time[-1]])
        self.linearRegionItem.setZValue(-10)
        self.plot.addItem(self.linearRegionItem)
        self.RemakeGui(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    def STFT(self,x, fs=1.0, Window='hamming', nperseg=256, noverlap=None):
        x = numpy.asarray(x)
        outdtype = numpy.result_type(x, numpy.complex64)
        if x.size == 0:
            return numpy.empty(x.shape), numpy.empty(x.shape), numpy.empty(x.shape)
        if nperseg is not None:
            nperseg = int(nperseg)
            if nperseg < 1:
                raise ValueError('nperseg musi być dodatnią liczbą całkowitą.')
        Window, nperseg = self.CreateSegments(Window, nperseg,inputLenght=x.shape[-1])
        if noverlap is None:
            noverlap = nperseg*0.5
        else:
            noverlap = int(noverlap)
        if numpy.result_type(Window,numpy.complex64) != outdtype:
            Window = Window.astype(outdtype)
        scale = 1.0 / Window.sum()**2
        scale = numpy.sqrt(scale)
        if numpy.iscomplexobj(x):
            sides = 'twosided'
        else:
            sides = 'onesided'
        if sides == 'twosided':
            freqs = fftpack.fftfreq(nperseg, 1/fs)
        elif sides == 'onesided':
            freqs = numpy.fft.rfftfreq(nperseg, 1/fs)
        result = self.FFT(x, Window, self.DetrendFunc, nperseg, noverlap, sides)
        result *= scale
        time = numpy.arange(nperseg/2, x.shape[-1] - nperseg/2 + 1,
                         nperseg - noverlap)/float(fs)
        result = result.astype(outdtype)
        result = numpy.rollaxis(result, -1, -2)
        return freqs, time, result
    def Update(self,newPath,MainWindow):
        self.ReadData(newPath)
        self.plot.close()
        self.plot2.close()
        self.plot3.close()
        self.CreatePlots()
        self._amplituda = self.plot
        self._amplituda.setObjectName("_amplituda")
        self._vertical.addWidget(self._amplituda)
        self._choice = self.plot2
        self._choice.setObjectName("_choice")
        self._vertical.addWidget(self._choice)
        self.widgetSpektogram = self.plot3
        self.widgetSpektogram.setObjectName("widgetSpektogram")
        self._vertical.addWidget(self.widgetSpektogram)
        self.linearRegionItem = pyqtgraph.LinearRegionItem([0, self._time[-1]])
        self.linearRegionItem.setZValue(-10)
        self.plot.addItem(self.linearRegionItem)
        self.RemakeGui(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)





