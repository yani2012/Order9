# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'condition_order_201712.ui'
# Created by: PyQt4 UI code generator 4.11.4
# WARNING! All changes made in this file will be lost!
from PyQt4 import QtCore, QtGui
import qt_helper
from qt_helper import (
    normal_font,
    bold_font,
    init_button,
    init_combox,
    init_checkbox,
    init_table_widget, 
    init_label,
    init_line_edit,
    _fromUtf8,
    _translate,
)

sizeNum = 1.18 ##页面倍数调整
buy_condtion_tab_with = 530*sizeNum   #卖出界面
buy_pool_table_with = 590*sizeNum
buy_condtion_tab_height = 390*sizeNum
buy_condtion_tab_top_margin = 40*sizeNum
buy_pool_table_height = 590*sizeNum
sell_condtion_tab_with = 700*sizeNum
sell_pool_table_with = 690*sizeNum

class MainWindow(object):
    def setupUi(self, MainWindow):
        global sizeNum
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1210 * sizeNum, 812 * sizeNum)
        MainWindow.setAutoFillBackground(False)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))

#-------------------------------------form row 1账户管理界面-----------------------------------------------------------------------------------------
        self.groupBox_accoutManage = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_accoutManage.setGeometry(QtCore.QRect(1* sizeNum, 5 * sizeNum, 1200 * sizeNum,260 * sizeNum))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_accoutManage.sizePolicy().hasHeightForWidth())
        self.groupBox_accoutManage.setSizePolicy(sizePolicy)
        self.groupBox_accoutManage.setObjectName(_fromUtf8("groupBox_accoutManage"))
        self.comboBox_broker = init_combox(self.groupBox_accoutManage, 'comboBox_broker', qt_helper.brokers, QtCore.QRect(80 * sizeNum, 30 * sizeNum, 120 * sizeNum,21 * sizeNum))      ##开户券商

        self.lineEdit_comPwd = QtGui.QLineEdit(self.groupBox_accoutManage) 
        self.lineEdit_comPwd.setGeometry(QtCore.QRect(80 * sizeNum, 120 * sizeNum, 120 * sizeNum,21 * sizeNum))        #通讯密码输入框
        self.lineEdit_comPwd.setText(_fromUtf8(""))
        self.lineEdit_comPwd.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEdit_comPwd.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_comPwd.setObjectName(_fromUtf8("lineEdit_comPwd"))
        self.lineEdit_trdPwd = QtGui.QLineEdit(self.groupBox_accoutManage)
        self.lineEdit_trdPwd.setGeometry(QtCore.QRect(80 * sizeNum, 90 * sizeNum, 120 * sizeNum,21 * sizeNum))         #密码输入框
        self.lineEdit_trdPwd.setText(_fromUtf8(""))
        self.lineEdit_trdPwd.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEdit_trdPwd.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_trdPwd.setObjectName(_fromUtf8("lineEdit_trdPwd"))
        self.lineEdit_userName = QtGui.QLineEdit(self.groupBox_accoutManage)
        self.lineEdit_userName.setGeometry(QtCore.QRect(80 * sizeNum, 60 * sizeNum, 120 * sizeNum,21 * sizeNum))       #用户账号输入框
        self.lineEdit_userName.setText(_fromUtf8(""))
        self.lineEdit_userName.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_userName.setObjectName(_fromUtf8("lineEdit_userName"))
        label_left = 25
        self.label_username = QtGui.QLabel(self.groupBox_accoutManage)
        self.label_username.setGeometry(QtCore.QRect(label_left * sizeNum, 65 * sizeNum, 54 * sizeNum,12 * sizeNum))   ##用户名标签
        self.label_username.setObjectName(_fromUtf8("label_username"))
        self.label_trdPwd = QtGui.QLabel(self.groupBox_accoutManage)
        self.label_trdPwd.setGeometry(QtCore.QRect(label_left * sizeNum, 95 * sizeNum, 54 * sizeNum,12 * sizeNum))     ##密码标签
        self.label_trdPwd.setObjectName(_fromUtf8("label_trdPwd"))
        self.label_comPwd = QtGui.QLabel(self.groupBox_accoutManage)
        self.label_comPwd.setGeometry(QtCore.QRect(label_left * sizeNum, 125 * sizeNum, 54 * sizeNum,12 * sizeNum))    ##通讯密码标签
        self.label_comPwd.setObjectName(_fromUtf8("label_comPwd"))
        self.label_posLimit = QtGui.QLabel(self.groupBox_accoutManage)
        self.label_posLimit.setGeometry(QtCore.QRect(label_left * sizeNum, 155 * sizeNum, 54 * sizeNum,12 * sizeNum))  ##仓位限制
        self.label_posLimit.setObjectName(_fromUtf8("label_posLimit"))

        self.horizontalSlider_posLimit = QtGui.QSlider(self.groupBox_accoutManage)
        self.horizontalSlider_posLimit.setGeometry(QtCore.QRect(80 * sizeNum, 150 * sizeNum, 90 * sizeNum,19 * sizeNum))
        self.horizontalSlider_posLimit.setMaximum(10)
        self.horizontalSlider_posLimit.setSingleStep(1)
        self.horizontalSlider_posLimit.setPageStep(1)
        self.horizontalSlider_posLimit.setValue(5)
        self.horizontalSlider_posLimit.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_posLimit.setObjectName(_fromUtf8("horizontalSlider_posLimit"))                           ##仓位滚动条

        self.lineEdit_posLimit = QtGui.QLineEdit(self.groupBox_accoutManage)
        self.lineEdit_posLimit.setGeometry(QtCore.QRect(170 * sizeNum, 150 * sizeNum, 30 * sizeNum,21 * sizeNum))      ## 仓位上限数字显示
        self.lineEdit_posLimit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_posLimit.setObjectName(_fromUtf8("lineEdit_posLimit"))

        self.pushButton_addAcc = QtGui.QPushButton(self.groupBox_accoutManage)
        self.pushButton_addAcc.setGeometry(QtCore.QRect(80 * sizeNum, 180 * sizeNum, 120 * sizeNum,30 * sizeNum))
        self.pushButton_addAcc.setObjectName(_fromUtf8("pushButton_addAcc"))                                           ##加入账户按钮

        self.pushButton_save = QtGui.QPushButton(self.groupBox_accoutManage)
        self.pushButton_save.setGeometry(QtCore.QRect(420 * sizeNum, 220 * sizeNum, 60 * sizeNum,26 * sizeNum))       ##保存按钮
        self.pushButton_save.setObjectName(_fromUtf8("pushButton_save"))
        self.pushButton_load = QtGui.QPushButton(self.groupBox_accoutManage)
        self.pushButton_load.setGeometry(QtCore.QRect(485 * sizeNum, 220 * sizeNum, 60 * sizeNum,26 * sizeNum))       ##载入按钮
        self.pushButton_load.setObjectName(_fromUtf8("pushButton_load"))
        self.pushButton_delAcc = QtGui.QPushButton(self.groupBox_accoutManage)
        self.pushButton_delAcc.setGeometry(QtCore.QRect(550 * sizeNum, 220 * sizeNum, 60 * sizeNum,26 * sizeNum))
        self.pushButton_delAcc.setObjectName(_fromUtf8("pushButton_delAcc"))                                          ##删除账户
        self.pushButton_refreshAcc = QtGui.QPushButton(self.groupBox_accoutManage)
        self.pushButton_refreshAcc.setGeometry(QtCore.QRect(615 * sizeNum, 220 * sizeNum, 60 * sizeNum,26 * sizeNum))
        self.pushButton_refreshAcc.setObjectName(_fromUtf8("pushButton_refreshAcc"))                                  ##刷新按钮
        self.lineEdit_curAcc = QtGui.QLineEdit(self.groupBox_accoutManage)
        self.lineEdit_curAcc.setGeometry(QtCore.QRect(210 * sizeNum, 220 * sizeNum, 80 * sizeNum,20 * sizeNum))
        self.lineEdit_curAcc.setText(_fromUtf8(""))
        self.lineEdit_curAcc.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_curAcc.setObjectName(_fromUtf8("lineEdit_curAcc"))                                              #选择账户
        #self.lineEdit_curPosLimit = QtGui.QLineEdit(self.groupBox_accoutManage)
        #self.lineEdit_curPosLimit.setGeometry(QtCore.QRect(260 * sizeNum, 220 * sizeNum, 45 * sizeNum,20 * sizeNum))
        #self.lineEdit_curPosLimit.setText(_fromUtf8(""))
        #self.lineEdit_curPosLimit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        #self.lineEdit_curPosLimit.setObjectName(_fromUtf8("lineEdit_curPosLimit"))
        self.lineEdit_curAsset = QtGui.QLineEdit(self.groupBox_accoutManage)
        self.lineEdit_curAsset.setGeometry(QtCore.QRect(295 * sizeNum, 220 * sizeNum, 50 * sizeNum, 20 * sizeNum))
        self.lineEdit_curAsset.setText(_fromUtf8(""))
        self.lineEdit_curAsset.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_curAsset.setObjectName(_fromUtf8("lineEdit_curAsset"))

        self.lineEdit_curUsable = QtGui.QLineEdit(self.groupBox_accoutManage)
        self.lineEdit_curUsable.setGeometry(QtCore.QRect(350 * sizeNum, 220 * sizeNum, 50 * sizeNum,20 * sizeNum))
        self.lineEdit_curUsable.setText(_fromUtf8(""))
        self.lineEdit_curUsable.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_curUsable.setObjectName(_fromUtf8("lineEdit_curUsable"))

