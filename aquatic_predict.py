 # -*- coding: utf-8 -*-
import urllib.request as ur
import urllib.parse as up
import pymysql
import json
from bs4 import BeautifulSoup as BS
import numpy as np
from sklearn.svm import SVR
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
import datetime
import base64
import hashlib

def predict(market_name='佳里', target='吳郭魚', start=90, predict_days=30, C=1e1):
    filename_h = hashlib.md5((market_name+str(target)+str(start)+str(C)+'h').encode('utf-8')).hexdigest()
    filename_m = hashlib.md5((market_name+str(target)+str(start)+str(C)+'m').encode('utf-8')).hexdigest()
    filename_l = hashlib.md5((market_name+str(target)+str(start)+str(C)+'l').encode('utf-8')).hexdigest()
    filename_a = hashlib.md5((market_name+str(target)+str(start)+str(C)+'a').encode('utf-8')).hexdigest()
    prefix = 'plot/'

    api_url = 'http://data.coa.gov.tw/Service/OpenData/FromM/AquaticTransData.aspx'
    amounts = [] 
    high_prices = []
    mid_prices = []
    low_prices = []
    avg_prices = []
    date = []
    day = []
    future_day = []
    future_date = []
    
    intervals = [int((start+predict_days)/10*(i+1))-1 for i in range(10)]
    api = ur.urlopen(api_url + '?' + 'marketname=' + up.quote(market_name) + '&' + 'typename=' + up.quote(target))
    json_data = json.loads(api.read().decode('utf-8'))
    for i, j in enumerate(json_data[0:start]):
        d = j['交易日期']
        dd = datetime.datetime(int(d[0:3])+1911, int(d[3:5]),  int(d[5:7]))
        date.append(dd)
        day.append(start-i)
        amounts.append(j['交易量'])
        avg_prices.append(j['平均價'])
        high_prices.append(j['上價'])
        mid_prices.append(j['中價'])
        low_prices.append(j['下價'])
    
    if len(day) == 0:
        print('Error: No enough data')
        return
    for i in range(predict_days):
        future_day.append(day[0]+i)
        future_date.append(date[0]+datetime.timedelta(days=i))
    
    high_prices.reverse()
    low_prices.reverse()
    mid_prices.reverse()
    avg_prices.reverse()
    day.reverse()
    date.reverse()
    date += future_date
    day = np.array(day).reshape(-1, 1)
    future_day = np.array(future_day).reshape(-1, 1)
    svr_rbf_h = SVR(kernel='rbf', C=C)
    svr_rbf_m = SVR(kernel='rbf', C=C)
    svr_rbf_l = SVR(kernel='rbf', C=C)
    svr_rbf_a = SVR(kernel='rbf', C=C)
    y_rbf_h = svr_rbf_h.fit(day, high_prices).predict(day)
    y_rbf_m = svr_rbf_m.fit(day, mid_prices).predict(day)
    y_rbf_l = svr_rbf_l.fit(day, low_prices).predict(day)
    y_rbf_a = svr_rbf_a.fit(day, avg_prices).predict(day)
    predict_result_a = svr_rbf_a.predict(future_day)
    predict_result_h = svr_rbf_m.predict(future_day)
    predict_result_l = svr_rbf_l.predict(future_day)
    predict_result_m = svr_rbf_m.predict(future_day)

    lw = 2 
    plt.scatter(day, avg_prices, color='darkorange', label='data')
    plt.plot(day, y_rbf_a, color='navy', lw=lw, label=u'近似曲線')
    plt.plot(future_day, predict_result_a, color='r', lw=lw, label=u'預測')
    plt.xticks(intervals, [date[i].strftime('%m/%d') for i in intervals])
    plt.xlabel('data')
    plt.ylabel(u'價格')
    plt.title(u'預測與實際誤差')
    plt.legend()
    plt.savefig(prefix + filename_a+'.png')
    plt.clf();

    plt.scatter(day, high_prices, color='darkorange', label='data')
    plt.plot(day, y_rbf_h, color='navy', lw=lw, label=u'近似曲線')
    plt.plot(future_day, predict_result_h, color='r', lw=lw, label=u'預測')
    plt.xticks(intervals, [date[i].strftime('%m/%d') for i in intervals])
    plt.xlabel('data')
    plt.ylabel(u'價格')
    plt.title(u'預測與實際誤差')
    plt.legend()
    plt.savefig(prefix + filename_h+'.png')
    plt.clf();

    plt.scatter(day, mid_prices, color='darkorange', label='data')
    plt.plot(day, y_rbf_m, color='navy', lw=lw, label=u'近似曲線')
    plt.plot(future_day, predict_result_m, color='r', lw=lw, label=u'預測')
    plt.xticks(intervals, [date[i].strftime('%m/%d') for i in intervals])
    plt.xlabel('data')
    plt.ylabel(u'價格')
    plt.title(u'預測與實際誤差')
    plt.legend()
    plt.savefig(prefix + filename_m+'.png')
    plt.clf();

    plt.scatter(day, low_prices, color='darkorange', label='data')
    plt.plot(day, y_rbf_l, color='navy', lw=lw, label=u'近似曲線')
    plt.plot(future_day, predict_result_l, color='r', lw=lw, label=u'預測')
    plt.xticks(intervals, [date[i].strftime('%m/%d') for i in intervals])
    plt.xlabel('data')
    plt.ylabel(u'價格')
    plt.title(u'預測與實際誤差')
    plt.legend()
    plt.savefig(prefix + filename_l+'.png')
    return {
        "上價": prefix + filename_h+'.png', 
        "中價": prefix + filename_m+'.png', 
        "下價": prefix + filename_l+'.png', 
        "平均價": prefix + filename_a+'.png' 
    }

if __name__ == '__main__':
    predict()
