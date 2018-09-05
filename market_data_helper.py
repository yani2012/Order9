# -*- coding: utf-8 -*-
import requests
import pandas as pd
import datetime
import TradeX
import log_helper
import time
import sys
import numpy as np
import time
import common

market_server_addresses = [
    ('221.231.141.60', 7709),
    ('101.227.73.20', 7709),
    ('59.173.18.140', 7709),
    ('60.28.23.80', 7709),
    ('218.60.29.136', 7709),
    ('140.207.219.18', 7709),
    ('122.192.35.44', 7709),
    ('121.14.110.200', 443),
    ('121.14.110.201', 80),
    ('113.105.73.88', 7709),
    ('58.249.119.236', 7709),
    ('119.147.212.81', 7709),
    ('183.232.161.155', 7709),
    ('61.135.149.185', 443),
    ('61.135.149.186', 443),
    ('61.135.142.88', 7709),
    ('221.231.141.60', 7709),
    ('61.49.50.190', 7709),
    ('106.120.74.86', 7709),
    ('221.130.42.57', 7709),
    ('116.57.224.5', 7709),
    ('119.147.171.205', 443),
    ('119.147.171.206', 80),
    ('119.147.171.207', 7709),
    ('119.147.164.60', 7709),
    ('114.80.80.222', 7709),
    ('222.73.49.4', 7709),
    ('61.152.249.56', 7709),
    ('182.175.240.156', 7709),
    ('117.184.140.156', 7709),
    ('59.173.18.77', 7709),
    ('218.108.50.178', 7709),
    ('221.194.181.176', 7709),
    ('101.227.73.130', 7709),
    ('119.147.81.37', 7709),
    ]


bars_columns = ['time', 'open', 'close', 'high', 'low', 'vol', 'money']
bars_columns_len = len(bars_columns)
market_depth_columns = ['market','stock_code','active','last_px','pre_close'
                ,'open','high','low','remain1','remain2'
                ,'total_vol','last_qty','total_money','initialtive_buy'
                ,'initialtive_sell','reamin3','remain4','bid1_px','ask1_px'
                ,'bid1_qty','ask1_qty','bid2_px','ask2_px','bid2_qty'
                ,'ask2_qty','bid3_px','ask3_px','bid3_qty','ask3_qty'
                ,'bid4_px','ask4_px','bid4_qty','ask4_qty','bid5_px'
                ,'ask5_px','bid5_qty','ask5_qty','remain5','remain6'
                ,'remain7','remain8','remain9','change_speed','active_ratio']