#-------------------------------------for  row2  账户信息显示栏-----------------------------------------------------
        self.qtable_accounts = QtGui.QTableWidget(self.groupBox_accoutManage)
        self.qtable_accounts.setGeometry(QtCore.QRect(210 * sizeNum, 8 * sizeNum, 465* sizeNum,200 * sizeNum))        ##账户列表栏
        init_table_widget(qt_helper.table_name_accounts, self.qtable_accounts)
        self.qtable_positions = QtGui.QTableWidget(self.groupBox_accoutManage)
        self.qtable_positions.setGeometry(QtCore.QRect(690 * sizeNum, 8 * sizeNum, 500 * sizeNum,200 * sizeNum))      ##持仓信息栏
        init_table_widget(qt_helper.table_name_positions, self.qtable_positions)

#-------------------------------------form row 3-自动交易界面----------------------------------------------------------------------------------------
        self.groupBox_4 = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_4.setGeometry(QtCore.QRect(1 * sizeNum, 288 * sizeNum, 1200 * sizeNum, buy_condtion_tab_height))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.tabWidget_conditions = QtGui.QTabWidget(self.groupBox_4)
        self.tabWidget_conditions.setEnabled(True)
        self.tabWidget_conditions.setGeometry(QtCore.QRect(2* sizeNum, buy_condtion_tab_top_margin, 535 * sizeNum, buy_condtion_tab_height))

        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.tabWidget_conditions.setFont(font)
        self.tabWidget_conditions.setObjectName(_fromUtf8("tabWidget_conditions"))

        begin_time = QtCore.QTime(9, 31)
        self.qt_begin_time = QtGui.QDateTimeEdit(begin_time, self.groupBox_4)
        self.qt_begin_time.setGeometry(QtCore.QRect(50*sizeNum, 5 * sizeNum, 60 * sizeNum,23 * sizeNum))
        self.qt_begin_time.setObjectName(_fromUtf8("qt_begin_time"))
        self.qt_begin_time.setDisplayFormat('H:mm')
        self.qt_begin_time.setTime(begin_time)

        end_time = QtCore.QTime(14, 50)
        self.qt_end_time = QtGui.QDateTimeEdit(end_time, self.groupBox_4)
        self.qt_end_time.setGeometry(QtCore.QRect(115*sizeNum, 5 * sizeNum, 60 * sizeNum,23 * sizeNum))
        self.qt_end_time.setObjectName(_fromUtf8("qt_end_time"))
        self.qt_end_time.setDisplayFormat('H:mm')
        self.qt_end_time.setTime(end_time)

        self.pushButton_changeTimeRange = QtGui.QPushButton(self.groupBox_4)
        self.pushButton_changeTimeRange.setGeometry(QtCore.QRect(190*sizeNum, 5 * sizeNum, 70 * sizeNum,23 * sizeNum))
        self.pushButton_changeTimeRange.setObjectName(_fromUtf8("pushButton_changeTimeRange"))
        self.pushButton_changeTimeRange.setText(u'修改时间范围')

        self.lineEdit_maxTradeCount = QtGui.QLineEdit(self.groupBox_4)
        self.lineEdit_maxTradeCount.setGeometry(QtCore.QRect(270 * sizeNum, 5 * sizeNum, 25 * sizeNum,20 * sizeNum))
        self.lineEdit_maxTradeCount.setObjectName(_fromUtf8("lineEdit_maxTradeCount"))

        self.pushButton_changeMaxTradeTimes = QtGui.QPushButton(self.groupBox_4)
        self.pushButton_changeMaxTradeTimes.setGeometry(QtCore.QRect(300*sizeNum, 5 * sizeNum, 70 * sizeNum,23 * sizeNum))
        self.pushButton_changeMaxTradeTimes.setObjectName(_fromUtf8("pushButton_changeMaxTradeTimes"))
        self.pushButton_changeMaxTradeTimes.setText(u'最大成交次数')

        self.pushButton_importStocks = QtGui.QPushButton(self.groupBox_4)
        self.pushButton_importStocks.setGeometry(QtCore.QRect(buy_pool_table_with-210*sizeNum, 5 * sizeNum, 75 * sizeNum,23 * sizeNum))
        self.pushButton_importStocks.setObjectName(_fromUtf8("pushButton_importStocks"))
        self.pushButton_importStocks.setText(u'导入股票')

        self.pushButton_clearAll = QtGui.QPushButton(self.groupBox_4)
        self.pushButton_clearAll.setGeometry(QtCore.QRect(buy_pool_table_with-130*sizeNum, 5 * sizeNum, 75 * sizeNum,23 * sizeNum))
        self.pushButton_clearAll.setObjectName(_fromUtf8("pushButton_clearAll"))
        self.pushButton_clearAll.setText(u'清除所有')
		
