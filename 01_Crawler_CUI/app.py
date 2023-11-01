# 自己定義のモジュール
from crawler import Crawler


def main():
    """プログラム全体の開始処理"""

    # Crawlerモジュールを呼び出してスクレイピング処理を実行
    crawler = Crawler()
    crawler.run_crawler()


if __name__ == '__main__':
    main()
