# 標準ライブラリ
from collections import defaultdict
from datetime import datetime, timedelta
import os
import random
import re
import threading
import time
import traceback
from urllib.parse import urljoin

# 外部ライブラリ
from bs4 import BeautifulSoup
from cachecontrol import CacheControl
from cachecontrol.caches import FileCache
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

# 自己定義のモジュール
from log_handler import Logger
from items import Items
from user_agent import UserAgent


# キャッシュを保存する場合のディレクトリパス
CACHE_DIR = './.webcache'


class Config(object):
    """crawlerの初期設定"""

    def __init__(self):
        # log_handlerモジュールをインスタンス化
        self.log_handler = Logger(name=__name__, stdout=False)

        # スクレイピングの開始URL
        self.start_url = 'https://books.toscrape.com/'

        # 許可ドメインを定義
        self.allowed_domains = [
            'books.toscrape.com',
        ]
        # ユーザーエージェントのブラウザ名
        browser = 'chrome'
        # リクエストに対する遅延秒数
        self.delay_sec = 2
        # 遅延秒数の乱数化
        self.randomize = True
        # 取得レスポンスのエンコード
        self.encoding = 'utf-8'
        # 出力先のディレクトリ
        self.output_dir = os.path.join(
            os.environ['USERPROFILE'], 'Downloads').replace(os.sep, '/')
        # 出力ファイルの拡張子
        self.output_extension = 'csv'
        # 画像データの出力フラグ
        self.img_out = True
        # 画像データのファイル名
        self.img_title = None

        # リクエストを送る際のユーザーエージェントを定義
        ua = UserAgent()
        self.user_agent = ua.get_ua(browser)
        # リクエストを送る際のヘッダーを定義
        self.headers = {'User-Agent': self.user_agent}
        # リクエスト情報の保持やパフォーマンス向上のためセッションを定義
        session = requests.Session()
        # セッションを基にキャッシュを定義
        self.session_cache = CacheControl(session, FileCache(CACHE_DIR))


