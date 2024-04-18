import requests
from pyquery import PyQuery

# 貨幣


def get_exchange_table2():
    # 資料來源網址
    url2 = 'https://www.moneydj.com/us/rank/rank0028/1M'
    # 輸出的字典
    table2 = {}
    # 取得伺服器的回應
    res2 = requests.get(url2)
    # 透過PyQuery解析HTML
    html2 = PyQuery(res2.text)
    # 所有股票名稱
    names2 = html2('td.col03').text().split()
    # 所有股票報價
    bids2 = html2('td.col06').text().split()

    # 價格計數器
    p2 = 0
    i = 0
    for n_idx2, name2 in enumerate(names2):
        if n_idx2==i:
            table2[name2] = {
                "bid2": bids2[p2],
            }
            # 把p+1
            p2 += 1
            i=i+1
            
    return table2

a2 = get_exchange_table2()
print(a2)