###############消息提示############################################################################################
        self.label_res = init_label(self.groupBox_4, 'label_res', u'消息提示:',  QtCore.QRect(700*sizeNum, 15 * sizeNum, 65 * sizeNum, 23 * sizeNum), font=bold_font)
        self.label_res.setAlignment(QtCore.Qt.AlignRight)
        self.label_result = init_label(self.groupBox_4, 'label_result', u'',  QtCore.QRect(780*sizeNum, 15 * sizeNum, 630 * sizeNum, 23 * sizeNum), font=bold_font)
        self.label_result.setAlignment(QtCore.Qt.AlignLeft)

#----------------------------------tabpage_1st_limit----- 一板池###########################################
        self.tabpage_1st_limit = QtGui.QWidget()
        self.tabpage_1st_limit.setObjectName(_fromUtf8("tabpage_1st_limit"))
        self.pushButton_commitVPBuy = QtGui.QPushButton(self.tabpage_1st_limit)
        self.pushButton_commitVPBuy.setGeometry(QtCore.QRect(150 * sizeNum, 30 * sizeNum, 75 * sizeNum,23 * sizeNum))
        self.pushButton_commitVPBuy.setObjectName(_fromUtf8("pushButton_commitVPBuy"))
        self.comboBox_posVPBuy = init_combox(self.tabpage_1st_limit, 'comboBox_posVPBuy', qt_helper.position_percents, QtCore.QRect(78 * sizeNum, 30 * sizeNum, 71 * sizeNum,22 * sizeNum))
        self.label_1stlimit_position = init_label(self.tabpage_1st_limit, 'label_1stlimit_position', u"仓位", QtCore.QRect(72 * sizeNum, 10 * sizeNum, 71 * sizeNum,21 * sizeNum))
        self.tableWidget_VPBuy = QtGui.QTableWidget(self.tabpage_1st_limit)
        self.tableWidget_VPBuy.setGeometry(QtCore.QRect(0 * sizeNum, 60 * sizeNum, buy_pool_table_with,301 * sizeNum))
        self.lineEdit_stkVPBuy = init_line_edit(self.tabpage_1st_limit, 'lineEdit_stkVPBuy', QtCore.QRect(10 * sizeNum, 30 * sizeNum, 61 * sizeNum,20 * sizeNum))
        self.label_1stlimit_stock = init_label(self.tabpage_1st_limit, 'label_1stlimit_stock', u"股票代码", QtCore.QRect(10 * sizeNum, 10 * sizeNum, 61 * sizeNum,16 * sizeNum))
        init_table_widget(qt_helper.table_name_1stUp_limit_pool, self.tableWidget_VPBuy)