class MDHelper(object):
    def __init__(self):
        self.real_ma_dict = {}
        self.connect_market_server()

    def connect_market_server(self):
        try_times = 0
        len_market_servers = len(market_server_addresses)
        while try_times<300:
            try_times += 1
            try:
                server_addr = market_server_addresses[try_times%len_market_servers]
                self.clientHq = TradeX.TdxHq_Connect(server_addr[0], server_addr[1])
                log_helper.info('connect hq success')
                break
            except TradeX.TdxHq_error, e:
                log_helper.error("connect hq fail TdxHq_error error: {0}".format(e.message))
                time.sleep(0.5)
            except Exception,e:
                log_helper.error("connect hq fail unkown error: {0}".format(e.message))
                time.sleep(0.5)

        if try_times >= 200:
            log_helper.error("connect hq fail too many times(>=200)")
            sys.exit(-1)


    def get_stock_count(self, market_no):
        errinfo, count = self.clientHq.GetSecurityCount(market_no)
        if errinfo != "":
            log_helper.error(errinfo)
        else:
	        log_helper.info("market no:{0} 股票数量：{1}".format(market_no, count))

    def get_stock_list(self, market_no):
        nStart = 0

        errinfo, count, result = self.clientHq.GetSecurityList(market_no, nStart)
        if errinfo != "":
            log_helper.error(errinfo)
            return
           
        res = result.splitlines()
        for item in res:
            log_helper.info(item)
        res = [stock_code.split('\t')[0] for stock_code in res ]

        #log_helper.info(res[:1500])
        return res[1:]

    def _get_market_no(self, stock_code):
        return (0 if stock_code[0] != '6' else 1)

    def get_bar_df(self, stock_code, start_no, count):
        nCategory = 9
        errinfo, count, result = self.clientHq.GetSecurityBars(nCategory, self._get_market_no(stock_code), stock_code, start_no, count)

        res = result.splitlines()
        res = [i.split('\t') for i in res]
        if len(res) == 1 :
            return None
        return pd.DataFrame([i[:bars_columns_len]for i in res[1:]], columns=bars_columns)


    def getMa(self, stock_code, count):
        bars_df = self.get_bar_df(stock_code, 0, count)
        if bars_df is None:
            return float('nan')

        bars_df_len = len(bars_df)
        if bars_df_len < count:
            count = float(bars_df_len)
        if count< 1:
            count = 1.0

        close_sum = bars_df['close'].astype(float).sum()
        maPx = round(close_sum/count, 2)

        return maPx

    def getMa_real(self, stock_code, count):
        key = '{0}_{1}_real'.format(stock_code, count)
        if key in self.real_ma_dict.keys():
            return self.real_ma_dict[key]

        bars_df = self.get_bar_df(stock_code, 1, count+1)
        if bars_df is None:
            return float('nan')

        bars_df_len = len(bars_df)

        if bars_df_len == count + 1:
            close_series = bars_df['close'].astype(float)
            close_sum_1 = close_series[:-1].sum()
            close_sum_2 = close_series[1:].sum()
            avg1 = close_sum_1/count
            avg2 = close_sum_2/count
            maPx = (avg2 + avg2 - avg1)
            self.real_ma_dict[key] = maPx
            return maPx

        if bars_df_len < count:
            count = float(bars_df_len)
        if count< 1:
            count = 1.0

        close_sum = bars_df['close'].astype(float).sum()
        maPx = round(close_sum/count, 2)
        self.real_ma_dict[key] = maPx
        return maPx

    def get_market_depths(self, stock_list):
        #log_helper.info('-----------begin')
        #log_helper.info('get_market_depths:{0}'.format(stock_list[:10]))
        query_stocks = []
        i = 0
        temp_arr = []
        for item in stock_list:
            i+=1
            temp_arr.append((self._get_market_no(item), item))
            if i%80==0:
                query_stocks.append(temp_arr)
                temp_arr = []
        
        if len(temp_arr) > 0:
            query_stocks.append(temp_arr)

        df_arr = []
        for item in query_stocks:
            errinfo, count, result = self.clientHq.GetSecurityQuotes(item)
            if errinfo != "":
                log_helper.error("GetSecurityQuotes error:{0}".format(errinfo))
                self.connect_market_server()
                continue
        
            res = result.splitlines()
            res = [i.split('\t') for i in res]
            length = min([len(x) for x in res])
            if length == 1:
                continue
             
            df_arr.append(pd.DataFrame([i[:length]for i in res[1:]], columns=market_depth_columns))
        if len(df_arr) == 0:
            return None

        ret_df = pd.concat(df_arr)
        ret_df.set_index('stock_code', inplace=True)
        ret_df[['last_px','pre_close','open','high','low','total_money','bid5_px','ask5_px','bid4_px','ask4_px','bid3_px','ask3_px','bid2_px','ask2_px','bid1_px','ask1_px']]\
                = ret_df[['last_px','pre_close','open','high','low','total_money','bid5_px','ask5_px','bid4_px','ask4_px','bid3_px','ask3_px','bid2_px','ask2_px','bid1_px','ask1_px']].astype(np.float)
        ret_df[['last_qty','total_vol','bid5_qty','ask5_qty','bid4_qty','ask4_qty','bid3_qty','ask3_qty','bid2_qty','ask2_qty','bid1_qty','ask1_qty']]\
                = ret_df[['last_qty','total_vol','bid5_qty','ask5_qty','bid4_qty','ask4_qty','bid3_qty','ask3_qty','bid2_qty','ask2_qty','bid1_qty','ask1_qty']].astype(np.int32)
        len_df = len(ret_df)
        #log_helper.info('-------:{0}'.format(len(ret_df)))

        # strong_stocks = []
        # for i in range(len_df):
        #     row_data = ret_df.iloc[i]
        #     last_px = row_data['last_px']
        #     pre_close = row_data['pre_close']
        #     if last_px <=0 or pre_close <= 0:
        #         continue
        #     change_percent = round(last_px/pre_close, 2)
        #     if change_percent < 1.07:
        #         continue

        #     if row_data['open'] == row_data['low'] == row_data['high']:
        #         continue

        #     strong_stocks.append((ret_df.index[i], [last_px, pre_close, '{0}%'.format((change_percent-1)*100)]))
        
        #log_helper.info('strong stocks:{0}'.format(strong_stocks))
        return ret_df

    def get_minute_data(self, stock_code):
        market_no = self._get_market_no(stock_code)
        errinfo, result = self.clientHq.GetMinuteTimeData(market_no, stock_code)
        log_helper.info('result:{0}'.format(result))

    def filter_df_by_change(self, orig_df, compare_value):
        strong_stocks = []
        if orig_df is None:
            return strong_stocks

        for i in range(len(orig_df)):
            row_data = orig_df.iloc[i]
            last_px = row_data['last_px']
            pre_close = row_data['pre_close']
            open_px = row_data['open']
            if last_px <=0 or pre_close <= 0:
                if compare_value == 0.9:
                    strong_stocks.append((orig_df.index[i], [last_px, pre_close, '0.0%']))
                continue
            change_percent = round(last_px/pre_close, 4)
            if change_percent < compare_value:
                continue

            if open_px == row_data['low'] == row_data['high']:
                continue
            if compare_value != 0.9:
                if open_px >= round(pre_close*1.1 - 0.01, 2):
                    continue

            strong_stocks.append((orig_df.index[i], [last_px, pre_close, '{0}%'.format((change_percent-1)*100)]))
        
        #log_helper.info('strong stocks:{0}'.format(strong_stocks))
        return strong_stocks

