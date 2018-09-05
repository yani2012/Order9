# -*- coding: utf-8 -*-
import common
import log_helper
import qt_helper
import time_condition_helper
import pandas as pd
import time
import itertools

def get_pool_name(page_index):
    if page_index == 0:#vol_px
        return qt_helper.table_name_1stUp_limit_pool

    elif page_index == 1:#up_limit
        return qt_helper.table_name_up_limit_pool
    elif page_index == 2:#up_limit
        return qt_helper.table_name_1stnew_up_limit_pool

def update_time_range(context, pool_name):
    context.qt_begin_time.setTime(time_condition_helper.run_time_dict[pool_name][0][0])
    context.qt_end_time.setTime(time_condition_helper.run_time_dict[pool_name][0][1])
    context.lineEdit_maxTradeCount.setText(str(qt_helper.max_trade_count_dict[pool_name]))

def buy_up_limit_work(context, data_cache_manager, pool_item_cache, pool_name):
    for tempUser in pool_item_cache: 
        try:
            if tempUser not in data_cache_manager.accounts.keys():
                #log_helper.warn('account {0} not exist for pool {1}'.format(tempUser, pool_name))
                continue

            if data_cache_manager.exceed_max_trade_count(tempUser, pool_name):
                log_helper.warn('{0} exceed max trade times at pool {1}'.format(tempUser, pool_name))
                time.sleep(15)
                continue

            posLimit = common.get_total_max_position_percent(data_cache_manager.accounts[tempUser]['posLimit'])
            usable = data_cache_manager.accounts[tempUser]['usable']
            asset = data_cache_manager.accounts[tempUser]['asset']
            poolItemList = list(pool_item_cache[tempUser].values())
            total_pos = 0.0
            for poolItem in poolItemList:
                if poolItem.is_sent_order:
                    continue      

                pos = common.percent2float(poolItem.pos)              
                total_pos += pos
                if not common.check_position_limit(data_cache_manager.accounts, tempUser, to_buy_percent=total_pos, max_limit=posLimit):
                    poolItem.state = u'仓位超{0}'.format(posLimit)
                    continue

                if poolItem.stock not in context.market_depths_df.index:
                    log_helper.warn('failed to get market data for stock:{0}'.format(poolItem.stock))
                    continue

                market_data = context.market_depths_df.ix[poolItem.stock]
                pre_close = market_data['pre_close']
                if pre_close <= 0:
                    continue

                high_limit = round(pre_close*1.1, 2)
                if common.is_open_high_limit(market_data):
                    continue

                last_px = market_data['last_px']
                if last_px < (high_limit-0.01):
                    continue
                    
                price = high_limit
                vol = common.get_order_vol(asset, pos, price)
                poolItem.is_sent_order = True
                state = data_cache_manager.accounts[tempUser]['tradeApi'].buy(poolItem.stock, price, vol)
                log_helper.info('[{0}]{1} buy {2} at {3} @ {4} state:{5}'.format(tempUser, pool_name, poolItem.stock, price, vol, state))
                state = state.splitlines()
                state = [i.split('\t') for i in state]
                if len(state) > 1:
                    poolItem.state = str(pd.DataFrame(state[1:], columns=state[0]).iloc[0,0])          
                    data_cache_manager.orderid2pooldict[common.get_order_key(tempUser, poolItem.state)] = pool_name
                    data_cache_manager.add_orderid_to_dict(pool_name, poolItem.stock, poolItem.state, tempUser)

        except Exception,e:
                log_helper.error(u'[error]请检查{0}买入条件单是否正确:{1}'.format(pool_name, e))

def stop_loss_check(poolItem, market_data, mdHelper=None):
    last_px = round(market_data['last_px'],2)
    pre_close = market_data['pre_close']
    up_limit = round(market_data['pre_close']*1.1, 2)
    high = round(market_data['high'], 2)

    need_trigger = False
    if poolItem.trigger_condition == u'01涨停打开卖出':
        if last_px < up_limit and high == up_limit:
            need_trigger = True
    elif poolItem.trigger_condition == u'02当日亏损5%卖出':
        if last_px < (pre_close*0.95):
            need_trigger = True
    elif poolItem.trigger_condition == u'03涨停回撤5%卖出':
        if last_px < (up_limit*0.95) and high == up_limit:
            need_trigger = True
    elif poolItem.trigger_condition == u'04高点回撤5%卖出':
        if last_px < (high*0.95):
            need_trigger = True
    elif poolItem.trigger_condition == u'05尾盘未涨停卖出':
        now = pd.Timestamp('today')
        minutesNo = now.hour*60 + now.minute
        if minutesNo >=895:
            if last_px < up_limit:
                need_trigger = True
    elif poolItem.trigger_condition == u'06尾盘破MA5卖出':
        now = pd.Timestamp('today')
        minutesNo = now.hour*60 + now.minute
        if minutesNo >=895:
            ma5 = mdHelper.getMa(poolItem.stock, 5)
            if last_px < ma5:
                need_trigger = True
    elif poolItem.trigger_condition == u'07上涨7%卖出':
        if last_px > (pre_close*1.07):
            need_trigger = True
    elif poolItem.trigger_condition == u'08即刻卖出':
        if last_px > 0:
            need_trigger = True

    return need_trigger

def sell_work(context, data_cache_manager, pool_item_cache, pool_name, trigger_condition_check, mdHelper=None):
    for tempUser in pool_item_cache:     
        poolItemList = list(pool_item_cache[tempUser].values())
        for poolItem in  itertools.chain.from_iterable(poolItemList):
            if poolItem.is_sent_order:
                continue
            vol = int(poolItem.vol)
            marketData = context.market_depths_df.ix[poolItem.stock]
            last_px = marketData['last_px']
            if last_px <= 0:
                continue

            need_trigger = False
            pre_close = marketData['pre_close']
            if not trigger_condition_check(poolItem, marketData, mdHelper=mdHelper):
                continue
            
            positions = data_cache_manager.accounts[tempUser]['position'].set_index('StockCode')
            if poolItem.stock not in positions.index:
                log_helper.warn('no position on {0} when stop loss'.format(poolItem.stock))
                continue

            available_sell_vol = positions['CoverableSize'][poolItem.stock]
            if available_sell_vol == 0:
                log_helper.warn('0 position on {0}  when stop loss'.format(poolItem.stock))
                continue
            if vol > available_sell_vol > 0:
                vol = available_sell_vol
                
            if poolItem.waySell == u'追五挂单':
                order_price = common.get_bid5_price(marketData)
                poolItem.is_sent_order = True
                state = data_cache_manager.accounts[tempUser]['tradeApi'].sell(poolItem.stock, order_price, vol) 
                log_helper.info('[user:{0}][{1} sell stock({2}) at price:{3}]@{4}. state:{5}'.format(tempUser, pool_name, poolItem.stock, order_price, vol, state))
                state = state.splitlines()
                state = [i.split('\t') for i in state]
                if len(state) > 1:
                    poolItem.state = str(pd.DataFrame(state[1:], columns=state[0]).iloc[0,0])