#---------------tabpage_New --- 次新池界面####################################################
        self.tabpage_New = QtGui.QWidget()
        self.tabpage_New.setObjectName(_fromUtf8("tabpage_New"))
        self.pushButton_commitNewBuy = QtGui.QPushButton(self.tabpage_New)
        self.pushButton_commitNewBuy.setGeometry(QtCore.QRect(150 * sizeNum, 30 * sizeNum, 75 * sizeNum,23 * sizeNum))
        self.pushButton_commitNewBuy.setObjectName(_fromUtf8("pushButton_commitNewBuy"))
        self.comboBox_posNewBuy = init_combox(self.tabpage_New, 'comboBox_posNewBuy', qt_helper.position_percents,QtCore.QRect(78 * sizeNum, 30 * sizeNum, 71 * sizeNum,22 * sizeNum))
        self.label_new_stock = init_label(self.tabpage_New, 'label_new_stock', u'股票代码',  QtCore.QRect(10 * sizeNum, 10 * sizeNum, 61 * sizeNum,16 * sizeNum))
        self.lineEdit_stkNewBuy = init_line_edit(self.tabpage_New, 'lineEdit_stkNewBuy', QtCore.QRect(10 * sizeNum, 30 * sizeNum, 61 * sizeNum,20 * sizeNum))
        self.label_new_position = init_label(self.tabpage_New, 'label_new_position', u'仓位',  QtCore.QRect(72 * sizeNum, 10 * sizeNum, 71 * sizeNum,21 * sizeNum))
        self.tableWidget_NewBuy = QtGui.QTableWidget(self.tabpage_New) 
        self.tableWidget_NewBuy.setGeometry(QtCore.QRect(0 * sizeNum, 60 * sizeNum, buy_pool_table_with,301 * sizeNum))
        init_table_widget(qt_helper.table_name_1stnew_up_limit_pool, self.tableWidget_NewBuy)

