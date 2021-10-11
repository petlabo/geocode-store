<h1>geocode-store</h1>
Store information of "Chofu Premium Gift" in a map using folium<br>
プレミアム商品券の対象店の情報をfoliumにて作成したマップ上に掲載

<h2>手順</h2>
<strong>1.</strong> プレミアム商品券の対象店の一覧が掲載されたページから店舗情報をスクレイピングする。<br>
<strong>2.</strong> <strong>1</strong>にて得られた店舗住所から緯度経度を取得する。<br>
<strong>3.</strong> <strong>2</strong>にて得られた緯度経度を用いて、foliumにて作成したマップ上にマーカーを作成する。

<h2>ソースコード</h2>
手順1・3に該当するソースコード: chofu_coupon.ipynbまたはchofu_coupon.py<br>
手順2に該当するソースコード: land_scraping_chofu.py<br><br>
出来上がったhtmlファイル: <a href="https://petlabo.github.io/geocode-store/chofu_maps.html">chofu_maps.html</a>
