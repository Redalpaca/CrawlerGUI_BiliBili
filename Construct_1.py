from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
import json
import sys
from BiliClass import BiliVideo
import os
import ctypes
#获取原对象
def get_object(object_id):
    return ctypes.cast(object_id, ctypes.py_object).value

#self是主窗口类的实例
class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.InitOriginUI()
        self.child_window = None
        self.signalTuple_single = None
        self.signalTuple_multiple = None
    #搭建空白界面
    def InitOriginUI(self):
        self.setGeometry(300,300,1600,1000)
        self.setWindowTitle('BiliCrawler')
        WindowIcon = QIcon('Project\PyQt5\CrawlerGUI_BiliBili\IconLib\Icon.jpg')
        self.setWindowIcon(WindowIcon)
        #显示状态栏
        self.status()
        #显示主菜单
        self.menu()

        #显示主窗口
        self.show()
    #获取单个视频的总界面
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
    #获取多个视频的总界面
    def InitUI_multiple(self):
        #默认信息输出路径
        self.infoPath = self.outputPath
        self.centralUI_multiple = CentralWidget_multiple(self)
        self.centralUI_multiple.startSignal.connect(self.StartSpider_multiple)
        self.centralUI_multiple.searchSignal.connect(self.searchVideoInfo)
        #在开始爬虫前检查输出路径
        if(not os.path.exists(self.outputPath)):
            self.pathCritical()
        self.setCentralWidget(self.centralUI_multiple)
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
        elif reply == QMessageBox.Retry:
            self.child_window.show()
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
    def bvidCritical_multiple(self):
        msgBox = QMessageBox()
        msgBox.setWindowTitle('BvidError')
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText("The video you select is not exist.")
        msgBox.setStandardButtons(QMessageBox.Ignore)
        msgBox.setDefaultButton(QMessageBox.Ignore)
        reply = msgBox.exec() 
        if reply == QMessageBox.Ignore:
            return False     
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
    def indexCritical(self):
        msgBox = QMessageBox()
        msgBox.setWindowTitle('PathError')
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText("The index you input point to a non-existent video.")
        msgBox.setStandardButtons(QMessageBox.Retry)
        msgBox.setDefaultButton(QMessageBox.Retry)
        reply = msgBox.exec() 
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
        multiAct.triggered.connect(self.showChild_multiple)
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
    #监听窗口关闭事件, 抛出询问对话框 (可以同时把子窗口关闭)
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No) #最后一个是默认按钮
        if reply == QMessageBox.Yes:
            event.accept()
            
            if self.child_window != None:
                self.child_window.close()
            sys.exit() #关闭窗口不意味着进程结束
        else:
            event.ignore()
    #显示子窗口
    def showChild(self):
        self.child_window = Child()
        #需要在主窗口中再为子窗口的按钮绑定方法, 不然参数传不过来
        self.child_window.bt1.clicked.connect(self.getChildSignal_single)    
        self.child_window.show()
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
    #开始爬虫
    def StartSpider_single(self):
        if self.centralUI_single.bt_start.text() == 'Start':
            self.centralUI_single.bt_start.setText('Pause')
        else:
            self.centralUI_single.bt_start.setText('Start')
        
        #self.video.MergeOutput(Quality= self.quality, path= self.outputPath, pbar= True)
        #self.centralUI_single
        
        #BV1BB4y1G7g2
        
        self.pbar = QProgressBar(self)
        self.pbar.setMinimum(0)
        #self.pbar.setMaximum(100)
        
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
        self.video.mergeOutput_UIpbar(self.pbar, Quality= self.quality, path= self.outputPath,
                                      label= downloadLabel, speedLabel= self.centralUI_single.speed)
        
        downloadLabel.setText('Download over.')
        self.pbar.reset()
        QApplication.processEvents()
        
        #self.centralUI_single.flayout_left.removeRow(1)
        #BV1BB4y1G7g2 BV1uS4y1w7cQ
        #Show the total information of the video.
        if self.centralUI_single.getTotal == True:
            print(self.TotalInfo)
            for key, value in self.TotalInfo.items():
                #print('{key}:{value}'.format(key= key, value= value))
                valueLabel = QLabel()
                valueLabel.setText(str(value))
                self.centralUI_single.flayout_left.addRow(key, valueLabel)
            self.statusBar().showMessage('Download completed with total information.')
        else: self.statusBar().showMessage('Download completed.')
        
        pass
    #显示子窗口_多视频爬虫
    def showChild_multiple(self):
        self.child_window_multiple = Child_Multi(self)
        self.child_window_multiple.multiSignal.connect(self.getChildSignal_multiple)
        #self.child_window_multiple.bt1.clicked.connect(self.getChildSignal_multiple)    
        self.child_window_multiple.show()
        pass
    def getChildSignal_multiple(self, *args):
        #self.child_window_mutiple.close()
        self.bvidList = args[0]
        self.quality = args[1]
        self.outputPath = args[2]
        self.child_window_multiple.close()
        self.InitUI_multiple()
        pass
    def StartSpider_multiple(self):
        self.centralUI_multiple.createProgressBar()
        self.videoList = []
        path = self.outputPath + str('VideoSave_BiliBili') + '/'
        if(not os.path.exists(path)):
            os.makedirs(path)
         
        for index, bv_id in enumerate(self.bvidList):
            video = BiliVideo(bv_id)
            pbar= self.centralUI_multiple.PBarList[index]
            label= self.centralUI_multiple.pbarLabelList[index]
            self.videoList.append(video)
            if video.res.status_code == 200:
                #此处是在右上角方框显示信息
                info = str(index + 1)+ ' ' + bv_id + '  title: %s'%(video.title)
                self.centralUI_multiple.labelList[index].setText(info)
                
                #The following is the body of video crawler
                video.mergeOutput_UIpbar(pbar= pbar, Quality= self.quality,
                                         path= path, label= label, speedLabel= self.centralUI_multiple.speed)
                label.setText('Video %s download Over.'%str(index + 1))
                pbar.reset()
                #self.centralUI_multiple.PBarList[index].setValue(0)
            else:
                info = str(index + 1) + ' Illigal bv_id.'
                self.centralUI_multiple.labelList[index].setText(info)
                label.setText('Video %s: non-existent.'%str(index + 1))
                #pbar.setValue(0) BV1r14y1W7pv,BV1sG4y1k7iF, asdfasdfaasdfasdfasdf, BV1r14y1W7pv
            self.centralUI_multiple.progress.setText('%d/%d'%(index+1, len(self.bvidList)))
            pass
        
        print('test')
        if self.centralUI_multiple.getTotal:
            self.saveVideoInfo()
            pass
        pass
    def searchVideoInfo(self, videoIndex: str):
        #for i in self.videoList:
        #    print(i.bvid)
        index = int(videoIndex) - 1
        if  index < 0 or index >= len(self.bvidList):
            self.indexCritical()
            return
        #如果BiliVideo对象已经保存了, 则在内存中直接获取信息, 效率很高
        try:
            tempVideo = self.videoList[index]
        except:
            tempVideo = BiliVideo(self.bvidList[index])
        
        if tempVideo.res.status_code != 200:
            self.bvidCritical_multiple()
            return
        self.child_window_info = Child_multiple_info(self, tempVideo)
        self.child_window_info.show()
        pass
    def saveVideoInfo(self):
        infoList = []
        for video in self.videoList:
            video: BiliVideo
            if video.res.status_code == 200:
                tempDict = video.TotalInfo()
                tempDict['legal'] = True
                infoList.append(tempDict)
            else:
                infoList.append(dict(legal = False))
        jsonStr = json.dumps(infoList)
        with open(self.infoPath + 'video.json', 'w') as f:
            f.write(jsonStr)
        pass

