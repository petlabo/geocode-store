# -*- coding: utf-8 -*-
"""chofu_coupon.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ie_imwU2lISnx9CB90gj0WRhZVx9xhWT

foliumによって新宿地図にマーカーを作成
"""

!pip install folium

import folium

text = "<h3>aaaaaaaaaaaaaaaa</h3><br><h4>aaaaaaaaaaaaaaaaaaaaaaaaaa</h4><br><a href=\"http://google.com\"><h4>詳細</h4></a>"

folium_map = folium.Map(location=[35.690921, 139.700258], zoom_start=15)
folium.Marker(
    location=[35.690921, 139.700258], 
    popup=text
  ).add_to(folium_map)

star1_group = folium.FeatureGroup(name="一つ星").add_to(folium_map)
star1_group.add_child(
    folium.Marker(
    location=[35.6, 139.7], 
    icon=folium.Icon(color="green"),
    popup=text
    ).add_to(folium_map)
  )

folium.LayerControl().add_to(folium_map)

folium_map

"""**手順1**<br>
プレミアム商品券のページから店舗情報をスクレイピング
"""

import requests
from bs4 import BeautifulSoup as bs4
import numpy as np
import re
import itertools
import time

#urlよりhtml情報を取得
def get_soup(page_url):
  get = requests.get(page_url)
  soup = bs4(get.content, "html.parser")
  return soup


#任意のページから複数の店舗情報を取得
def soup_one_page(page):
  #正規表現により整地した店舗情報を以下の変数に格納
  store_name_trim = []
  store_tag_trim = []
  store_url_trim = []
  store_add_trim = []

  #今回情報を取得するページ
  page_url = "https://premium-gift.jp/chofu2021/use_store?events=page&id=" + str(page) + "&store=&addr=&industry="
  soup = get_soup(page_url)

  block_name = soup.find_all("h3", "store-card__title")
  block_tag = soup.find_all("p", "store-card__tag")
  block_url = soup.find_all("a", "store-card__button")
  block_add = soup.find_all("tbody")

  for i in range(len(block_name)):
    name = block_name[i]
    name = re.sub("</*h3( class=\"store-card__title\")*>", "", str(name))
    name = re.sub("\xa0", " ", name)
    store_name_trim.append(name)

    tag = block_tag[i]
    tag = re.sub("</*p( class=\"store-card__tag\")*>", "", str(tag))
    store_tag_trim.append(tag)

    url = block_url[i]
    url = re.sub("</*p( class=\"store-card__tag\")*>", "", str(url))
    url = re.sub(r".*href=\"(.*)\">", r"\1", url)
    url = re.sub(r"(.*)\n.*", r"\1", url)
    store_url_trim.append(url)      

    add = block_add[i].find("td")
    add = re.sub("</*td>", "", str(add))
    add = re.sub(".*\xa0", "", add)
    add = re.sub(r"([0-9])[あ-んア-ン一-鿐]+.*", r"\1", add)
    store_add_trim.append(add)

  
  print("-"*60)
  print("page_num: {}".format(page))
  print("len: {}, store_name_trim: {}".format(len(store_name_trim), store_name_trim))
  print("len: {}, store_tag_trim: {}".format(len(store_tag_trim), store_tag_trim))
  print("len: {}, store_url_trim: {}".format(len(store_url_trim), store_url_trim))
  print("len: {}, store_add_trim: {}".format(len(store_add_trim), store_add_trim))

  return {"name": store_name_trim, "tag": store_tag_trim, "url": store_url_trim, "add": store_add_trim}

#すべてのページから店舗情報を取得page1~53
def soup_all_page(page_num = 53):
  #すべての店舗情報を格納する変数
  store_name = []
  store_tag = []
  store_url = []
  store_add = []
  
  for page in range(1, page_num+1):
    store_data = soup_one_page(page)
    print(store_data)
    store_name_trim = store_data["name"]
    store_tag_trim = store_data["tag"]
    store_url_trim = store_data["url"]
    store_add_trim = store_data["add"]
    time.sleep(15) #Webページのサーバに迷惑が掛からないように時間を置く

    store_name.append(store_name_trim)
    store_tag.append(store_tag_trim)
    store_url.append(store_url_trim)
    store_add.append(store_add_trim)

    print(store_name)

  store_name = [x for row in store_name for x in row]
  store_tag = [x for row in store_tag for x in row]
  store_url = [x for row in store_url for x in row]
  store_add = [x for row in store_add for x in row]

  return store_name, store_tag, store_url, store_add

import pandas as pd

#すべてのページ情報をDataFrameに格納
store_name, store_tag, store_url, store_add = soup_all_page() 

df = pd.DataFrame(columns=["name", "tag", "url", "add"])

df = pd.DataFrame({"name": store_name,
                   "tag": store_tag,
                   "url": store_url,
                   "add": store_add})


df.info()

df.to_csv("/content/drive/My Drive/chofu_coupon/store_data.csv", index=False, header=True)

"""**手順3**<br>
緯度経度情報を追加した店舗情報をもとに、foliumマップに店舗を表したマーカーを追加する。
"""

import pandas as pd

df_store = pd.read_csv("/content/drive/My Drive/chofu_coupon/store_data_add_latlon.csv")
print(df_store["latitude"].describe())
print(df_store["longitude"].describe())
mean_latitude = df_store["latitude"].mean()
mean_longitude = df_store["longitude"].mean()

#店舗の属性（今回は飲食店・コンビニ・スーパーのみを出力させる。）
df_store["tag"].value_counts()

import folium

#店舗のマーカーをクリックしたときに出てくるポップアップに表示されるテキストを作成
def create_text(row):
  text = "<h4>{}{}</h4><h5>{}</h5><a href=\"{}\"><h5>詳細</h5></a>".format(
      row["name"], "　"*10, row["tag"], row["url"]
  )
  return text

#マーカーの色を店舗属性ごとに分類
def create_marker_color(row):
  if row["tag"] == "飲食店":
    return "red"
  elif row["tag"] == "スーパー":
    return "blue"
  elif row["tag"] == "コンビニ":
    return "green"

#マーカーを作成
def create_marker(row):
  marker = folium.Marker(
      location=[row["latitude"], row["longitude"]], 
      icon=folium.Icon(color=create_marker_color(row)),
      popup=create_text(row)
    )
  return marker

#マップを作成
plot_map = folium.Map(location=[mean_latitude, mean_longitude], zoom_start=13)

restaurants_group = folium.FeatureGroup(name="飲食店").add_to(plot_map)
supermarkets_group = folium.FeatureGroup(name="スーパー").add_to(plot_map)
convenience_stores_group = folium.FeatureGroup(name="コンビニ").add_to(plot_map)

for i, row in df_store[df_store["tag"] == "飲食店"].iterrows():
  restaurants_group.add_child(create_marker(row))

for i, row in df_store[df_store["tag"] == "スーパー"].iterrows():
  supermarkets_group.add_child(create_marker(row))

for i, row in df_store[df_store["tag"] == "コンビニ"].iterrows():
  convenience_stores_group.add_child(create_marker(row))

folium.LayerControl().add_to(plot_map)


# [‘red’, ‘blue’, ‘green’, ‘purple’, ‘orange’, ‘darkred’,
# ’lightred’, ‘beige’, ‘darkblue’, ‘darkgreen’, ‘cadetblue’, 
# ‘darkpurple’, ‘white’, ‘pink’, ‘lightblue’, ‘lightgreen’, 
# ‘gray’, ‘black’, ‘lightgray’]

plot_map

plot_map.save("chofu_maps.html")