def dailyH10(code):
    symbol = ('sh' if code[0] == '6' else 'sz') + code
    url = "http://api.finance.ifeng.com/akdaily/?code=%s&type=last"%symbol
    cols = ['date',
             'open',
             'high',
             'close',
             'low',
             'volume',
             'price_change',
             'p_change',
             'ma5',
             'ma10',
             'ma20',
             'v_ma5',
             'v_ma10',
             'v_ma20',
             'turnover']
    data = pd.DataFrame(eval(requests.get(url).text)['record'], columns = cols)
    data = data.sort_values('date', ascending = False).head(10)
    highestHigh = str(round(data['high'].astype(float).max(), 2))
    return(highestHigh)

def getMa(code, nowPrice, maCount):
    symbol = ('sh' if code[0] == '6' else 'sz') + code
    url = "http://api.finance.ifeng.com/akdaily/?code=%s&type=last"%symbol
    cols = ['date',
             'open',
             'high',
             'close',
             'low',
             'volume',
             'price_change',
             'p_change',
             'ma5',
             'ma10',
             'ma20',
             'v_ma5',
             'v_ma10',
             'v_ma20',
             'turnover']
    data = pd.DataFrame(eval(requests.get(url).text)['record'], columns = cols)

    #如果是周末，取5天；如果是工作日取4天同当前求平均
    headLen = 0
    now = datetime.datetime.now()
    weekday = now.weekday()
    #工作日
    if weekday < 5:
        headLen = maCount-1
    #周末
    else:
        headLen = maCount
    data = data.sort_values('date', ascending = False).head(headLen)
    # highestHigh = str(round(data['high'].astype(float).max(), 2))

    theSum = data['close'].astype(float).sum();

    ma = 0
    #工作日
    if weekday < 5:
        ma = (theSum + nowPrice)/(headLen +1)
    #周末
    else:
        ma = theSum/headLen

    return round(ma,2)

if __name__ == '__main__':
    mdHelper = MDHelper()
    mdHelper.get_stock_count(0)
    mdHelper.get_stock_count(1)
    #sz_stock_list = mdHelper.get_stock_list(0)
    #sh_stock_list = mdHelper.get_stock_list(2)
    #mdHelper.dailyH10('300112')
    print('get ma 10:', mdHelper.dailyH10('002813'))
    print('get ma 10:', mdHelper.dailyH10('000717'))
    df = mdHelper.get_market_depths(['300561', '002931'])
    print('is_open_high_limit:', common.is_open_high_limit(df.ix['002931']))
    # print('000509 depth:', df.ix['000509'])
    # print('600519 depth:', df.ix['600519'])
    #mdHelper.get_minute_data('002208')