#QMainWindow自带layout, 实际排版的时候不能加入布局, 而是加入中心组件
#选择单个视频时中心组件的构造类
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
        self.fra_right.setLineWidth(3)
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
        hbox.addWidget(self.fra_left, 2) 
        hbox.addWidget(self.fra_right, 1)
        
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
        self.bt_start = QPushButton('Start')
        self.bt_start.clicked.connect(self.window.StartSpider_single)
        #复选框
        self.checkbox_msg = QCheckBox('Require basic information of the video?')
        self.checkbox_msg.stateChanged.connect(self.getTotalInfoStatus)
        
        self.vlayout.addWidget(self.bt_start)
        self.vlayout.addWidget(self.checkbox_msg)
        
        BasicInfo = self.window.BasicInfo
        
        speed_label = QLabel('Speed:\t')
        self.speed = QLabel('0.00 MB/s')
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
        self.flayout.addRow(speed_label, self.speed)
        
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
#获取单个视频定位信息的子窗口类
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
        self.signalTuple = signalTuple
        self.close()
        return signalTuple

#选择多个视频时中心组件的构造类
class CentralWidget_multiple(QWidget):
    startSignal = QtCore.pyqtSignal()
    searchSignal = QtCore.pyqtSignal(str)
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
        self.fra_right.setLineWidth(3)
        self.fra_right.setFrameShape(QFrame.Panel)
        self.fra_right.setFrameShadow(QFrame.Raised)
        
        self.flayout_left = QFormLayout()
        
        #以下是右边框架的
        hbox = QHBoxLayout()
        #第二个参数是设置比例(即伸缩量), 不设置则默认为零, 框架不显示
        hbox.addWidget(self.fra_left, 2) 
        hbox.addWidget(self.fra_right, 1)
        
        # 开始：
        wlayout_right = QVBoxLayout() # 右侧全局布局（1个）：水平
        
        topFiller_right = QWidget()
        #防止过小无法显示
        topFiller_right.setMinimumSize(1200, 400)
        fflayout_inner_right = QFormLayout()
        topFiller_right.setLayout(fflayout_inner_right)
        self.labelList = []
        for index, bv_id in enumerate(self.window.bvidList):
            bv_id = bv_id.replace('\'','').replace(' ','')
            self.window.bvidList[index] = bv_id
            testLabel = QLabel()
            #testLabel.setMinimumWidth(300)
            testLabel.setText(str(index+1) + ' ' + bv_id)
            self.labelList.append(testLabel)
            fflayout_inner_right.addRow(testLabel)
            pass
        self.scroll_right = QScrollArea()
        self.scroll_right.setWidget(topFiller_right)
        wlayout_right.addWidget(self.scroll_right)
        
        
        self.vlayout = QVBoxLayout()
        self.flayout_msg = QFormLayout()
        self.flayout = QFormLayout()
        
        #Select the index of the video which you wanna get info from.
        self.indexCombo = QComboBox()
        self.indexCombo.addItems([str(i) for i in range(1, len(self.window.bvidList)+1)])
        self.bt_infoSearch = QPushButton()
        self.bt_infoSearch.setText('Search')
        self.bt_infoSearch.clicked.connect(self.sendSearchSignal)
        self.flayout_msg.addRow(self.indexCombo, self.bt_infoSearch)
                
        #放置开关按钮和复选框
        self.bt_start = QPushButton('Start')
        #self.bt_start.clicked.connect(self.window.StartSpider_multiple)
        self.bt_start.clicked.connect(self.sendStartSignal)
        #复选框
        self.checkbox_msg = QCheckBox('Require basic information of the video?')
        self.checkbox_msg.setChecked(False)
        self.checkbox_msg.stateChanged.connect(self.getTotalInfoStatus)
        
        self.vlayout.addWidget(self.bt_start)
        self.vlayout.addWidget(self.checkbox_msg)
        
        #BasicInfo = self.window.BasicInfo
        
        speed_label = QLabel('Speed:\t')
        self.speed = QLabel('0.00 MB/s')
        self.speed.setWordWrap(True)
        progress_label = QLabel('Progress:\t')
        self.progress = QLabel('0/0')
        aid_label = QLabel('aid:\t')
        aid = QLabel('test')
        cid_label = QLabel('cid:\t')
        cid = QLabel('test')
        self.flayout.addRow(speed_label, self.speed)
        self.flayout.addRow(progress_label, self.progress)
        self.flayout.addRow(aid_label, aid)
        self.flayout.addRow(cid_label, cid)
        
        #将局部布局设为部件类的对象, 这就不会出现布局冲突问题
        hwg = QWidget()
        vwg = QWidget()
        fwg_msg = QWidget()
        fwg = QWidget()
        
        #hwg.setLayout(fflayout_inner_right) 
        vwg.setLayout(self.vlayout)
        fwg_msg.setLayout(self.flayout_msg)
        fwg.setLayout(self.flayout)
        #wlayout_right.addWidget(hwg) # 四个部件加至主布局
        wlayout_right.addWidget(vwg)
        wlayout_right.addWidget(fwg_msg)
        wlayout_right.addWidget(fwg)
        #如果下方是self.setLayout(wlayout_right)的话就加上这两句
        #rightContainer = QWidget(self.fra_right)
        #rightContainer.setLayout(wlayout_right)
        self.fra_left.setLayout(self.flayout_left)
        self.fra_right.setLayout(wlayout_right)
        self.setLayout(hbox)
    #复选框控件的槽函数
    def getTotalInfoStatus(self, state):
        if state == QtCore.Qt.Checked:
            self.getTotal = True
            legalDir_bool = self.showDiretDialog()
            if legalDir_bool == False:
                self.showNotDirDialog()
        else:
            self.getTotal = False
            self.checkbox_msg.setChecked(False)
        pass
    #弹出文件选择对话框
    def showDiretDialog(self):
        dirName = QFileDialog.getExistingDirectory(self, 'Select output dir:', '/home')
        #if
        if(not os.path.exists(dirName)):
            return False
        else: 
            self.window.InfoPath = dirName + '/'
        return True
    #弹出未选择目录的警告对话框
    def showNotDirDialog(self):
        msgBox = QMessageBox()
        msgBox.setWindowTitle('PathError')
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText("You have not selected an output path of detail.")
        msgBox.setStandardButtons(QMessageBox.Retry | QMessageBox.Abort)
        msgBox.setDefaultButton(QMessageBox.Retry)
        reply = msgBox.exec() 
        if reply == QMessageBox.Retry:
            #如果选择重试, 则继续self.getTotalInfoStatus内的流程判定
            legalDir_bool = self.showDiretDialog()
            if legalDir_bool == False:
                self.showNotDirDialog()
        else:
            self.checkbox_msg.setChecked(False)
        pass
    #在中心组件中初始化进度条等控件
    def createProgressBar(self):
        createVar = locals()
        self.PBarList = []
        #self.pbar = QProgressBar(self)
        #self.pbar.setMinimum(0)
        
        topFiller_left = QWidget()
        #注意设置, 否则进度条会变得很短
        topFiller_left.setMinimumSize(800, 100)
        fflayout_inner_left = QFormLayout()
        topFiller_left.setLayout(fflayout_inner_left)

        self.pbarLabelList = []
        #批量创建进度条变量
        for index, bv_id in enumerate(self.window.bvidList):
            #testLabel = QLabel()
            #testLabel.setText(bv_id)
            #fflayout_inner_left.addRow(testLabel)
            createVar['pbar_'+ str(index)] = QProgressBar(self.window)
            createVar['pbar_'+ str(index)].setMinimum(0)
            '1234,123,15,43,123411,4124135315,d,sf,sads,f,24,5t,dasf,das,431,5,df,a,34,513,rfdeD,1234,123,15,43,123411,4124135315,d,sf,sads,f,24,5t,dasf,das,431,5,df,a,34,513,rfdeD,1234,123,15,43,123411,4124135315,d,sf,sads,f,24,5t,dasf,das,431,5,df,a,34,513,rfdeD,1234,123,15,43,123411,4124135315,d,sf,sads,f,24,5t,dasf,das,431,5,df,a,34,513,rfdeD'
            #createVar['pbar_'+ str(index)].setMaximum(100)
            #createVar['pbar_'+ str(index)].setValue(100)
            self.PBarList.append(createVar['pbar_'+ str(index)])
            label = QLabel()
            label.setText(str(index))
            self.pbarLabelList.append(label)
            fflayout_inner_left.addRow(label, self.PBarList[index])
            QApplication.processEvents()
            pass
        self.scroll_left = QScrollArea()
        self.scroll_left.setWidget(topFiller_left)
        self.flayout_left.addWidget(self.scroll_left)
        pass
    #使用自定义信号有助于结构化构造
    def sendStartSignal(self):
        self.startSignal.emit()
    #send searching signal for video info.
    def sendSearchSignal(self):
        self.searchSignal.emit(self.indexCombo.currentText())
        pass
    pass