#--------------------tabpage_UpLimit --- 涨停池界面############################################
        self.tabpage_UpLimit = QtGui.QWidget()
        self.tabpage_UpLimit.setObjectName(_fromUtf8("tabpage_UpLimit"))
        self.pushButton_commitUpLimitBuy = QtGui.QPushButton(self.tabpage_UpLimit)
        self.pushButton_commitUpLimitBuy.setGeometry(QtCore.QRect(150 * sizeNum, 30 * sizeNum, 75 * sizeNum,23 * sizeNum))
        self.pushButton_commitUpLimitBuy.setObjectName(_fromUtf8("pushButton_commitUpLimitBuy"))                               #确认按钮
        self.comboBox_posUpLimitBuy = init_combox(self.tabpage_UpLimit, 'comboBox_posUpLimitBuy', qt_helper.position_percents,QtCore.QRect(78 * sizeNum, 30 * sizeNum, 71 * sizeNum,22 * sizeNum))       #仓位选择下拉框
        self.label_UpLimit = init_label(self.tabpage_UpLimit, 'label_UpLimit', u'仓位', QtCore.QRect(72 * sizeNum, 10 * sizeNum, 71 * sizeNum,21 * sizeNum))                                              #仓位标签
        self.tableWidget_UpLimitBuy = QtGui.QTableWidget(self.tabpage_UpLimit)
        self.tableWidget_UpLimitBuy.setGeometry(QtCore.QRect(0 * sizeNum, 60 * sizeNum, buy_pool_table_with,301 * sizeNum))    #股票列表
        self.lineEdit_stkUpLimitBuy = init_line_edit(self.tabpage_UpLimit, 'lineEdit_stkUpLimitBuy', QtCore.QRect(10 * sizeNum, 30 * sizeNum, 61 * sizeNum,20 * sizeNum))            #股票代码输入框
        self.label_UpLimit_stock = init_label(self.tabpage_UpLimit, 'label_UpLimit_stock', u'股票代码', QtCore.QRect(10 * sizeNum, 10 * sizeNum, 61 * sizeNum,16 * sizeNum))          #股票代码标签
        init_table_widget(qt_helper.table_name_up_limit_pool, self.tableWidget_UpLimitBuy)

