# Crawler_GUI
![python](https://img.shields.io/badge/python-v3.10-blue)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-v4.12.2-blue)
![CacheControl](https://img.shields.io/badge/CacheControl-v0.12.11-blue)
![lxml](https://img.shields.io/badge/lxml-v4.9.2-blue)
![requests](https://img.shields.io/badge/requests-v2.29.0-blue)
![tenacity](https://img.shields.io/badge/tenacity-v8.2.2-blue)<br>
<br>
Webサイトから任意のデータを自動収集(スクレイピング)してファイル出力を行うGUIアプリケーションです。<br>
<br>
<image width='700' alt='処理中の画像' src="https://github.com/suzu02/PortFolio/assets/117723810/ea8e2983-4560-44f3-8109-e39cffe09fda"><br>
<br>
「sample_exe」ディレクトリ内の「sample_exe.zip」をダウンロード、解凍後に「app.exe」をダブルクリックすることで、スクレイピング練習サイトを対象とした処理をお試しできます。<br>
<br>
## 特徴
- ボタンクリックにより、処理の 開始 / 停止 / 中止 などを操作することができます。<br>
  <br>
  <image width="600" alt="操作ボタンの画像" src="https://github.com/suzu02/PortFolio/assets/117723810/00a15155-00db-42a3-b231-8c28858770d1"><br>
  <br>
  操作状況や処理状況はアプリケーション上に表示されるため、視覚的にもわかりやすく直観的な操作が可能です。<br>
  <br>
  <image width="700" alt="ログウィンドウの画像" src="https://github.com/suzu02/PortFolio/assets/117723810/7f2de248-0652-42ee-a473-f7db5f61506f"><br>
  <br>
- Webサイトから取得したデータは、全角 / 半角や大文字 / 小文字の変換、年数や時刻の形式変更など、任意の形式に整形して出力できます。また、画像の出力も可能です。<br>
  <br>
- コードを追加(seleniumライブラリを使用)することで、ログイン、キーワード検索、ページスクロールなど、ブラウザの操作が必要な場合も対応可能です。<br>
  <br>
  <image width="700" alt="seleniumの画像" src="https://github.com/suzu02/PortFolio/assets/117723810/5a8f6f68-1f3b-496c-9134-cea726035df9"><br>
  <br>
- exeファイルに変換することも可能です。  
  exeファイルは、プログラミング(Python)の実行環境がない場合でも、ダブルクリックのみでGUIアプリケーションを起動できます。<br>
  <br>
  <image width="700" alt="exeファイルの画像" src="https://github.com/suzu02/PortFolio/assets/117723810/2db7a7dc-422f-47f8-a26e-4edb96820f0e"><br>
  <br>
- 出力形式は「CSV」としていますが、「xlsx」「json」「Googleスプレッドシート」など変更可能です。<br>
  <br>
  <image width="100" alt="csvのロゴ" src="https://github.com/suzu02/PortFolio/assets/117723810/fe40b7c5-ce00-4e37-991c-902e6a384e4a">
  <image width="100" alt="xlsのロゴ" src="https://github.com/suzu02/PortFolio/assets/117723810/6592c3ab-3b01-418c-8b80-29d0f63b2f83">
  <image width="100" alt="jsonのロゴ" src="https://github.com/suzu02/PortFolio/assets/117723810/a7b2d7fb-1ba9-48fe-a7d4-0df2fa42b518">
  <image width="100" alt="スプレッドシートのロゴ" src="https://github.com/suzu02/PortFolio/assets/117723810/59201ac2-8fed-49e3-a961-7ddac5d0ea7f"><br>
  <br>
- ログはファイルとしても出力され、実行ごとに上書きされます。  
  エラー発生時は前述とは別に出力されます。<br>
  <br>
  <image width="700" alt="ログの画像" src="https://github.com/suzu02/PortFolio/assets/117723810/3727b60d-df3d-4ba9-93f9-209ac83d40e4"><br>
  <br>

### 注意事項
- Webサイトへの負荷軽減のため、リクエストを送る際に数秒の遅延を設定しています。
- Webサイトの方針に従い、可能な場合に限りキャッシュを取得/使用します。
- 動作確認は「Windows」のみで行っています。
