# 標準ライブラリ
import csv
import os
import re
from urllib.parse import urljoin


class Items(object):
    """スクレイピングデータの受け取り/値取得/整形/ファイル出力/画像出力を定義"""

    def __init__(self, log_handler):
        # log_handlerモジュールのインスタンス化
        self.log_handler = log_handler
        # 最終的なスクレイピングデータの格納場所
        self.items = []
        # 最終的な画僧データの格納場所
        self.img_data = {}

    def add_items(self, data):
        """スクレイピングデータの受け取りから出力までの全体処理を管理"""

        # 受け取ったスクレイピングデータ
        self.data = data
        # 値の取得
        self.get_content(self.data)
        # 整形処理
        self.shaping_content(self.data)
        # itemsに格納
        self.items.append(self.data)

        # 整形処理後のスクレイピングデータをログ表示
        [self.log_handler.logger.info(
                f'- {k}: {v}') for k, v in self.data.items()]

    def get_content(self, data):
        """スクレイピングデータから値を取得"""

        # スクレイピングデータからkey/valueを順に取り出す
        for key, value in data.items():
            # keyに応じたvalue(タグ情報)がNoneTypeではない場合
            if key == 'url' and value:
                # urlは既に値が代入されているため取得処理不要
                continue
            # keyに応じたvalue(スクレイピングデータ)がNoneTypeではない場合
            elif key == 'title' and value:
                # valueから値を取得して再代入
                self.data[key] = value.text
            elif key == 'price' and value:
                self.data[key] = value.text
            elif key == 'star' and value:
                self.data[key] = value.attrs['class'][1]
            elif key == 'reviews' and value:
                self.data[key] = value.text
            elif key == 'stock' and value:
                self.data[key] = value.text
            elif key == 'upc' and value:
                self.data[key] = value.text
            elif key == 'image_url' and value:
                self.data[key] = value.attrs['src']
            # いずれにも該当しない場合(valueがNoneTypeの場合)
            else:
                self.log_handler.logger.warning(
                    f'[Get content] "{key}" の取得に失敗しました。(NoneType)'
                )
                # 該当するkeyのvalueに空文字列を再代入
                self.data[key] = 'none'

    def shaping_content(self, data):
        """必要に応じて取得した値の整形/更新"""

        # 該当するkeyに整形処理後のvalueを再代入
        data['star'] = self.convert_text_to_number(data['star'])
        data['reviews'] = self.convert_integer(data['reviews'])
        data['stock'] = self.extract_stock(data['stock'])
        data['image_url'] = self.convert_image_url(data['image_url'])

    def delete_meta_str(self, data):
        """特殊文字列の削除"""

        # 値が存在する場合
        if data:
            # 前後の空白文字や特殊文字を削除
            data = data.strip().replace('\r', '').replace('\t', '').replace('\n', '')
            # 特殊文字を削除して値がない場合は欠損として文字列を返す
            if not data:
                return 'none'
            return data
        # 値が存在しない場合は空文字を返す
        return 'none'

    def convert_integer(self, data):
        """int型への変換"""

        if data:
            try:
                return int(data)
            except (TypeError, ValueError):
                key = [k for k, v in self.data.items() if v == data]
                self.log_handler.logger.warning(
                    f'* 整形処理失敗 [{key[0]}: {data}]')
                return 'none'
        return 'none'

    def extract_stock(self, data):
        """「stock」の抽出"""

        if data:
            m = re.search('In stock', data)
            if m:
                return self.convert_integer(
                    data.replace(
                        'In stock (', '').replace(' available)', ''))
            else:
                key = [k for k, v in self.data.items() if v == data]
                self.log_handler.logger.warning(
                    f'* 整形処理失敗 [{key[0]}: {data}]')
                return 'none'
        return 'none'

    def convert_text_to_number(self, data):
        """テキストから数字へ変換"""

        convert_pattern = {
            'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5
        }
        if data:
            try:
                return convert_pattern[data]
            except KeyError:
                key = [k for k, v in self.data.items() if v == data]
                self.log_handler.logger.warning(
                    f'* 整形処理失敗 [{key[0]}: {data}]')
                return 'none'
        return 'none'

    def convert_image_url(self, data):
        """画像の相対URLを絶対URLに変換"""

        if data:
            if re.search(r'\.jpg', data):
                rel_url = data.replace('../', '')
                abs_url = urljoin('https://books.toscrape.com/', rel_url)
                return abs_url
            else:
                key = [k for k, v in self.data.items() if v == data]
                self.log_handler.logger.warning(
                    f'* 整形処理失敗 [{key[0]}: {data}]')
                return 'none'
        return 'none'

    def output_img(self, output_dir, date_time, extension='jpg'):
        """画像の出力処理"""

        # 引数を組み合わせて画像用の出力ディレクトリを定義
        img_dir = f'{output_dir}/{date_time}_images'
        # 画像の出力ディレクトリが存在しない場合
        if not os.path.exists(img_dir):
            # ディレクトリを新規作成
            os.mkdir(img_dir)

        # img_dataからkey(画像の名前)/value(バイト文字列の画像データ)を順に取り出す
        for title, content in self.img_data.items():
            # 前述のディレクトリと引数を組み合わせて出力パスを定義/画像出力
            with open(f'{img_dir}/{title}.{extension}', 'wb') as f:
                f.write(content)

        self.log_handler.logger.info(f'> 画像データの保存先: {img_dir}')

    def output_file(self, output_file_path):
        """ファイル出力処理"""

        # ヘッダー(各列のタイトル)の空リストを定義
        field_name = []
        # リスト内包表記によりスクレイピングデータのkeyをヘッダーとして上記のリストに代入
        [field_name.append(key) for key in self.data.keys()]
        # 「csv」ファイル出力
        with open(output_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=field_name)
            writer.writeheader()
            writer.writerows(self.items)
        self.log_handler.logger.info(f'> 出力ファイル {output_file_path}')
