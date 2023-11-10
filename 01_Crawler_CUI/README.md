# Crawler_CUI
Webサイトから任意のデータを自動収集(スクレイピング)してファイル出力を行うアプリケーションです。<br>
<br>
<image width="600" alt="処理中の画像" src="https://github.com/suzu02/PortFolio/assets/117723810/3b7f84e3-0bb6-407a-81d0-8567d54dfa71"><br>
<br>
「sample_exe」ディレクトリ内の「sample_exe.zip」をダウンロード、解凍後に「app.exe」をダブルクリックすることで、スクレイピング練習サイトを対象とした処理をお試しできます。<br>
<br>
## 特徴
- Webサイトから取得したデータは、全角 / 半角や大文字 / 小文字の変換、年数や時刻の形式変更など、任意の形式に整形して出力できます。また、画像の出力も可能です。<br>
  <br>
- コードを追加(seleniumライブラリを使用)することで、ログイン、キーワード検索、ページスクロールなど、ブラウザの操作が必要な場合も対応可能です。<br>
  <br>
  <image width="500" alt="seleniumの画像" src="https://github.com/suzu02/PortFolio/assets/117723810/c58e93f0-c18c-4f98-96a8-9504fbd0e47f"><br>
  <br>
- exeファイルに変換することも可能です。  
  exeファイルは、プログラミング(Python)の実行環境がない場合でも、一般的なアプリケーションのようにダブルクリックのみで同様の処理を行うことができます。  
  実行するとコマンドプロンプトに処理状況が表示されますが、非表示にすることも可能です。<br>
  <br>
  <image width="550" alt="exeファイルの画像" src="https://github.com/suzu02/PortFolio/assets/117723810/277721ca-18c5-48d8-a121-24042c30a96d"><br>
  <br>
- 出力形式は「CSV」としていますが、「xlsx」「json」「Googleスプレッドシート」など変更可能です。<br>
  <br>
  <image width="550" alt="出力ファイルの画像" src="https://github.com/suzu02/PortFolio/assets/117723810/0d3d87de-4704-431f-bd3a-a4dd3b5ae94a"><br>
  <br>
- ログはファイルとしても出力され、実行ごとに上書きされます。  
  エラー発生時は前述とは別に出力されます。<br>
  <br>
  <image width="550" alt="ログの画像" src="https://github.com/suzu02/PortFolio/assets/117723810/5d974639-6ce4-4042-b098-d94ec728bd7d"><br>
  <br>

### 注意事項
- Webサイトへの負荷軽減のため、リクエストを送る際に数秒の遅延を設定しています。
- Webサイトの方針に従い、可能な場合に限りキャッシュを取得/使用します。
- 動作確認は「Windows」のみで行っています。