#获取多个视频定位信息的子窗口类
class Child_Multi(QWidget):
    multiSignal = QtCore.pyqtSignal([list, str, str])
    def __init__(self, window: Example):
        super(Child_Multi, self).__init__()
        id_ = id(window)
        #通过id获取主窗口对象, 可以藉此操作主窗口
        self.window: Example = get_object(id_)
        self.Init_UI()
        self.path = ''
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
        
        bvLabel = QLabel("IdList:")
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
        self.bt1.clicked.connect(self.emitSignal)
         
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
    #用自定义信号的方法在不同窗口传递信号
    def emitSignal(self):
        bvList = self.bvEdit.text().split(',')
        self.multiSignal[list, str, str].emit(bvList, self.QualityEdit.currentText(), self.path)
        pass
    pass
#直接显示视频信息的窗口类
class Child_multiple_info(QWidget):
    def __init__(self, window: Example, video: BiliVideo):
        super(Child_multiple_info, self).__init__()
        id_ = id(window)
        #通过id获取主窗口对象, 可以藉此操作主窗口
        self.window: Example = get_object(id_)
        self.video = video
        self.facePath = 'E:\CodeField_1\Code_Python_E\Project\PyQt5\CrawlerGUI_BiliBili\IconLib\\'
        self.Init_UI()
        
    def Init_UI(self):
        self.move(400,400)
        self.setMinimumWidth(800)
        self.setMinimumHeight(1000)
        print('yes')
        #Total layout
        self.setWindowTitle('VideoInformation')
        self.flayout = QFormLayout(self)
        
        #The following is to set face of the video
        self.video.GetFace(path= self.facePath)
        size = (350,220)
        lbl = QLabel()
        lbl.resize(*size)
        facePath = self.facePath + 'face.jpg'
        image = QImage(facePath)
        image = image.scaled(*size)                                
        lbl.setPixmap(QPixmap.fromImage(image))
        imageBox = QHBoxLayout()
        imageBox.addStretch(1)
        imageBox.addWidget(lbl, 3)
        imageWB = QWidget()
        imageWB.setLayout(imageBox)
        self.flayout.addWidget(imageWB)
        
        topFiller = QWidget()
        topFiller.setMinimumSize(500, 600)
        fflayout = QFormLayout()
        topFiller.setLayout(fflayout)
        
        #add title to info layout
        titleLbl = QLabel()
        titleLbl.setText(self.video.title)
        fflayout.addRow('title', titleLbl)
        for key, value in self.video.TotalInfo().items():
            #print('{key}:{value}'.format(key= key, value= value))
            valueLabel = QLabel()
            valueLabel.setText(str(value))
            fflayout.addRow(key, valueLabel)
        
        scroll_1 = QScrollArea()
        scroll_1.setWidget(topFiller)
        self.flayout.addWidget(scroll_1)
        
        self.setLayout(self.flayout)
        #BV16F411j7QC
        pass
    pass

#选择用户时中心组件的构造类
class CentralWidget_user(QWidget):
    
    pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())