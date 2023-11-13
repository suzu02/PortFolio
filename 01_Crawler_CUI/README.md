# Crawler_CUI
![python](https://img.shields.io/badge/python-v3.10-blue)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-v4.12.2-blue)
![CacheControl](https://img.shields.io/badge/CacheControl-v0.12.11-blue)
![lxml](https://img.shields.io/badge/lxml-v4.9.2-blue)
![requests](https://img.shields.io/badge/requests-v2.29.0-blue)
![tenacity](https://img.shields.io/badge/tenacity-v8.2.2-blue)<br>
<br>
Webサイトから任意のデータを自動収集(スクレイピング)してファイル出力を行うアプリケーションです。<br>
<br>
<image width="700" alt="処理中の画像" src="https://github.com/suzu02/PortFolio/assets/117723810/89fafd8f-a112-421d-aea9-356e3276f848"><br>
<br>
「sample_exe」ディレクトリ内の「sample_exe.zip」をダウンロード、解凍後に「app.exe」をダブルクリックすることで、スクレイピング練習サイトを対象とした処理をお試しできます。<br>
<br>
## 特徴
- Webサイトから取得したデータは、全角 / 半角や大文字 / 小文字の変換、年数や時刻の形式変更など、任意の形式に整形して出力できます。また、画像の出力も可能です。<br>
  <br>
- コードを追加(seleniumライブラリを使用)することで、ログイン、キーワード検索、ページスクロールなど、ブラウザの操作が必要な場合も対応可能です。<br>
  <br>
  <image width="700" alt="seleniumの画像" src="https://github.com/suzu02/PortFolio/assets/117723810/e992cb16-53ec-49f2-99ad-e044c1aad42b"><br>
  <br>
- exeファイルに変換することも可能です。  
  exeファイルは、プログラミング(Python)の実行環境がない場合でも、一般的なアプリケーションのようにダブルクリックのみで同様の処理を行うことができます。  
  実行するとコマンドプロンプトに処理状況が表示されますが、非表示にすることも可能です。<br>
  <br>
  <image width="700" alt="exeファイルの画像" src="https://github.com/suzu02/PortFolio/assets/117723810/35f8c137-66ad-4bdf-a7b9-e13b623c948c"><br>
  <br>
- 出力形式は「CSV」としていますが、「xlsx」「json」「Googleスプレッドシート」など変更可能です。<br>
  <br>
  <image width="100" alt="csvのロゴ" src="https://github.com/suzu02/PortFolio/assets/117723810/780f59a6-4236-4604-a07b-f24dfb1c5a33">
  <image width="100" alt="xlsのロゴ" src="https://github.com/suzu02/PortFolio/assets/117723810/964ffba4-8b78-478d-b975-2ffb2b112760">
  <image width="100" alt="jsonのロゴ" src="https://github.com/suzu02/PortFolio/assets/117723810/fc80b984-27f2-4c88-bdbb-f7a2d80237f7">
  <image width="100" alt="スプレッドシートのロゴ" src="https://github.com/suzu02/PortFolio/assets/117723810/6863c3b8-19a2-4792-8d62-23997daa4eaf"><br>
  <br>
- ログはファイルとしても出力され、実行ごとに上書きされます。  
  エラー発生時は前述とは別に出力されます。<br>
  <br>
  <image width="700" alt="ログの画像" src="https://github.com/suzu02/PortFolio/assets/117723810/9fd4b346-dbcb-49e9-a6aa-8b393153bc28"><br>
  <br>

### 注意事項
- Webサイトへの負荷軽減のため、リクエストを送る際に数秒の遅延を設定しています。
- Webサイトの方針に従い、可能な場合に限りキャッシュを取得/使用します。
- 動作確認は「Windows」のみで行っています。
