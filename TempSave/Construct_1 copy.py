from typing import overload
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
import time
import sys
from BiliClass import BiliVideo
import os
import ctypes

#可视化选择path: QFileDialog

def get_object(object_id):
    return ctypes.cast(object_id, ctypes.py_object).value
    pass

#self是主窗口类的实例
class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.InitOriginUI()
        self.child_window = None
        self.signalTuple_single = None
        self.signalTuple_multiple = None
        
    def InitOriginUI(self):
        self.setGeometry(300,300,1500,1000)
        self.setWindowTitle('BiliCrawler')
        WindowIcon = QIcon('Project\PyQt5\CrawlerGUI_BiliBili\IconLib\Icon.jpg')
        self.setWindowIcon(WindowIcon)
        #显示状态栏
        self.status()
        #显示主菜单
        self.menu()

        #显示主窗口
        self.show()
    def InitUI_single(self):
        #输出封面的路径
        self.facePath = 'E:/CodeField_1/Code_Python_E/Project/PyQt5/CrawlerGUI_BiliBili/IconLib/'
        self.outputPath = self.signalTuple_single[2]
        #在开始爬虫前检查输出路径
        if(not os.path.exists(self.outputPath)):
            self.pathCritical()
            return False
        
        self.video = BiliVideo(self.signalTuple_single[0])
        self.quality = self.signalTuple_single[1]
        #检查bvid
        if self.video.res.status_code != 200:
            self.bvidCritical()
            return False
        #检查视频清晰度
        if self.video.qualityCheck(Quality= self.quality) == False:
            abort = self.qualityCritical()
            if abort == False:
                return False
        
        self.BasicInfo = {'title':self.video.title, 'authorID':self.video.mid_author,
                          'aid':self.video.aid, 'cid':self.video.cid}
        self.TotalInfo = self.video.TotalInfo()
        self.video.GetFace(path= self.facePath)
        
        
        self.centralUI_single = CentralWidget_single(self)
        self.setCentralWidget(self.centralUI_single)
        
        
        
        pass
    #输入参数有误后弹出提示对话框
    def qualityCritical(self):
        msgBox = QMessageBox()
        msgBox.setWindowTitle('QualityError')
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText("The quality you select is out of range.\nThe current highest quality will be selected by default.")
        msgBox.setStandardButtons(QMessageBox.Retry | QMessageBox.Ignore | QMessageBox.Abort)
        msgBox.setDefaultButton(QMessageBox.Retry)
        msgBox.setDetailedText('The highest Quality is: %s'%self.video.HighestQuality)
        reply = msgBox.exec() 
        if reply == QMessageBox.Abort:
            return False
        else:
            pass#self.la.setText('你选择了Ignore')
    def bvidCritical(self):
        msgBox = QMessageBox()
        msgBox.setWindowTitle('BvidError')
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText("The video you select is not exist.")
        msgBox.setStandardButtons(QMessageBox.Retry)
        msgBox.setDefaultButton(QMessageBox.Retry)
        reply = msgBox.exec() 
        if reply == QMessageBox.Retry:
            self.child_window.show()
            pass     
    def pathCritical(self):
        msgBox = QMessageBox()
        msgBox.setWindowTitle('PathError')
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText("The path you select is not exist.")
        msgBox.setStandardButtons(QMessageBox.Retry | QMessageBox.Abort)
        msgBox.setDefaultButton(QMessageBox.Retry)
        reply = msgBox.exec() 
        if reply == QMessageBox.Retry:
            self.child_window.show()
        else:
            return False
        pass
    #测试输入框
    def showDialog(self):
        sender = self.sender()
        if sender == self.bt1:
            text, ok = QInputDialog.getText(self, '测试输入框', '请随意输入：')
            if ok:
                self.showChild()
                pass
        pass
    #构建状态栏
    def status(self):
        self.statusBar().showMessage('创建新项目以继续..')
        pass
    #菜单的构建是自底向上的, 需要先从子菜单开始构建
    def menu(self):
        #以下是文件菜单的构造
        iconPath = ''
        #iconPath = 'E:\CodeField_1\Code_Python_E\Project\PyQt5\IconLib\exit.jpg'
        exitAct = QAction(QIcon(iconPath), '退出(&E)', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('退出程序')
        exitAct.triggered.connect(qApp.quit)
        #创建多级子菜单('项目'下的)
        projectMenu = QMenu('创建项目', self)
        singleAct = QAction(QIcon(),'获取单个视频(&S)', self)
        singleAct.triggered.connect(self.showChild)
        multiAct = QAction('获取多个视频(&M)', self)
        projectMenu.addAction(singleAct)
        projectMenu.addAction(multiAct)
        
        aboutAuthor = QAction('关于作者', self)
        aboutQt = QAction('关于QT', self)
        
        #创建菜单栏
        menubar = self.menuBar()
        #文件菜单
        fileMenu = menubar.addMenu('文件(&F)')
        fileMenu.addAction(exitAct)
        fileMenu.addMenu(projectMenu)
        
        aboutMenu = menubar.addMenu('关于(&A)')
        aboutMenu.addAction(aboutAuthor)
        aboutMenu.addAction(aboutQt)
        pass
    #显示子窗口
    def showChild(self):
        self.child_window = Child()
        #需要在主窗口中再为子窗口的按钮绑定方法, 不然参数传不过来
        self.child_window.bt1.clicked.connect(self.getChildSignal_single)    
        self.child_window.show()
        #print(self.child_window.signalTuple)
    #监听窗口关闭事件, 抛出询问对话框 (可以同时把子窗口关闭)
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No) #最后一个是默认按钮
        if reply == QMessageBox.Yes:
            event.accept()
            if self.child_window != None:
                self.child_window.close()
        else:
            event.ignore()
    #接收从子窗口传递的信号
    #该方法运行结束后进行UI界面初始化
    def getChildSignal_single(self):
        signalTuple = (self.child_window.bvEdit.text(), self.child_window.QualityEdit.currentText(), self.child_window.path)
        self.signalTuple_single = signalTuple
        self.child_window.close()
        
        #self.InitUI_single()
        print(self.signalTuple_single)
        self.InitUI_single()
        
        return signalTuple

        
        pass
    #开始爬虫
    def StartSpider(self):
        if self.centralUI_single.getTotal == True:
            print(self.TotalInfo)
            for key, value in self.TotalInfo.items():
                print('{key}:{value}'.format(key= key, value= value))
        #self.video.MergeOutput(Quality= self.quality, path= self.outputPath, pbar= True)
        #self.centralUI_single
        
        #BV1BB4y1G7g2
        self.pbar = QProgressBar(self)
        self.pbar.setMinimum(0)
        self.pbar.setMaximum(100)
        
        downloadLabel = QLabel()
        downloadLabel.setText('Downloading video:')
        self.centralUI_single.flayout_left.addRow(downloadLabel, self.pbar)
        """
        进度条测试
        注意:   当使用setValue方法时, 进度条并不会实时更新, 而是一直占用线程. 
                只有调用 app.exec_() 方法时才会更新
                需要与setValue 同时使用 QtGui.QApplication.processEvents() 事件处理器来实现更新 
        for i in range(100):
            time.sleep(0.1)
            self.pbar.setValue(i)
            QApplication.processEvents() 
        """
        #实现爬虫的代码
        self.video.mergeOutput_UIpbar(self.pbar, Quality= self.quality, path= self.outputPath, label= downloadLabel)
        
        overLabel = QLabel()
        overLabel.setText('Download completed')
        self.centralUI_single.flayout_left.addWidget(overLabel)
        
        self.pbar.reset()
        QApplication.processEvents()
        pass

