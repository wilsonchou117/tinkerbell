import requests
from pyquery import PyQuery

# 貨幣


def get_exchange_table3():
    # 資料來源網址
    url3 = 'https://histock.tw/stock/rank.aspx'
    # 輸出的字典
    table3 = {}
    # 取得伺服器的回應
    res3 = requests.get(url3)
    # 透過PyQuery解析HTML
    html3 = PyQuery(res3.text)
    # 所有股票名稱
    names2 = html3('td').children()
    names3=names2('a').text().split()
    # 所有股票報價
    bids2 = html3('td').children()
    bids3=bids2('span').text().split()

    # 價格計數器
    p2 = 0
    i = 0
    for n_idx2, name2 in enumerate(names3):
        if n_idx2 == i:
            table3[name2] = {
                "bid3": bids3[p2],
            }
            # 把p2+6
            p2 += 6
            i=i+1
        
    return(table3)

a2 = get_exchange_table3()
print(a2)