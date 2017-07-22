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

targets = [
    [
        "白肉雞(2.0Kg以上)",
        "白肉雞(1.75-1.95Kg)",
        "白肉雞(門市價高屏)",
        "雞蛋(產地)"
    ],
    [
        "中區紅羽土雞公上貨"
        "中區紅羽土雞母上貨",
        "嘉南紅羽土雞公上貨",
        "嘉南紅羽土雞母上貨",
        "高屏紅羽土雞公上貨",
        "高屏紅羽土雞母上貨",
        "嘉南紅羽土雞綜貨",
        "黑羽土雞公舍飼",
        "黑羽土雞母舍飼"
    ],
    [
        "紅羽土雞北區",
        "紅羽土雞中區",
        "紅羽土雞南區"
    ],
    [
        "雛鵝參考價格",
        "肉鵝平均價格"
    ],
    [
        "肉鵝(上鵝)價格/土鵝",
        "小鵝產地價格(隻)/土鵝",
        "肉鵝(上鵝)價格/白羅曼鵝",
        "小鵝產地價格(隻)/白羅曼鵝"
    ]
]
api_urls = [
    'http://data.coa.gov.tw/Service/OpenData/FromM/PoultryTransBoiledChickenData.aspx',
    'http://data.coa.gov.tw/Service/OpenData/FromM/PoultryTransLocalChickenData.aspx',
    'http://data.coa.gov.tw/Service/OpenData/FromM/PoultryTransLocalRedChickenData.aspx',
    'http://data.coa.gov.tw/Service/OpenData/FromM/PoultryTransGooseWeeklyPriceData.aspx',
    'http://data.coa.gov.tw/Service/OpenData/FromM/PoultryTransGooseDailyPriceData.aspx',
    'http://data.coa.gov.tw/Service/OpenData/FromM/PoultryTransGooseDuckData.aspx'
]
def predict(target="肉鵝平均價格", start=90, predict_days=30, C=1e1):
    filename = hashlib.md5((str(target)+str(start)+str(C)).encode('utf-8')).hexdigest()
    prefix = 'plot/'
    prices = []
    date = []
    day = []
    future_day = []
    future_date = []

    for i in range(len(targets)):
        if target in targets[i]:
            api_url = api_urls[i]
            break
    
    intervals = [int((start+predict_days)/10*(i+1))-1 for i in range(10)]
    api = ur.urlopen(api_url) 
    json_data = json.loads(api.read().decode('utf-8'))
    for i, j in enumerate(json_data[0:start]):
        d = j['日期']
        dd = datetime.datetime(int(d[0:4]), int(d[5:7]),  int(d[8:10]))
        date.append(dd)
        day.append(start-i)
        
        prices.append(j[target]) if(j[target] != '休市') else prices.append(0)
    
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
    return {"filepath": prefix + filename+'.png'}

if __name__ == '__main__':
    predict()