##############################################################################################################
        self.tabWidget_conditions.addTab(self.tabpage_1st_limit, _fromUtf8(""))        #涨停一
        self.tabWidget_conditions.addTab(self.tabpage_UpLimit, _fromUtf8(""))      #涨停二
        self.tabWidget_conditions.addTab(self.tabpage_New, _fromUtf8(""))          #次新池

#-----------------------------------卖出界面-----------------------------############################################
        self.tabWidget_Trading = QtGui.QTabWidget(self.groupBox_4)
        self.tabWidget_Trading.setGeometry(QtCore.QRect(buy_condtion_tab_with+15, 50 * sizeNum, sell_condtion_tab_with,401 * sizeNum))
        self.tabWidget_Trading.setObjectName(_fromUtf8("tabWidget_Trading"))
#---------------------------------tabPage_StopLoss 卖出界面---------------------##########################################################
        self.tabPage_StopLoss = QtGui.QWidget()
        self.tabPage_StopLoss.setObjectName(_fromUtf8("tabPage_StopLoss"))
        self.groupBox_sellCondition = QtGui.QGroupBox(self.tabPage_StopLoss)
        self.groupBox_sellCondition.setGeometry(QtCore.QRect(10 * sizeNum, 10 * sizeNum, 1021 * sizeNum, 361 * sizeNum)) #卖出界面总大小
        self.groupBox_sellCondition.setObjectName(_fromUtf8("groupBox_sellCondition"))
        self.label_stkSell = QtGui.QLabel(self.groupBox_sellCondition)
        self.label_stkSell.setGeometry(QtCore.QRect(20 * sizeNum, 30 * sizeNum, 54 * sizeNum, 12 * sizeNum))
        self.label_stkSell.setObjectName(_fromUtf8("label_stkSell"))
        self.lineEdit_stkSell = QtGui.QLineEdit(self.groupBox_sellCondition)
        self.lineEdit_stkSell.setGeometry(QtCore.QRect(10 * sizeNum, 50 * sizeNum, 71 * sizeNum, 20 * sizeNum))      #卖出界面股票代码输入框
        self.lineEdit_stkSell.setText(_fromUtf8(""))
        self.lineEdit_stkSell.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.lineEdit_stkSell.setObjectName(_fromUtf8("lineEdit_stkSell"))
        self.label_volSell = QtGui.QLabel(self.groupBox_sellCondition)
        self.label_volSell.setGeometry(QtCore.QRect(100 * sizeNum, 30 * sizeNum, 54 * sizeNum, 12 * sizeNum))
        self.label_volSell.setObjectName(_fromUtf8("label_volSell"))

        self.comboBox_volStopLoss = init_combox(self.groupBox_sellCondition, 'comboBox_volStopLoss',                 #卖出数量
                                                qt_helper.sell_percents,
                                                QtCore.QRect(90 * sizeNum, 50 * sizeNum, 71 * sizeNum, 20 * sizeNum))

        self.label_priceSell = QtGui.QLabel(self.groupBox_sellCondition)
        self.label_priceSell.setGeometry(QtCore.QRect(185 * sizeNum, 55 * sizeNum, 54 * sizeNum, 12 * sizeNum))     #触发方式标签
        self.label_priceSell.setObjectName(_fromUtf8("label_priceSell"))

        self.label_waySell = QtGui.QLabel(self.groupBox_sellCondition)
        self.label_waySell.setGeometry(QtCore.QRect(420 * sizeNum, 30 * sizeNum, 54 * sizeNum, 12 * sizeNum))      #挂单方式标签
        self.label_waySell.setObjectName(_fromUtf8("label_waySell"))

        self.combox_trigger_condition = init_combox(self.groupBox_sellCondition, 'combox_trigger_condition',
                                                    qt_helper.stop_max_drawdown,
                                                    QtCore.QRect(235 * sizeNum, 50 * sizeNum, 160 * sizeNum,        #触发卖出条件列表
                                                                 20 * sizeNum))

        self.pushButton_addSellCondition = QtGui.QPushButton(self.groupBox_sellCondition)
        self.pushButton_addSellCondition.setGeometry(
            QtCore.QRect(490 * sizeNum, 30 * sizeNum, 75 * sizeNum, 41 * sizeNum))                                  #卖出条件按钮
        self.pushButton_addSellCondition.setObjectName(_fromUtf8("pushButton_addSellCondition"))
        self.comboBox_waySell = QtGui.QComboBox(self.groupBox_sellCondition)
        self.comboBox_waySell.setGeometry(QtCore.QRect(410 * sizeNum, 50 * sizeNum, 71 * sizeNum, 21 * sizeNum))    #挂单方式选择框
        self.comboBox_waySell.setObjectName(_fromUtf8("comboBox_waySell"))
        # self.comboBox_waySell.addItem(_fromUtf8(""))
        self.comboBox_waySell.addItem(_fromUtf8(""))
        self.tableWidget_stopLoss = QtGui.QTableWidget(self.groupBox_sellCondition)                                 #卖出界面列表
        self.tableWidget_stopLoss.setGeometry(
            QtCore.QRect(0 * sizeNum, 90 * sizeNum, sell_pool_table_with, 271 * sizeNum))
        init_table_widget(qt_helper.table_name_stop_loss, self.tableWidget_stopLoss)
        self.tabWidget_Trading.addTab(self.tabPage_StopLoss, _fromUtf8(""))
 
