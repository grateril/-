import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QComboBox, QCheckBox
from PyQt5.QtMultimedia import QSound
from MainWindow2 import *  # 直接调出MainWindow2，实现界面与业务逻辑的分离
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import wave
import soundfile  # 这个库用来写入滤波后的音频信号
import matplotlib
matplotlib.use('Qt5Agg')   # 连接后端与前端

class MyMainWindow(QMainWindow, Ui_MainWindow):
    matplotlib.rcParams['font.family'] = 'STSong  '  # 使标题可用宋体输出

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)

        self.setupUi(self)
        # 点击关闭菜单时连接槽函 close()
        self.actionClose.triggered.connect(self.close)
        # 点击打开菜单时连接槽函数 openMsg()
        self.actionOpen.triggered.connect(self.openMsg)

        self.pushButton_2.clicked.connect(self.Time_frequency)  # 绘出音频的时域谱和频谱

        self.pushButton_8.clicked.connect(self.iir)  # 按动按钮设计IIR滤波器
        self.pushButton_9.clicked.connect(self.iirFilter)  # 按动按钮用IIR滤波器进行滤波
        self.pushButton_3.clicked.connect(self.compareIIR)  # 按动按钮将滤波前的图像和IIR滤波后的图像放在一起比较
        self.pushButton_4.clicked.connect(self.outputWaviir)  # 将滤波后的波形转化回wav文件

        self.pushButton_10.clicked.connect(self.fir)  # 按动按钮设计FIR滤波器
        self.pushButton_11.clicked.connect(self.firFilter)  # 按动按钮用FIR滤波器进行滤波
        self.pushButton_6.clicked.connect(self.compareFIR)  # 按动按钮将滤波前的图像和FIR滤波后的图像放在一起比较
        self.pushButton_4.clicked.connect(self.outputWavfir)  # 将滤波后的波形转化回wav文件

    def openMsg(self):  # 控制音频文件的打开及播放
        self.file, ok = QFileDialog.getOpenFileName(self, "打开", "音频文件", "(*.wav)")  # 打开文件

    def player(self):
        self.sound = QSound(self.file, self)   # 将播放音频与pushbutton连接
        self.pushButton.clicked.connect(self.sound.play)

    def Time_frequency(self):

        path = self.file  # 将打开的文件传递到本函数
        wavfile = wave.open(path, "rb")
        params = wavfile.getparams()
        # 一次性返回所有的音频参数，返回的是一个元组,包括声道数，量化位数(byte单位)，采样频率，采样点数
        nchannels, sampwidth, framesra, frameswav = params[:4]
        self.datawav = wavfile.readframes(frameswav)
        wavfile.close()
        self.datause = np.fromstring(self.datawav, dtype=np.short)  # 将字符串转换为数组，得到一维的short类型的数组
        self.time = np.arange(0, frameswav) * (1.0 / framesra)  # 赋值的归一化
        print(params)  # 在后台输出音频参数

        self.c = np.fft.fft(self.datause)   # 进行快速傅里叶变换
        self.c = abs(self.c)

        self.freq = np.arange(0, len(self.c))  # 建立时间轴

        fig, ax = plt.subplots(2, 1)

        ax[0].plot(self.time, self.datause)  # 画出时域图像
        ax[0].set_title("Time Domain")
        ax[0].set_xlabel('time /s')
        ax[0].set_ylabel('amplitude ')

        ax[1].plot(self.freq/5, abs(self.c), color='red')  # 画出频域图像
        ax[1].set_title("Frequency Domain")
        ax[1].set_xlabel('frequency /Hz')
        ax[1].set_ylabel('amplitude')

        plt.show()

    def iir(self):
        # 将gui中读取到的数值调用到这里设计滤波器
        f = float(self.lineEdit.text())  # 抽样频率，已经在gui中设置了默认值为8000
        gpass = float(self.lineEdit_6.text())
        gstop = float(self.lineEdit_7.text())

        if self.radioButton_5.isChecked() or self.radioButton_6.isChecked():
            fp1 = float(self.lineEdit_2.text())
            fst1 = float(self.lineEdit_3.text())
            fp2 = float(self.lineEdit_4.text())
            fst2 = float(self.lineEdit_5.text())
            wp = [2 * fp1 / f, 2 * fp2 / f]
            ws = [2 * fst1 / f, 2 * fst2 / f]

        # 低通、高通滤波用这里，只要一组数据
        if self.radioButton_3.isChecked() or self.radioButton_4.isChecked():
            fp1 = float(self.lineEdit_2.text())
            fst1 = float(self.lineEdit_3.text())
            wp = (2 * fp1) / f
            ws = (2 * fst1) / f

        iirType = self.comboBox_2.currentText()  # 在comboBox中选择想要的滤波器类型
        self.b, self.a = signal.iirdesign(wp, ws, gpass, gstop, False, iirType, "ba")  # 根据选择的滤波器类型，返回分子分母形式
        w, h = signal.freqz(self.b, self.a)    #计算滤波器的频率响应

        plt.figure()
        plt.plot(w*f/(2*np.pi) , np.abs(h))
        plt.title('IIR Filter')
        plt.ylabel('decay')
        plt.xlabel('frequency')
        plt.show()

    def fir(self):
        global f, type

        numtaps = int(self.lineEdit_8.text())  # 读取FIR滤波器的阶数
        firWindows = str(self.comboBox.currentText())  # 获取fir滤波器的窗口类型

        if self.radioButton_3.isChecked():  # 低通滤波
            f = float(self.lineEdit_9.text())
            type = 'lowpass'
        if self.radioButton_4.isChecked():  # 高通滤波
            f = float(self.lineEdit_9.text())
            type = 'highpass'
        if self.radioButton_5.isChecked():  # 带通滤波
            f1 = float(self.lineEdit_9.text())
            f2 = float(self.lineEdit_10.text())
            f = [f1, f2]
            type = 'bandpass'
        if self.radioButton_6.isChecked():  # 带阻滤波
            f1 = float(self.lineEdit_9.text())
            f2 = float(self.lineEdit_10.text())
            f = [f1, f2]
            type = 'bandstop'

        self.FIR = signal.firwin(numtaps, f, window=firWindows, pass_zero=type)
        w, h = signal.freqz(self.FIR)

        plt.figure()
        plt.plot(w, np.abs(h))
        plt.title('FIR Filter')
        plt.ylabel('decay')
        plt.xlabel('frequency')
        plt.show()

    def iirFilter(self):  # 用设计出来的滤波器对音频进行滤波

        self.y = signal.lfilter(self.b, self.a, self.datause)  # 用设计出来的滤波器对音频进行滤波
        self.Y = np.fft.fft(self.y)  # 进行快速傅里叶变换 ,求频域

        plt.figure()
        plt.subplot(211)
        plt.title("滤波后的时域图像")
        plt.ylabel("振幅")
        plt.xlabel("时间 /s")
        plt.plot(self.time, self.y)

        plt.subplot(212)
        plt.title("滤波后的频域图像")
        plt.ylabel("幅度")
        plt.xlabel("频率 /Hz")
        plt.plot(self.freq, abs(self.Y), color='red')
        plt.show()

    def firFilter(self):

        a = 1  # 分母为1
        self.z = signal.lfilter(self.FIR, a, self.datause)  # 用设计出来的滤波器对音频进行滤波
        self.Z = np.fft.fft(self.z)

        plt.figure()
        plt.subplot(211)
        plt.title("滤波后的时域图像")
        plt.ylabel("振幅")
        plt.xlabel("时间 /s")
        plt.plot(self.time, self.z)

        plt.subplot(212)
        plt.title("滤波后的频域图像")
        plt.ylabel("幅度")
        plt.xlabel("频率 /Hz")
        plt.plot(self.freq, abs(self.Z), color='red')
        plt.show()

    def compareIIR(self):

        plt.figure()

        plt.subplot(221)
        plt.title("音频文件的时域图像")
        plt.ylabel("振幅")
        plt.xlabel("时间 /s")
        plt.plot(self.time, self.datause)

        plt.subplot(222)
        plt.title("音频文件的频域图像")
        plt.ylabel("幅度")
        plt.xlabel("频率 /Hz")
        plt.plot(self.freq, abs(self.c), color='red')

        plt.subplot(223)
        plt.title("滤波后的时域图像")
        plt.ylabel("振幅")
        plt.xlabel("时间 /s")
        plt.plot(self.time, self.y)

        plt.subplot(224)
        plt.title("滤波后的频域图像")
        plt.ylabel("幅度")
        plt.xlabel("频率 /Hz")
        plt.plot(self.freq, abs(self.Y), color='red')
        plt.show()

    def compareFIR(self):

        plt.figure()

        plt.subplot(221)
        plt.title("音频文件的时域图像")
        plt.ylabel("振幅")
        plt.xlabel("时间 /s")
        plt.plot(self.time, self.datause)

        plt.subplot(222)
        plt.title("音频文件的频域图像")
        plt.ylabel("幅度")
        plt.xlabel("频率 /Hz")
        plt.plot(self.freq, abs(self.c), color='red')

        plt.subplot(223)
        plt.title("滤波后的时域图像")
        plt.ylabel("振幅")
        plt.xlabel("时间 /s")
        plt.plot(self.time, self.z)

        plt.subplot(224)
        plt.title("滤波后的频域图像")
        plt.ylabel("幅度")
        plt.xlabel("频率 /Hz")
        plt.plot(self.freq, abs(self.Z), color='red')
        plt.show()

    def outputWaviir(self):
        self.y = self.y.astype(np.short)  # 经过滤波后的数据是float类型，要重新声明为short类型
        soundfile.write("noise/test.wav", self.y, 8000)

    def outputWavfir(self):
        self.z = self.z.astype(np.short)
        soundfile.write("noise/test.wav", self.z, 8000)

# 开始主循环
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())