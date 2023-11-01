# 標準ライブラリ
import logging
import os
import queue


class Logger(object):
    """ログに関連した処理を定義"""

    def __init__(self, name, stdout=False):
        # 引数で受け取った名前のloggerを定義
        self.logger = logging.getLogger(name)
        # ログレベル設定
        self.logger.setLevel(logging.INFO)
        # フォーマット
        self.fmt = logging.Formatter(
            '[%(asctime)s] (%(levelname)s) %(message)s')
        # 様々なハンドラーをloggerに追加
        self.set_handler(stdout)

    def set_handler(self, stdout):
        """
        ハンドラーの追加と引数に応じたログの標準出力

        Note:
            queue_handler(QueueHandler):
                エラー発生時のログ出力
                queueから任意のタイミングで取り出せるためエラー発生時のログ出力に使用
                QueueHandlerは自己定義のハンドラーでqueueへログ出力
            file_handler(logging.FileHandler):
                一時的なログとして、1回分の実行ログを出力(同じファイルに上書き)
                FileHandlerはlogger追加時点でファイル出力
            stream_handler(logging.StreamHandler):
                コマンドプロンプト表示用のログ出力に使用
                StreamHandlerは標準出力へのログ出力
        """

        # queueの定義
        self.log_queue = queue.Queue()
        # QueueHandlerの定義
        self.queue_handler = QueueHandler(self.log_queue)
        # フォーマット適用
        self.queue_handler.setFormatter(self.fmt)
        # loggerに追加
        self.logger.addHandler(self.queue_handler)

        # loggingのFileHandlerを定義
        file_handler = logging.FileHandler(
            './tmp.log', mode='w', encoding='utf-8')
        # フォーマット適用
        file_handler.setFormatter(self.fmt)
        # loggerに追加
        self.logger.addHandler(file_handler)

        # 引数がTrueの場合
        if stdout:
            # loggingのStreamHandlerを定義
            stream_handler = logging.StreamHandler()
            # フォーマット適用
            stream_handler.setFormatter(self.fmt)
            # loggerに追加
            self.logger.addHandler(stream_handler)

    def output_error_log(self, date_time, output_dir, error_note):
        """Crawlerのエラー発生時におけるログファイル出力"""

        # 引数からエラーログのファイル名を定義
        file_name = f'{date_time}_scrape_error.log'
        # 上記と引数を組み合わせてエラーログのファイルパスを定義
        path = os.path.join(
            output_dir, file_name).replace(os.sep, '/')

        # whileループによりqueueからログを取り出す
        while True:
            try:
                # queueからログの取り出し(blockパラメータは取り出し中に処理全体を停止させるかどうか)
                record = self.log_queue.get(block=False)
            # queueが空になったら処理終了
            except queue.Empty:
                break
            # 取り出せた場合
            else:
                # 取り出したログにフォーマット適用/str型変換
                msg = self.queue_handler.format(record)
                # ファイル出力(追記モード)
                with open(path, 'a', encoding='utf-8', newline='') as f:
                    f.write(f'{msg}\n')
        with open(path, 'a', encoding='utf-8', newline='') as f:
            f.write(f'\n----- ERROR NOTE -----\n{error_note}')


class QueueHandler(logging.Handler):
    """Queueをログの出力先とするためのHandlerを自己定義"""

    def __init__(self, log_queue):
        # 親クラスの__init__()を要請
        super().__init__()
        # 引数で受け取ったqueueを属性定義(ログの出力先)
        self.log_queue = log_queue

    def emit(self, record):
        """logging.Handlerクラスの関数(ログ出力時に呼び出される)"""

        # ログ出力時に引数を通してqueueにログを追加
        self.log_queue.put(record)