class Crawler(Config):
    """
    Webスクレイピング処理(crawl/scrape)を行うcrawlerを定義

    Note: crawlerに関連した属性等について
        status: crawlerの処理状況をタプルで定義
                none: 初期値/正常終了
                run: 処理中
                pause: 停止中
                cancel: 取消終了/エラー終了

        crawler_status: crawlerの処理状況の設定
            上記のstatusを代入することで設定

        crawler_alive_flag:
            crawlerの全体処理フラグ(True:処理中/False:終了)

        crawler_event:
            crawlerのthreading.Event

        threading.Event:
            イベントの内部フラグ(True/False)によってスレッドの停止/再開を制御
            set(): 内部フラグをTrueに設定/スレッドの再開処理
            clear(): 内部フラグをFalseに設定
            wait(): スレッドの停止処理(内部フラグがTrueになると再開)
            is_set(): 内部フラグ(True/False)の確認
    """

    def __init__(self):
        super().__init__()

        # 出力パスの生成
        self.create_output_path()

        # イベントの定義
        self.crawler_event = threading.Event()
        # 処理状況の定義
        self.status = ('none', 'run', 'pause', 'cancel')
        # ステータスを「初期値」に設定
        self.crawler_status = self.status[0]

    def create_output_path(self):
        """出力パスの生成"""

        # 実行日時を定義
        self.date_time = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')

        # ファイル名を定義
        file_name = f'{self.date_time}_scrape.{self.output_extension}'
        # 出力パスを定義
        self.output_file_path = os.path.join(
            self.output_dir, file_name).replace(os.sep, '/')

    def start_crawler_thread(self):
        """crawlerのスレッド作成/処理開始"""

        # 実行時のタイムスタンプ(経過時間算出のため)
        self.execute_time = time.time()
        # スレッドの定義(スレッド上で行う処理はdef run_crawler)
        self.crawler_thread = threading.Thread(target=self.run_crawler)
        # itemsモジュールのインスタンス化
        self.items = Items(self.log_handler)

        # ログ表示する処理結果のカウント
        self.result_count = {
            'リクエスト送信数': 0,
            'レスポンス受信数': 0,
            'ステータスコード': defaultdict(int),
            'スクレイピング処理数': 0,
        }

        # スレッドの開始(処理開始)
        self.crawler_thread.start()

    def run_crawler(self):
        """crawlerの全体処理を管理"""

        self.log_handler.logger.info('----- 処理開始 -----')

        # 内部フラグをTrueに設定
        self.crawler_event.set()
        # ステータスを「処理中」に設定
        self.crawler_status = self.status[1]
        # 全体処理フラグをTrueに設定
        self.crawler_alive_flag = True

        # crawlerの設定状況等をログ表示
        self.display_crawler_info()
        # 開始URLのcrawl(リクエスト)
        r = self.crawl(self.start_url)
        # 上記のレスポンスを基にスクレイピング処理
        self.execute_scraping(r)

        # ステータスが「取消終了/エラー終了」以外の場合
        if not self.crawler_status == self.status[3]:
            # 画像出力フラグがTrueの場合
            if self.img_out:
                # Itemsモジュールの画像出力
                self.items.output_img(self.output_dir, self.date_time)

            # 画像以外のデータをファイル出力
            self.items.output_file(self.output_file_path)

            # ステータスを「初期値」に設定
            self.crawler_status = self.status[0]

        # Itemsモジュールのデータ格納場所を初期化
        self.items.items = []
        self.items.img_data = {}

        # log_handlerモジュールの初期化
        self.log_handler.logger.removeHandler(self.log_handler.file_handler)
        self.log_handler.queue_handler.log_box = []

    def display_crawler_info(self):
        """crawlerの設定情報を表示"""

        self.log_handler.logger.info(
            f'- 開始URL: {self.start_url}')
        self.log_handler.logger.info(
            f'- ユーザーエージェント: {self.headers["User-Agent"]}')
        self.log_handler.logger.info(
            f'- リクエスト遅延秒数: {self.delay_sec}')
        self.log_handler.logger.info(
            f'- 遅延秒数のランダム化: {self.randomize}')
        self.log_handler.logger.info(
            f'- ファイルの保存先: {self.output_dir}')
        self.log_handler.logger.info(
            f'- ファイルの拡張子: {self.output_extension}'
        )

    def crawl(self, url):
        """リクエスト/レスポンスステータスコードに応じた処理"""

        self.log_handler.logger.info('----- クロール -----')

        # ドメインの検証結果フラグ
        is_allow = None

        # 自己定義した許可ドメインを順に取り出す
        for domain in self.allowed_domains:
            # 許可ドメインがリクエストURLに含まれている場合
            if domain in url:
                # フラグ変更
                is_allow = True

        # 許可ドメインがリクエストURLに含まれていない場合
        if not is_allow:
            # エラーメッセージの定義
            error_msg = (
                '[Crawl] 予期せぬURLにリクエストしようとしたため処理を中止しました。'
                f'URL: {url}'
            )
            # エラー終了
            self.error_handler(error_msg)

        # リクエストとステータスコードに応じた処理
        try:
            r = self.request_check_response(url)
        # エラーによるリクエストのリトライ上限を超えた場合
        except RetryError:
            # エラーメッセージの定義
            error_msg = (
                '[Crawl] リクエストが正常に処理されませんでした。'
                'ネットワーク環境の不具合もしくはWebページの一時的な不具合などが考えられます。'
            )
            # エラー終了
            self.error_handler(error_msg)
        # レスポンスを取得できた場合
        else:
            # Noneが返ってきた場合(一時的ではないエラー)
            if not r:
                # エラーメッセージの定義
                error_msg = (
                    '[Crawl] リクエストが正常に処理されませんでした。'
                    'クライアントエラーもしくはサーバーエラーが考えられます。'
                )
                # エラー終了
                self.error_handler(error_msg)

            # 処理結果のカウント
            self.result_count['レスポンス受信数'] += 1
            return r

    # stopはリトライ上限(値は上限数)
    # waitは次のリトライまでの待機時間(値は指数関数的に待機時間を増加)
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1))
    def request_check_response(self, url):
        """リクエストを送りステータスコードの確認/リトライ処理"""

        # 一時的なエラーとするステータスコードを自己定義
        temporary_error_codes = (408, 500, 502, 503, 504)

        # リクエスト前に負荷軽減の遅延処理
        self.request_delay(self.delay_sec, self.randomize)
        # 処理結果のカウント
        self.result_count['リクエスト送信数'] += 1
        # Configクラスで定義したセッションによりリクエスト
        r = self.session_cache.get(url, headers=self.headers, timeout=3.5)

        # リクエストの結果をログ表示
        self.log_handler.logger.info(f'リクエストURL: {r.url}')
        # ステータスコードに異常がある場合
        if 400 <= r.status_code:
            # エラーログとして表示
            self.log_handler.logger.error(f'ステータスコード: {r.status_code}')
        else:
            self.log_handler.logger.info(f'ステータスコード: {r.status_code}')
        self.log_handler.logger.info(f'キャッシュ: {r.from_cache}')

        # 処理結果のカウント
        self.result_count['ステータスコード'][r.status_code] += 1

        # ステータスコードに異常があり、一時的ではないエラーでもない場合
        if 400 <= r.status_code and r.status_code not in temporary_error_codes:
            # Noneを返す(呼び出し元でエラー終了)
            return None

        # ステータスコードが正常値である場合
        if r.status_code not in temporary_error_codes:
            # レスポンスを返す
            return r

        # 上記以外の場合(一時的なエラーの場合)は例外を発生させてtenacityモジュールのリトライ処理
        raise Exception('Temporary Error')

    def request_delay(self, sec=1, randomize=False):
        """リクエストの遅延処理"""

        if randomize:
            # 乱数の下限
            min = sec * 0.5
            # 乱数の上限
            max = sec * 1.5
            # uniform()はfloat対応の乱数生成処理
            self.log_handler.logger.info(f'リクエスト送信(遅延{min}s～{max}s)...')
            time.sleep(random.uniform(min, max))
        else:
            self.log_handler.logger.info(f'リクエスト送信(遅延{self.delay_sec}s)...')
            time.sleep(sec)

    def execute_scraping(self, r):
        """スクレイピングルートの設定/スクレイピングの実行"""

        # 開始URLから取得したレスポンス
        start_response = r

        # cssセレクター(各一覧ページのページURL)
        selector = 'ul.nav ul > li > a'
        # 一覧ページのurlを取得
        catalogue_urls = self.scrape_page_url(start_response, selector)

        # 一覧ページのurlを順に取り出す
        for i, url in enumerate(catalogue_urls, start=1):

            # 一覧ページの制限
            if i > 2:
                break

            # crawler制御の確認
            self.judgement_crawler_control()

            # 一覧ページのレスポンスを取得
            catalogue_response = self.crawl(url)

            # 詳細ページのページ数
            page_count = 1
            # 詳細ページのループ処理
            while True:
                # crawler制御の確認
                self.judgement_crawler_control()

                # cssセレクター(各詳細ページのページURL)
                selector = 'h3 > a'
                # 詳細ページのurlを取得
                detail_urls = self.scrape_page_url(
                    catalogue_response, selector)

                # 詳細ページのurlを順に取り出す
                for i, url in enumerate(detail_urls, start=1):
                    # crawler制御の確認
                    self.judgement_crawler_control()

                    # 詳細ページのレスポンスを取得
                    detail_response = self.crawl(url)
                    # スクレイピングデータ(タグ情報)の抽出
                    self.scrape_object(detail_response)

                # 詳細ページの抽出終了につきカウント
                page_count += 1
                # 詳細ページの制限
                if page_count > 2:
                    break

                # cssセレクター(次ページのURL)
                selector = 'li.next > a'
                # 次ページurlの取得
                next_page_url = self.scrape_page_url(
                    catalogue_response, selector, is_next=True)
                # 次ページurlがある場合
                if next_page_url:
                    # 処理起点のレスポンスを次ページのレスポンスで上書き
                    catalogue_response = self.crawl(next_page_url[0])
                    # 上書きしたレスポンスで初めの処理(whileループ)に戻る
                    self.log_handler.logger.info('>> 次のページに遷移')
                # 次ページがない場合はループから抜ける
                else:
                    break
        # 処理結果をログ表示
        self.display_result()

    def judgement_crawler_control(self):
        """
        crawlerのステータス/フラグの確認とそれに応じた制御

        Note:
            取消/終了処理について(if not self.crawler_alive_flag:)
                自己定義したフラグ(self.crawler_alive_flag)により判定。
                raiseにより本モジュールごとcrawler(スレッド)を終了。

            停止/再開処理について(elif not self.crawler_event.is_set():)
                thread.Eventの状態により判定
                EventがFalseの場合、event.wait()によりスレッド停止
                上記の状態でevent.set()されると、EventがTrueに変更されスレッドも再開
                Eventの状態は、GUIの特定のボタン操作により変更
        """

        # 呼び出された時点で処理全体フラグがFalseの場合
        if not self.crawler_alive_flag:
            # ステータスを「取消終了/エラー終了」に設定
            self.crawler_status = self.status[3]
            # 処理結果を表示
            self.display_result()
            # log_handlerモジュールを初期化
            self.log_handler.logger.removeHandler(self.log_handler.file_handler)
            self.log_handler.queue_handler.log_box = []
            # 例外発生により本モジュールを終了
            raise Exception('処理を終了します。')
        # 呼び出された時点で内部フラグがFalseの場合
        elif not self.crawler_event.is_set():
            self.log_handler.logger.info('----- 停止中 -----')
            # ステータスを「停止中」に設定
            self.crawler_status = self.status[2]
            # スレッドを停止(内部フラグがTrueになるまで)
            self.crawler_event.wait()
            # スレッドが再開したらステータスを「処理中」に設定
            self.crawler_status = self.status[1]

    def scrape_page_url(self, r, selector, is_xml=False, is_next=False):
        """レスポンスからページURLを抽出"""

        # lxmlのレスポンスである場合
        if not is_xml:
            # lxmlパーサーで解析して全体のタグ情報を取得
            soup = BeautifulSoup(r.text, 'lxml')
        # xmlのレスポンスである場合
        else:
            # xmlパーサーで解析して全体のタグ情報を取得
            soup = BeautifulSoup(r.text, 'xml')

        # 抽出したurlの格納場所
        urls = []
        # ページURLに該当するタグ情報を抽出
        url_tags = soup.select(selector)

        # ページタグを抽出できない場合
        if not url_tags:
            # 次ページURLを取得する場合
            if is_next:
                # 次ページがないものとしてNoneを返す
                return None

            # 上記以外の場合はエラー終了
            error_msg = (
                '[Scrape page url] ページURLのスクレイピングに失敗しました。(NoneType)'
            )
            self.error_handler(error_msg)

        # ページタグを抽出できた場合は順に取り出す
        for url_tag in url_tags:
            try:
                # lxmlのレスポンスである場合
                if not is_xml:
                    # href属性(URL)を取得
                    url = url_tag.attrs['href']
                # xmlのレスポンスである場合
                elif is_xml:
                    # テキスト情報(URL)を取得
                    url = url_tag.text
            # href属性が存在しない場合(念のため)
            except KeyError:
                # エラーメッセージの定義
                error_msg = (
                    '[Scrape page url] ページURLのスクレイピングに失敗しました。(KeyError)'
                )
                # エラー終了
                self.error_handler(error_msg)
            # 無事にURLを取得できた場合
            else:
                # 必要に応じてURLの整形処理して格納
                url = self.shaping_url(url, r)
                urls.append(url)
        return urls

    def shaping_url(self, url, r):
        """urlの整形処理(必要な場合のみ)"""

        # 必要に応じてURLの種類ごとに様々な整形処理を追加
        if re.match('catalogue/', url):
            shaped_url = urljoin('https://books.toscrape.com/', url)
            return shaped_url
        elif re.match(r'../../', url):
            rep_url = url.replace('../', '')
            shaped_url = urljoin('https://books.toscrape.com/catalogue/', rep_url)
            return shaped_url
        elif re.match(r'page', url):
            base_url = r.url.replace('index.html', '')
            shaped_url = urljoin(base_url, url)
            return shaped_url
        # 想定していないURLを取得した場合
        else:
            # エラーメッセージの定義
            error_msg = (
                '[Shaping url] 予期せぬURLをスクレイピングしたため処理を中止します。'
                f'URL: {url}'
            )
            # エラー終了
            self.error_handler(error_msg)

    def scrape_object(self, r):
        """対象のページから特定の情報(タグ情報)を抽出"""

        self.log_handler.logger.info('----- スクレイピング -----')

        # レスポンスからページ情報を取得
        soup = BeautifulSoup(r.text, 'lxml')

        # 一度全体のタグ情報から範囲を絞って抽出
        contents = soup.select_one('article > div.row')
        table = soup.find('table')

        # この段階で抽出できなかった場合
        if not contents or not table:
            # エラーメッセージの定義
            error_msg = (
                '[Scrape object] 特定要素のスクレイピングに失敗しました。'
            )
            # エラー終了
            self.error_handler(error_msg)

        # 抽出した1件分のタグ情報をdict型で集約
        data = {
            'url': r.url,
            'title': contents.find('h1'),
            'price': table.select_one('th:-soup-contains("excl")+td'),
            'star': contents.select_one('div.product_main p.star-rating'),
            'reviews': table.select_one('th:-soup-contains("reviews")+td'),
            'stock': table.select_one(
                'th:-soup-contains("Availability")+td'),
            'upc': table.select_one('th:-soup-contains("UPC")+td'),
            'image_url': contents.select_one('div.item > img'),
        }

        # Itemsモジュールに渡す
        self.items.add_items(data)
        # 処理結果のスクレイピング項目にカウント
        self.result_count['スクレイピング処理数'] += len(data)

        # 画僧出力の必要がある場合
        if self.img_out:
            self.scrape_img_content(contents)

    def scrape_img_content(self, tag_data):
        """画像データの抽出"""

        # 画像データのファイル名を定義
        img_title = self.setup_img_title(self.img_title)
        # cssセレクター
        img_selector = 'div.item > img'
        # imgタグを抽出
        img_tag = tag_data.select_one(img_selector)

        # セレクターの誤りによるNoneTypeを取得した場合
        if not img_tag:
            self.log_handler.logger.warning(
                '[Scrape object] 画像出力に失敗しました。(NoneType)'
            )
            # 処理終了
            return

        # imgタグからsrc属性を抽出
        try:
            src = img_tag.attrs['src']
        # src属性が存在しない場合(念のため)
        except KeyError:
            self.log_handler.logger.warning(
                '[Scrape object] 画像出力に失敗しました。(KeyError)'
            )
            # 処理終了
            return

        # 無事にURLが取得できた場合(必要に応じてURLの整形処理)
        img_src = urljoin('https://books.toscrape.com/', src)

        # ソースタグのURLをcrawl(リクエスト)
        r = self.crawl(img_src)
        # Itemsモジュールの属性に画像の名前と画像データのバイト文字列を渡す
        self.items.img_data[img_title] = r.content

    def setup_img_title(self, title=None):
        """画像の名前設定(重複時の上書き防止)"""

        # タイムスタンプの取得
        time_stamp = str(time.time()).replace('.', '')
        # 名前の指定がない場合
        if not title:
            # 上記のタイムスタンプを返す(重複の可能性なし)
            return time_stamp

        # 名前の指定があり、Itemsモジュールに既に渡された名前と重複している場合
        if title in self.items.img_data.keys():
            # 上書き防止のため指定された名前に追記して返す
            return f'{title}_copy({time_stamp})'

        # 名前の指定があり、Itemsモジュールに既に渡された名前とも重複していない場合
        return title

    def error_handler(self, error_msg):
        """エラー発生時の処理を一元管理"""

        # 引数で受け取ったエラーメッセージをログ表示
        self.log_handler.logger.error(error_msg)
        # プログラムのエラーメッセージを格納
        error_note = traceback.format_exc()

        # ステータスを「取消終了/エラー終了」に設定
        self.crawler_status = self.status[3]
        # エラー発生までの処理結果をログ表示
        self.display_result()

        # QueueHandlerのエラーログ用のリストを一旦格納
        log_box = self.log_handler.queue_handler.log_box
        # 上記のログを基にエラーログをファイル出力
        self.log_handler.output_error_log(
            self.date_time, self.output_dir, log_box, error_note)

        # 連続実行を想定してhandler等を初期化
        self.log_handler.logger.removeHandler(self.log_handler.file_handler)
        self.log_handler.queue_handler.log_box = []

        # 例外発生により本モジュールを終了
        raise Exception(error_msg)

    def display_result(self):
        """処理結果の表示処理"""

        self.log_handler.logger.info('===== 処理終了 =====')

        # 処理結果のカウントからkey/valueを取り出す
        for k, v in self.result_count.items():
            # ステータスコードの場合
            if k == 'ステータスコード':
                # valueがdict型のため更にループで取り出す
                for status_code, count in v.items():
                    # ステータスコードのログ表示
                    self.log_handler.logger.info(
                        f'> {k}: {status_code}[{count}]')
                continue
            # ステータスコード以外のログ表示
            self.log_handler.logger.info(f'> {k}: {v}')

        # 経過時間の定義
        elapsed_time = int(time.time() - self.execute_time)
        # 経過時間のログ表示
        self.log_handler.logger.info(
            f'> 経過時間: {timedelta(seconds=elapsed_time)}')
