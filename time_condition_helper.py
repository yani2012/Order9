# -*- coding: utf-8 -*-
from PyQt4.QtCore import QTime
import qt_helper
import time
import log_helper

run_time_dict = {
    qt_helper.table_name_1stUp_limit_pool:[(QTime(9, 26), QTime(9, 59))],
    qt_helper.table_name_up_limit_pool:[(QTime(9, 26), QTime(9, 55))],
    qt_helper.table_name_1stnew_up_limit_pool:[(QTime(9, 26), QTime(9, 57))],
}

class TimeConditionHelper(object):
    def __init__(self):
        self.tradable = False

    def set_tradable(self, tradable):
        self.tradable = tradable

    def check_time(self, name):
        if not self.tradable:
            return False

        if name not in run_time_dict.keys():
            return False

        now = QTime.currentTime()
        time_range_arr = run_time_dict[name]
        for item in time_range_arr:
            if now>item[0] and now <item[1]:
                #log_helper.info('now:{0}, begin:{1}, end:{2}'.format(now, item[0], item[1]))
                return True

        return False

    #通用运行时间为9：26-14：56
    def check_common_buy_time(self):
        if not self.tradable:
            return 0

        now = time.strftime("%H:%M:%S", time.localtime())
        if now < '09:26:00':
            return 0
        elif now > '14:56:10':
            return -1
        
        return 1