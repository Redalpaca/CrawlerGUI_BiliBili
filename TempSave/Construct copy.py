
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
import sys

#self是主窗口类的实例
class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.InitOriginUI()
        self.child_window = None
        
    def InitOriginUI(self):
        self.setGeometry(300,300,400,300)
        self.setWindowTitle('菜单')

        #显示状态栏
        self.status()
        #显示主菜单
        self.menu()

        self.bt1 = QPushButton('修改姓名',self)
        self.bt1.move(150,150)
        self.bt1.clicked.connect(self.showDialog)
        
        
        
        #显示主窗口
        self.show()
    
    def showDialog(self):
        sender = self.sender()
        if sender == self.bt1:
            text, ok = QInputDialog.getText(self, '测试输入框', '请随意输入：')
            if ok:
                self.showChild()
                pass
        
        pass
    
    def status(self):
        self.statusBar().showMessage('创建新项目以继续..')
        pass
    
    #菜单的构建是自底向上的, 需要先从子菜单开始构建
    def menu(self):
        
        
        iconPath = ''
        #iconPath = 'E:\CodeField_1\Code_Python_E\Project\PyQt5\IconLib\exit.jpg'
        exitAct = QAction(QIcon(iconPath), '退出(&E)', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('退出程序')
        exitAct.triggered.connect(qApp.quit)
        
        #创建多级子菜单
        projectMenu = QMenu('创建项目', self)
        singleAct = QAction(QIcon(),'获取单个视频(&S)', self)
        singleAct.triggered.connect(self.showChild)
        
        multiAct = QAction('获取多个视频(&M)', self)
        
        projectMenu.addAction(singleAct)
        projectMenu.addAction(multiAct)
        
        
        
        #创建菜单栏
        menubar = self.menuBar()
        #文件菜单
        fileMenu = menubar.addMenu('文件(&F)')
        fileMenu.addAction(exitAct)
        fileMenu.addMenu(projectMenu)
        pass

    def showChild(self):
        self.child_window = Child()
        #需要在主窗口中再为子窗口的按钮绑定方法, 不然参数传不过来
        self.child_window.bt1.clicked.connect(self.getChildSignal_single)    
        self.child_window.show()
        #print(self.child_window.signalTuple)
        
        
    
    #监听窗口关闭事件(可以同时把子窗口关闭)
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
    def getChildSignal_single(self):
        signalTuple = (self.child_window.bvEdit.text(), self.child_window.QualityEdit.text(), self.child_window.pathEdit.text())
        self.signalTuple = signalTuple
        self.child_window.close()
        
        print(self.signalTuple)
        
        return signalTuple

        
        pass
 
class Child(QWidget):
    def __init__(self, parent=None):
        super(Child, self).__init__(parent)
        self.Init_UI()
        
    signal_single = QtCore.pyqtSignal(str, str, str)    
    
    def Init_UI(self):
        self.setGeometry(300,300,300,200)
        self.setWindowTitle('输入参数')
        #嵌套布局
        vbox = QVBoxLayout()
        formlayout = QFormLayout()
        
        bvLabel = QLabel("bv_id:")
        self.bvEdit = QLineEdit("")
        QualityLabel = QLabel("Quality:")
        self.QualityEdit = QLineEdit("")
        pathLabel = QLabel("Path:")
        self.pathEdit = QLineEdit("")
        
        formlayout.addRow(bvLabel, self.bvEdit)
        formlayout.addRow(QualityLabel, self.QualityEdit)
        formlayout.addRow(pathLabel, self.pathEdit)
        
        self.bt1 = QPushButton('over',self) 
        vbox.addLayout(formlayout)
        vbox.addWidget(self.bt1)
        self.setLayout(vbox)
        
        #self.child_window.bt1.clicked.connect(self.child_window.sendTempSignal)
        #self.bt1.clicked.connect(self.sendTempSignal)
        
    #槽函数返回值无意义吗? 
    def sendTempSignal(self):
        signalTuple = (self.bvEdit.text(), self.QualityEdit.text(), self.pathEdit.text())
        #print(signalTuple)
        #print('1')
        self.signalTuple = signalTuple
        
        self.close()
        return signalTuple
   
        

    def close(self):
        self.setParent(None)
        self.deleteLater()
        return super(Child, self).close()
    
    
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())