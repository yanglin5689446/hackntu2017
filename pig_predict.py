 # -*- coding: utf-8 -*-
import urllib.request as ur
import urllib.parse as up
import pymysql
import json
from bs4 import BeautifulSoup as BS
import numpy as np
from sklearn.svm import SVR
import matplotlib.pyplot as plt
import matplotlib
import time
import datetime
import base64
import hashlib

def predict(market_name='台中市', target_level="規格豬(75公斤以上)", start=360, predict_days=30, C=1e1):
    filename = hashlib.md5((market_name+str(target_level)+str(start)+str(C)).encode('utf-8')).hexdigest()
    prefix = 'plot/'

    api_url = 'http://data.coa.gov.tw/Service/OpenData/FromM/AnimalTransData.aspx'
    amounts = [] 
    prices = []
    date = []
    day = []
    future_day = []
    future_date = []
    
    intervals = [int((start+predict_days)/10*(i+1))-1 for i in range(10)]
    api = ur.urlopen(api_url + '?' + 'marketname=' + up.quote(market_name)) 
    json_data = json.loads(api.read().decode('utf-8'))
    for i, j in enumerate(json_data[0:start]):
        d = j['交易日期']
        dd = datetime.datetime(int(d[0:3])+1911, int(d[3:5]),  int(d[5:7]))
        date.append(dd)
        day.append(start-i)
        amounts.append(j[target_level + '-頭數'])
        prices.append(j[target_level + '-平均價格'])
    
    for i in range(predict_days):
        future_day.append(day[0]+i)
        future_date.append(date[0]+datetime.timedelta(days=i))
    
    prices.reverse()
    day.reverse()
    date.reverse()
    date += future_date
    day = np.array(day).reshape(-1, 1)
    future_day = np.array(future_day).reshape(-1, 1)
    svr_rbf = SVR(kernel='rbf', C=C)
    y_rbf = svr_rbf.fit(day, prices).predict(day)
    predict_result = svr_rbf.predict(future_day)

    lw = 2 
    plt.scatter(day, prices, color='darkorange', label='data')
    plt.plot(day, y_rbf, color='navy', lw=lw, label=u'近似曲線')
    plt.plot(future_day, predict_result, color='r', lw=lw, label=u'預測')
    plt.xticks(intervals, [date[i].strftime('%m/%d') for i in intervals])
    plt.xlabel('data')
    plt.ylabel(u'價格')
    plt.title(u'預測與實際誤差')
    plt.legend()
    plt.savefig(prefix + filename+'.png')
    return {'filepath': prefix+filename+'.png'}

if __name__ == '__main__':
    predict()