#QMainWindow自带layout, 实际排版的时候不能加入布局, 而是加入中心组件
class CentralWidget_single(QWidget):
    def __init__(self, window: Example):
        super().__init__()
        id_ = id(window)
        #通过id获取主窗口对象, 可以藉此操作主窗口
        self.window: Example = get_object(id_)
        self.getTotal = False
        self.Init_UI()
    def Init_UI(self):
        #以下是构造画面
        #创建Frame
        self.fra_left = QFrame()
        self.fra_left.setLineWidth(3)
        self.fra_left.setFrameShape(QFrame.Panel)
        self.fra_left.setFrameShadow(QFrame.Raised)
        
        self.fra_right = QFrame()
        self.fra_right.setLineWidth(5)
        self.fra_right.setFrameShape(QFrame.Panel)
        self.fra_right.setFrameShadow(QFrame.Raised)
        
        
        self.flayout_left = QFormLayout()
        """
        self.pbar = QProgressBar(self)
        self.pbar.setMinimum(0)
        self.pbar.setMaximum(100)
        self.pbar.setValue(50)
        self.flayout_left.addRow('测试:', self.pbar)
        """
        
        #以下是右边框架的
        hbox = QHBoxLayout()
        #第二个参数是设置比例(即伸缩量), 不设置则默认为零, 框架不显示
        hbox.addWidget(self.fra_left, 5) 
        hbox.addWidget(self.fra_right, 3)
        
        # 开始：
        wlayout_right = QVBoxLayout() # 全局布局（1个）：水平
        
        self.hlayout = QHBoxLayout() # 局部布局（4个）：水平、竖直、网格、表单
        self.vlayout = QVBoxLayout()
        self.flayout_msg = QFormLayout()
        self.flayout = QFormLayout()
        
        size = (350,220)
        lbl = QLabel()
        lbl.resize(*size)
        #创建QImage对象, 缩放等操作需要在image上进行, 对标签对象设置大小是无用的, 设置自适应也不行
        #封面输出路径
        facePath = self.window.facePath + 'face.jpg'
        print(facePath)
        image = QImage(facePath)
        #统一使用size变量设置大小
        image = image.scaled(*size)                                
        lbl.setPixmap(QPixmap.fromImage(image))
        
        #name author aid cid introduction
        #放置图片
        self.hlayout.addStretch(2)
        self.hlayout.addWidget(lbl,12)
        
        #放置开关按钮和复选框
        bt_start = QPushButton('Start')
        bt_start.clicked.connect(self.window.StartSpider)
        #复选框
        checkbox_msg = QCheckBox('Require basic information of the video?')
        checkbox_msg.stateChanged.connect(self.getTotalInfoStatus)
        
        self.vlayout.addWidget(bt_start)
        self.vlayout.addWidget(checkbox_msg)
        
        BasicInfo = self.window.BasicInfo
        
        title_label = QLabel('Title:\t')
        title = QLabel(BasicInfo['title'])
        title.setWordWrap(True)
        author_label = QLabel('Author:\t')
        author = QLabel(BasicInfo['authorID'])
        aid_label = QLabel('aid:\t')
        aid = QLabel(BasicInfo['aid'])
        cid_label = QLabel('cid:\t')
        cid = QLabel(BasicInfo['cid'])
        self.flayout.addRow(title_label, title)
        self.flayout.addRow(aid_label, aid)
        self.flayout.addRow(cid_label, cid)
        self.flayout.addRow(author_label, author)
        
        #将局部布局设为部件类的对象, 这就不会出现布局冲突问题
        hwg = QWidget()
        vwg = QWidget()
        fwg_msg = QWidget()
        fwg = QWidget()
        hwg.setLayout(self.hlayout) 
        vwg.setLayout(self.vlayout)
        fwg_msg.setLayout(self.flayout_msg)
        fwg.setLayout(self.flayout)
        
        
        wlayout_right.addWidget(hwg) # 四个部件加至主布局
        wlayout_right.addWidget(vwg)
        wlayout_right.addWidget(fwg_msg)
        wlayout_right.addWidget(fwg)
        
        #如果下方是self.setLayout(wlayout_right)的话就加上这两句
        #rightContainer = QWidget(self.fra_right)
        #rightContainer.setLayout(wlayout_right)
        self.fra_left.setLayout(self.flayout_left)
        self.fra_right.setLayout(wlayout_right)
        self.setLayout(hbox)
    
    def getTotalInfoStatus(self, state):
        if state == QtCore.Qt.Checked:
            self.getTotal = True
        else:
            self.getTotal = False
        pass    
        
    pass

