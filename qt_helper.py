# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QTime
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


normal_font = QtGui.QFont()
normal_font.setPointSize(9)
normal_font.setBold(False)
normal_font.setUnderline(False)
normal_font.setWeight(50)
normal_font.setStrikeOut(False)
normal_font.setKerning(True)

bold_font = QtGui.QFont()
bold_font.setPointSize(11)
bold_font.setBold(True)
bold_font.setUnderline(True)
bold_font.setWeight(65)
bold_font.setStrikeOut(False)
bold_font.setKerning(True)

table_name_accounts = 'qtable_accounts'
table_name_positions = 'qtable_positions'
table_name_orders = 'qtable_orders'

table_name_1stnew_up_limit_pool = 'qttable_1stnew_up_limit_pool'
table_name_up_limit_pool = 'qttable_up_limit_pool'
table_name_1stUp_limit_pool = 'qttable_1st_up_limit_pool'

table_name_stop_loss = 'qtable_stop_loss'
#table_name_max_drawdown = 'qtable_max_drawdown'

max_trade_count_dict = {
    table_name_up_limit_pool:3,
    table_name_1stUp_limit_pool:3,
    table_name_1stnew_up_limit_pool:3,
}
col_names_dict={
    table_name_accounts:['股东名', '券商', '证券账号','仓位上限', '总资产', '可用资金', '仓位比例'],
    table_name_positions:['股票代码', '股票名称', '股票余额', '可用余额', '冻结数量', '买入市值', '总市值', '盈亏','盈亏比例'],
    table_name_orders:['委托时间', '股票代码', '股票名称', '操作', '委托价格', '委托数量', '成交数量', '委托编号'],

    table_name_up_limit_pool:['股票代码', '股票名称', '仓位', '挂单方式', '挂单状态'],
    table_name_1stUp_limit_pool:['股票代码', '股票名称', '仓位', '挂单方式', '挂单状态'],
    table_name_1stnew_up_limit_pool:['股票代码', '股票名称', '仓位', '挂单方式', '挂单状态'],

    table_name_stop_loss:['股票代码', '股票名称', '卖出数量', '触发条件', '挂单方式', '挂单数量', '挂单价格', '成交信息', '挂单状态'],
}

brokers = ['兴业证券', '华泰证券', '中信建投','广发证券', '安信证券', '国联证券'
        , '长城证券', '西南证券', '东海证券', '东莞证券', '红塔证券'
        , '国金证券', '西部证券', '海通证券', '东北证券', '华福证券'
        , '国泰君安', '联储证券', '同信证券', '银河证券', '华西证券']

position_percents=['1%', '2%', '5%', '10%', '20%']
sell_percents=['33%', '50%', '100%']
show_level=['全部','1%', '2%', '3%', '5%', '7%', '10%']

stop_max_drawdown = [u"01涨停打开卖出", u"02当日亏损5%卖出", u"03涨停回撤5%卖出",u"04高点回撤5%卖出", u"05尾盘未涨停卖出", u"06尾盘破MA5卖出", u"07上涨7%卖出", u"08即刻卖出"]

def init_button(parent_control, name, text, position):
    ret = QtGui.QPushButton(parent_control)
    ret.setGeometry(position)
    ret.setObjectName(_fromUtf8(name))
    ret.setText(text)
    return ret

def init_checkbox(parent_control, name, text, position):
    ret = QtGui.QCheckBox(parent_control)
    ret.setGeometry(position)
    ret.setObjectName(_fromUtf8(name))
    ret.setText(text)
    ret.setChecked(True)
    return ret

def init_combox(parent_control, name, text_array, position):
    combox = QtGui.QComboBox(parent_control)
    combox.setGeometry(position)
    combox.setObjectName(_fromUtf8(name))
    for i in range(len(text_array)):
        combox.addItem(_fromUtf8(""))
        combox.setItemText(i, _translate("MainWindow", text_array[i], None))
    return combox

def init_label(parent_control, name, text, position, font=normal_font ):
    label = QtGui.QLabel(parent_control)
    label.setEnabled(True)
    label.setGeometry(position)
    label.setFont(font)
    label.setLineWidth(position.width())
    label.setAlignment(QtCore.Qt.AlignCenter)
    label.setObjectName(_fromUtf8(name))
    label.setText(_translate("MainWindow", text, None))
    return label

def init_line_edit(parent_control, name, pos):
    lineEdit_obj = QtGui.QLineEdit(parent_control)
    lineEdit_obj.setGeometry(pos)
    lineEdit_obj.setObjectName(_fromUtf8(name))
    return lineEdit_obj

def init_table_widget(name, tableWidget, rowNo=20):
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Ignored)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(tableWidget.sizePolicy().hasHeightForWidth())
    tableWidget.setSizePolicy(sizePolicy)

    tableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
    tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
    tableWidget.setObjectName(_fromUtf8(name))

    col_names = col_names_dict[name]
    col_count = len(col_names)
    tableWidget.setColumnCount(col_count)
    tableWidget.setRowCount(rowNo)
    col_width = tableWidget.width()/(col_count+1)
    for i in range(col_count):
        item = QtGui.QTableWidgetItem()
        tableWidget.setHorizontalHeaderItem(i, item)
        tableWidget.setColumnWidth(i, col_width)
        item = tableWidget.horizontalHeaderItem(i)
        item.setText(_translate("MainWindow", col_names[i], None))

    for i in range(rowNo):
        item = QtGui.QTableWidgetItem()
        tableWidget.setVerticalHeaderItem(i, item)
        item = tableWidget.verticalHeaderItem(i)
        item.setText(_translate("MainWindow", '{0}'.format(i+1), None))

def update_position_limit(srouce_slider, target_line_edit):     #仓位限制滑动函数
    value = srouce_slider.value()
    text = str(value*10) +'%'
    target_line_edit.setText(text)


# if __name__ == '__main__':
#     s = 'hello'
#     print('s:', s)
#     s1 = _fromUtf8(s)
#     print('s1:', s1)
#     s2 = s1.toUtf8()
#     print('s2:', s2)

#     s3 = str(unicode(s1.toUtf8(), 'utf-8', 'ignore'))
#     print('s3:', s3)
        