#----------------------------------------------------成交界面------------------
        self.tabPage_Orders = QtGui.QWidget()
        self.tabPage_Orders.setObjectName(_fromUtf8("tabPage_Orders"))
        self.groupBox = QtGui.QGroupBox(self.tabPage_Orders)
        self.groupBox.setGeometry(QtCore.QRect(0 * sizeNum, 10 * sizeNum, 1011 * sizeNum, 361 * sizeNum))            #成交列表挂单界面大小
        self.groupBox.setObjectName(_fromUtf8("groupBox"))

        self.qtable_orders = QtGui.QTableWidget(self.groupBox)
        self.qtable_orders.setGeometry(QtCore.QRect(0 * sizeNum, 20 * sizeNum, sell_pool_table_with, 361 * sizeNum))  #成交列表大小
        init_table_widget(qt_helper.table_name_orders, self.qtable_orders)
        self.tabWidget_Trading.addTab(self.tabPage_Orders, _fromUtf8(""))
        MainWindow.setCentralWidget(self.centralwidget)

#--------------------------TABLE按键焦点-----------------
        self.retranslateUi(MainWindow)
        self.tabWidget_conditions.setCurrentIndex(0)
        self.tabWidget_Trading.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.comboBox_broker, self.lineEdit_userName)
        MainWindow.setTabOrder(self.lineEdit_userName, self.lineEdit_trdPwd)
        MainWindow.setTabOrder(self.lineEdit_trdPwd, self.lineEdit_comPwd)
        MainWindow.setTabOrder(self.lineEdit_comPwd, self.lineEdit_posLimit)
        MainWindow.setTabOrder(self.lineEdit_posLimit, self.pushButton_addAcc)
        MainWindow.setTabOrder(self.pushButton_addAcc, self.qtable_accounts)
        MainWindow.setTabOrder(self.qtable_accounts, self.pushButton_delAcc)
        MainWindow.setTabOrder(self.pushButton_delAcc, self.tabWidget_Trading)
        MainWindow.setTabOrder(self.tabWidget_Trading, self.lineEdit_stkSell)
        MainWindow.setTabOrder(self.lineEdit_stkSell, self.comboBox_volStopLoss)
        MainWindow.setTabOrder(self.comboBox_volStopLoss, self.combox_trigger_condition)
        MainWindow.setTabOrder(self.combox_trigger_condition, self.comboBox_waySell)
        MainWindow.setTabOrder(self.comboBox_waySell, self.pushButton_addSellCondition)
        MainWindow.setTabOrder(self.pushButton_addSellCondition, self.tableWidget_stopLoss)
		
