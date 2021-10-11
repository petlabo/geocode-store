import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from tqdm import tqdm

# queries例 = ["東京都調布市", "東京都調布市小島町１－１－１", "東京都調布市小島町1-1-1"] 住所をq=の後に入力
split_url = "https://www.geocoding.jp/?q="

addresses = pd.read_csv("store_data.csv")
print(addresses.at[0,"add"])

addresses["latitude"] = addresses["longitude"] = 0.

count = 0
for query in tqdm(addresses["add"]): #address群に対して、address(住所)->address(緯度経度)に変換作業
    url = split_url + query

    try:
        html = requests.get(url) #html情報を取得

        soup = BeautifulSoup(html.content, 'html.parser') #html.contentをhtmlの見慣れた形に整地

        #緯度経度の該当箇所をfindメソッドで収集->re.subでタグ等を除去
        LatLon = soup.find("div", {"id":"address"}).find("span", {"class":"nowrap"}).find_all("b")
        LatLon[0] = re.sub("</*b>", "", str(LatLon[0]))
        LatLon[1] = re.sub("</*b>", "", str(LatLon[1])) 

    #適さない住所によって、緯度経度が返されない場合に例外処理
    except:
        LatLon[0] = LatLon[1] = -1

    LatLon_result = [float(LatLon[0]), float(LatLon[1])]
    # print(LatLon_result)
    time.sleep(8) #WEBページサーバーの負荷を考慮して時間を置く
    
    #DataFrameに格納
    addresses.at[count, "latitude"] = LatLon_result[0]
    addresses.at[count, "longitude"] = LatLon_result[1]
    count+=1

    # if count == 5: #testモード
    #     break

addresses.to_csv("store_data_add_latlon.csv", index=False)