#获取单个视频的子窗口类
class Child(QWidget):
    def __init__(self, parent=None):
        super(Child, self).__init__(parent)
        self.Init_UI()
        self.path = ''
    signal_single = QtCore.pyqtSignal(str, str, str)    
    
    def Init_UI(self):
        self.setGeometry(400,400,500,300)
        self.setWindowTitle('输入参数')
        #嵌套布局
        vbox = QVBoxLayout()
        self.formlayout = QFormLayout()
        
        #为视频质量创建多选栏
        combo = QComboBox(self)
        combo.addItem("360p")
        combo.addItem("480p")
        combo.addItem("720p")
        combo.addItem("1080p")
        combo.addItem("1080p+")
        combo.addItem("4k")
        
        bvLabel = QLabel("bv_id:")
        self.bvEdit = QLineEdit("")
        QualityLabel = QLabel("Quality:")
        self.QualityEdit = combo
        pathLabel = QLabel("Path:")
        self.pathEdit = QPushButton("Select the ouput dir of video")
        self.pathEdit.clicked.connect(self.showDiretDialog)
        
        self.formlayout.addRow(bvLabel, self.bvEdit)
        self.formlayout.addRow(QualityLabel, self.QualityEdit)
        self.formlayout.addRow(pathLabel, self.pathEdit)
        
        self.bt1 = QPushButton('over',self) 
        vbox.addLayout(self.formlayout)
        vbox.addWidget(self.bt1)
        self.setLayout(vbox)
        
        #self.child_window.bt1.clicked.connect(self.child_window.sendTempSignal)
        #self.bt1.clicked.connect(self.sendTempSignal)
    #弹出文件选择对话框
    def showDiretDialog(self):
        fname = QFileDialog.getExistingDirectory(self, 'Open file', '/home')
        self.path = fname + '/'
        #修改按钮文本
        self.pathEdit.setText(self.path)
        return True    
    #槽函数返回值无意义吗? 
    def sendTempSignal(self):
        signalTuple = (self.bvEdit.text(), self.QualityEdit.currentText() , self.path)
        #print(signalTuple)
        #print('1')
        self.signalTuple = signalTuple
        
        self.close()
        return signalTuple
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())