#----------------------------------主要UI界面-----------------------
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.groupBox_accoutManage.setTitle(_translate("MainWindow", "账户管理", None))
        self.label_comPwd.setText(_translate("MainWindow", "通讯密码", None))
        self.label_username.setText(_translate("MainWindow", "证券账号", None))
        self.label_trdPwd.setText(_translate("MainWindow", "交易密码", None))
        self.label_posLimit.setText(_translate("MainWindow", "仓位上限", None))
        self.pushButton_delAcc.setText(_translate("MainWindow", "删除账户", None))
        self.lineEdit_posLimit.setText(_translate("MainWindow", "0%", None))
        self.pushButton_save.setText(_translate("MainWindow", "保存", None))
        self.pushButton_load.setText(_translate("MainWindow", "载入", None))
        self.pushButton_addAcc.setText(_translate("MainWindow", "加入账户", None))
        self.pushButton_refreshAcc.setText(_translate("MainWindow", "刷新", None))
        self.groupBox_4.setTitle(_translate("MainWindow", "自动交易", None))
		  
        #############################次新池相关#############################################
        self.pushButton_commitNewBuy.setText(_translate("MainWindow", "确认", None))
        self.tabWidget_conditions.setTabText(self.tabWidget_conditions.indexOf(self.tabpage_New), _translate("MainWindow", "次新池", None))

        #############################一板池相关#############################################
        self.pushButton_commitVPBuy.setText(_translate("MainWindow", "确认", None))
        self.tabWidget_conditions.setTabText(self.tabWidget_conditions.indexOf(self.tabpage_1st_limit), _translate("MainWindow", "一板池", None))
		
        #############################涨停池相关#############################################
        self.pushButton_commitUpLimitBuy.setText(_translate("MainWindow", "确认", None))
        self.tabWidget_conditions.setTabText(self.tabWidget_conditions.indexOf(self.tabpage_UpLimit), _translate("MainWindow", "涨停池", None))

        ####################################止损卖出相关###################################################################
        self.groupBox_sellCondition.setTitle(_translate("MainWindow", "卖出条件", None))
        self.label_stkSell.setText(_translate("MainWindow", "股票代码", None))
        self.label_volSell.setText(_translate("MainWindow", "卖出数量", None))
        self.label_priceSell.setText(_translate("MainWindow", "触发方式", None))
        self.label_waySell.setText(_translate("MainWindow", "挂单方式", None))
        self.pushButton_addSellCondition.setText(_translate("MainWindow", "卖出条件", None))
        #self.comboBox_waySell.setItemText(0, _translate("MainWindow", "市价挂单", None))
        self.comboBox_waySell.setItemText(0, _translate("MainWindow", "追五挂单", None))
        self.tabWidget_Trading.setTabText(self.tabWidget_Trading.indexOf(self.tabPage_StopLoss), _translate("MainWindow", "卖出设置", None))
        #####################################################################################################
        self.groupBox.setTitle(_translate("MainWindow", "挂单", None))
        self.tabWidget_Trading.setTabText(self.tabWidget_Trading.indexOf(self.tabPage_Orders), _translate("MainWindow", "成交列表", None))
