# 標準ライブラリ
import queue
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

# 自己定義モジュール
from crawler import Crawler


class ControlUi(object):
    """
    「Crawlerコントロール」部分の定義

    Note: 関連するCrawlerモジュールの属性等について
        crawler_status: Crawlerモジュールの処理状況の詳細
            status[0]: 初期値/正常終了
            status[1]: 処理中
            status[2]: 停止中
            status[3]: 取消終了/エラー終了

        crawler_alive_flag:
            Crawlerモジュールの全体処理フラグ(True:処理中/False:終了)

        crawler_event:
            Crawlerモジュールのthreading.Event

        threading.Event:
            イベントの内部フラグ(True/False)によってスレッドの停止/再開を制御
            set(): 内部フラグをTrueに設定/スレッドの再開処理
            clear(): 内部フラグをFalseに設定
            wait(): スレッドの停止処理(内部フラグがTrueになると再開)
            is_set(): 内部フラグ(True/False)の確認
    """

    def __init__(self, frame, crawler, master, log_window, log_handler):
        # 「Crawlerコントロール」用のフレームを属性定義
        self.frame = frame
        # crawlerモジュールを属性定義
        self.crawler = crawler
        # Tkオブジェクトを属性定義
        self.master = master
        # GUI「ログウィンドウ」部分のテキストを属性定義
        self.scrolled_text = log_window.scrolled_text
        # log_handlerモジュールを属性定義
        self.log_handler = log_handler

        # 「Crawlerコントロール」の各widgetを生成/配置
        self.create_widget()

    def create_widget(self):
        """
        Crawlerコントロール部分の各widget定義

        Note:
            「開始URL」「ファイルの保存先」のEntry幅をウィンドウの横幅に合わせて引き延ばし、ウィンドウの伸縮にも連動。
            そのために、関連するframeにcolumnconfigureを設定し、widgetはwidthを設定せずstickyでew(両方向)に設定。
            これらは、元となっているAppクラスのmasterの時点からcolumnconfigureを設定する必要がある。
        """

        # 属性定義したフレームを土台に更にフレームを定義(全体の余白調整のため)
        frame = tk.Frame(self.frame)
        # grid配置して上下左右に広げ全体の余白を設定
        frame.grid(column=0, row=0, sticky='nesw', padx=10, pady=(10, 0))
        # frame幅をウィンドウ幅に広げて伸縮可能に(第一引数に列番号、第二引数はその列をどのくらい広げるかの割合)
        frame.columnconfigure(0, weight=1)

        # 「開始url」配置用のフレーム
        target_url_frame = tk.Frame(frame)
        target_url_frame.grid(column=0, row=0, pady=(0, 5), sticky='ew')
        # frame幅をウィンドウ幅に広げて伸縮可能に(第一引数に列番号、第二引数はその列をどのくらい広げるかの割合)
        target_url_frame.columnconfigure(0, weight=1)

        # 「開始URL」のラベル
        tk.Label(
            target_url_frame,
            text='開始URL',
        ).grid(column=0, row=0, pady=(0, 2), sticky='w')

        # 「開始URL」の変数(入力欄表示用)
        target_url_var = tk.StringVar()
        # 空白文字列はEntry内部の左右余白を表現
        target_url_var.set(' '+self.crawler.start_url+' ')

        # 「開始URL」の入力欄(読み取り専用)
        target_url = tk.Entry(
            target_url_frame,
            textvariable=target_url_var,
            state='readonly',
        )
        target_url.grid(column=0, row=1, ipady=5, sticky='ew')

        # 「開始URL」のスクロールバー
        target_url_xbar = tk.Scrollbar(
            target_url_frame, orient=tk.HORIZONTAL, command=target_url.xview)
        target_url['xscrollcommand'] = target_url_xbar.set
        target_url_xbar.grid(column=0, row=2, sticky='ew')

        # 「ファイルの保存先」配置用のフレーム
        output_path_frame = tk.Frame(frame)
        output_path_frame.grid(column=0, row=1, sticky='ew')
        # frame幅をウィンドウ幅に広げて伸縮可能に(第一引数に列番号、第二引数はその列をどのくらい広げるかの割合)
        output_path_frame.columnconfigure(0, weight=1)

        # 「ファイルの保存先」のラベル
        tk.Label(
            output_path_frame,
            text='ファイルの保存先',
        ).grid(column=0, row=0, pady=(0, 2), sticky='w')

        # 「ファイルの保存先」の変数(値の更新/入力欄表示用)
        self.output_path_var = tk.StringVar()
        # 空白文字列はEntry内部の左右余白を表現
        self.output_path_var.set(' '+self.crawler.output_file_path+' ')

        # 「ファイルの保存先」の入力欄(読み取り専用)
        output_path = tk.Entry(
            output_path_frame,
            textvariable=self.output_path_var,
            state='readonly',
        )
        output_path.grid(column=0, row=1, ipady=5, sticky='ew')

        # 「ファイルの保存先」のスクロールバー
        output_path_xbar = tk.Scrollbar(
            output_path_frame, orient=tk.HORIZONTAL, command=output_path.xview)
        output_path['xscrollcommand'] = output_path_xbar.set
        output_path_xbar.grid(column=0, row=2, sticky='ew')

        # 「メッセージ」配置用のラベルフレーム
        message_frame = tk.LabelFrame(
            frame,
            text='メッセージ',
            borderwidth=1,
        )
        message_frame.grid(
            column=0,
            row=2,
            pady=(10, 0),
            sticky='w',
        )

        # 「メッセージ」の変数(ラベル表示用)
        self.message_var = tk.StringVar()
        self.message_var.set('Crawler待機中')
        # 「メッセージ」のテキスト部分はラベルとして配置
        self.message = tk.Label(
            message_frame,
            textvariable=self.message_var,
            width=30,
            padx=5,
            pady=5,
            anchor='w'
        )
        self.message.grid(column=0, row=0, sticky='w')

        # 各ボタン配置用のフレーム
        btn_frame = tk.Frame(frame)
        btn_frame.grid(column=0, row=3, pady=(15, 20), sticky='w')

        # ボタンサイズ(幅は文字数が異なるのでwidth、高さは微調整ができるpadyで調整)
        btn_w = 8
        pad_y = 4

        # 「開始」ボタン
        self.start_btn = tk.Button(
            btn_frame,
            text='開始',
            command=self.start,
            width=btn_w,
            pady=pad_y
        )
        self.start_btn.grid(column=0, row=0)

        # 「停止」ボタン
        self.pause_btn = tk.Button(
            btn_frame,
            text='停止',
            command=self.pause,
            width=btn_w,
            pady=pad_y,
            state='disabled',
        )
        self.pause_btn.grid(column=1, row=0, padx=10)

        # 「取消」ボタン
        self.cancel_btn = tk.Button(
            btn_frame,
            text='取消',
            command=self.cancel,
            width=btn_w,
            pady=pad_y,
            state='disabled',
        )
        self.cancel_btn.grid(column=2, row=0)

        # 「ﾛｸﾞｸﾘｱ」ボタン
        self.clear_btn = tk.Button(
            btn_frame,
            text='ﾛｸﾞｸﾘｱ',
            command=self.clear_log,
            width=btn_w,
            pady=pad_y,
        )
        self.clear_btn.grid(column=4, row=0, padx=(30, 0))

        # 「終了」ボタン
        tk.Button(
            btn_frame,
            text='終了',
            command=self.quit,
            width=btn_w,
            pady=pad_y,
        ).grid(column=5, row=0, padx=(10, 0))

    def start(self):
        """
        「開始」ボタン押下時の処理

        Note:
            ボタンを押すたびスレッド作成/スクレイピング処理を行うため、
            処理終了後も連続実行が可能
        """

        # スレッド作成/スクレイピング処理の呼び出し
        self.crawler.start_crawler_thread()

        # 処理開始に際してボタンの状態とメッセージの更新
        self.start_btn.config(state='disabled')
        self.pause_btn.config(state='normal')
        self.cancel_btn.config(state='normal')
        self.clear_btn.config(state='disabled')
        self.message_var.set('Crawler処理中...')

        # 「開始」ボタン押下後、2秒後に指定された関数を呼び出す
        self.start_btn.after(2000, self.confirm_crawler_status)

    def confirm_crawler_status(self):
        """crawlerモジュールの処理状況を一定間隔で監視/状況に応じた処理"""

        # statusの正常終了/取消終了/エラー終了を検知した場合
        if self.crawler.crawler_status == self.crawler.status[0] or \
                self.crawler.crawler_status == self.crawler.status[3]:
            # GUIの初期化/値更新
            self.initialize_gui()
            # 処理終了
            return None

        # 「開始」ボタン押下後、2秒後に再度自身を呼び出すため、処理開始から2秒間隔でstatusを監視
        # 処理終了を検知した場合は上記のreturnで監視終了(GUIが閉じるまでループするのを防ぐ)
        self.start_btn.after(2000, self.confirm_crawler_status)

    def initialize_gui(self):
        """GUIの初期化と値の更新"""

        # 出力パス(現在日時)の更新してGUIに反映
        self.crawler.create_output_path()
        self.output_path_var.set(' '+self.crawler.output_file_path+' ')

        self.start_btn.config(state='normal')
        # disabled状態ではボタンテキストを変更できないので順番に注意
        self.pause_btn.config(text='停止')
        self.pause_btn.config(state='disabled')
        self.cancel_btn.config(state='disabled')
        self.clear_btn.config(state='normal')

        # 「メッセージ」の表示内容更新
        self.message_var.set('Crawler処理終了')

    def pause(self):
        """「停止/再開」ボタン押下時の処理"""

        # ボタン押下時、イベントの内部フラグがTrue(処理中)の場合
        if self.crawler.crawler_event.is_set():
            # 内部フラグをFalseに設定(Crawlerモジュールではこれを検知してwait())
            self.crawler.crawler_event.clear()
            # ボタンテキストを「再開」に変更
            self.pause_btn.config(text='再開')
            # メッセージの表示内容更新
            self.message_var.set('Crawler停止中')
        # ボタン押下時、イベントの内部フラグがFalse(停止中)の場合
        else:
            # 内部フラグをTrueに設定(Crawlerモジュールではこれを検知してwait解除)
            self.crawler.crawler_event.set()
            # ボタンテキストの変更
            self.pause_btn.config(text='停止')
            # メッセージの表示内容更新
            self.message_var.set('Crawler処理中...')

    def cancel(self):
        """「取消」ボタン押下時の処理"""

        # 内部フラグをFalseに設定(Crawlerモジュールではこれを検知してwait())
        self.crawler.crawler_event.clear()

        # tkinterのメッセージボックスにより実行確認/確認結果の代入
        ask_result = messagebox.askokcancel(
            '確認',
            'Crawlerの処理を取消しますか？\n'
            '処理の途中で終了する場合、抽出データはファイル保存されません。'
        )

        # 確認結果がTrueの場合(「OK」ボタン押下)
        if ask_result:
            # 内部フラグをTrueに設定
            self.crawler.crawler_event.set()
            # Crawlerモジュールの全体処理フラグをFalseに設定
            # 同モジュールではこれを検知してraise終了
            self.crawler.crawler_alive_flag = False
            # スレッドが終了するまでCrawlerモジュールの処理を待機
            self.crawler.crawler_thread.join()
        # 確認結果がFalseの場合(「cancel」or「✕」ボタン押下)
        else:
            # ボタンテキストが「停止」の場合(「停止」ボタン以外で停止されている場合)
            if self.pause_btn['text'] == '停止':
                # 内部フラグをTrueに設定(Crawlerモジュールではこれを検知してwait解除)
                self.crawler.crawler_event.set()

    def clear_log(self):
        """「ﾛｸﾞｸﾘｱ」ボタン押下時の処理"""

        # tkinterのメッセージボックスにより実行確認/確認結果の代入
        ask_result = messagebox.askokcancel(
            '確認',
            'ログウィンドウの表示内容をクリアしますか？'
        )

        # 確認結果がTrueの場合(「OK」ボタン押下)
        if ask_result:
            # 読み取り専用から書き込み可能に変更
            self.scrolled_text.config(state='normal')
            # 1行目から末尾まで削除
            self.scrolled_text.delete(0., tk.END)
            # 書き込み可能から読み取り専用に変更
            self.scrolled_text.config(state='disabled')

    def quit(self):
        """「終了」ボタン押下時の処理"""

        # ボタン押下時、statusが処理中/停止中の場合
        if self.crawler.crawler_status == self.crawler.status[1] or \
                self.crawler.crawler_status == self.crawler.status[2]:

            # 内部フラグをFalseに設定(Crawlerモジュールではこれを検知してwait())
            self.crawler.crawler_event.clear()

            # tkinterのメッセージボックスにより実行確認/確認結果の代入
            ask_result = messagebox.askokcancel(
                '確認',
                'アプリを終了しますか？\n'
                '処理の途中で終了する場合、抽出データはファイル保存されません。'
            )

            # 確認結果がTrueの場合(「OK」ボタン押下)
            if ask_result:
                # 内部フラグをTrueに設定
                self.crawler.crawler_event.set()
                # Crawlerモジュールの全体処理フラグをFalseに設定
                # 同モジュールではこれを検知してraise終了
                self.crawler.crawler_alive_flag = False
                # スレッドが終了するまでCrawlerモジュールの処理を待機
                self.crawler.crawler_thread.join()
                # GUIを閉じる
                self.master.destroy()
            # 確認結果がFalseの場合(「cancel」or「✕」ボタン押下)
            else:
                # ボタンテキストが「停止」の場合(「停止」ボタン以外で停止されている場合)
                if self.pause_btn['text'] == '停止':
                    # 内部フラグをTrueに設定(Crawlerモジュールではこれを検知してwait解除)
                    self.crawler.crawler_event.set()
        # ボタン押下時、statusが処理中/停止中以外の場合
        else:
            # GUIを閉じる(メッセージボックスを表示せずに)
            self.master.destroy()


class LogWindowUi(object):
    """
    ログウィンドウ部分におけるwidget(scrolledtext)の定義。

    Note:
        scrolledtextは、定義時にタグを設定、テキストinsert時にタグに応じた文字色等を設定可能。
        今回は、定義時に発生したログレベルをタグに設定、後述するinsert時にERRORタグの場合は文字色を変更。
    """

    def __init__(self, frame, crawler, log_handler):
        """
        args:
            frame: Appクラスで定義した「Crawlerコントロール」用のラベルフレーム
            crawler: Appクラスでインスタンス化されたcrawlerモジュール
            log_handler: Appクラスでインスタンス化されたlog_handlerモジュール
            log_queue: log_handlerモジュールにおけるログ格納用のqueue
            queue_handler: log_handlerモジュールでインスタンス化されたQueueHandlerクラス
        """

        # 「ログウィンドウ」用のフレームを属性定義
        self.frame = frame
        # crawlerモジュールを属性定義
        self.crawler = crawler
        # log_handlerモジュールを属性定義
        self.log_handler = log_handler
        # queueを属性定義
        self.log_queue = self.log_handler.log_queue
        # QueueHandlerを属性定義
        self.queue_handler = self.log_handler.queue_handler

        # 「ログウィンドウ」のスクロールドテキスト
        self.scrolled_text = ScrolledText(
            self.frame,
            height=16,
            state='disabled',
        )
        self.scrolled_text.grid(column=0, row=0, sticky='nesw')
        # 「ERROR」タグに文字色を指定
        self.scrolled_text.tag_config('ERROR', foreground='red')

        # 「ログウィンドウ」用のフレームが読み込まれた0.1秒後に指定された関数を呼び出す
        self.frame.after(100, self.get_log_queue)

    def get_log_queue(self):
        """log_handlerモジュールのqueueの監視/ログの取り出し"""

        while True:
            try:
                # queueからログを取り出す
                record = self.log_queue.get(block=False)
            # queueが空になったらループから抜ける
            except queue.Empty:
                break
            # 取り出せた場合
            else:
                # スクロールドテキストに表示
                self.display_log(record)

        # 「ログウィンドウ」用のフレーム読み込み後、0.1秒後に再度自身を呼び出すため、
        # 処理開始から0.1秒間隔でqueueからログの取り出しを試みる
        self.frame.after(100, self.get_log_queue)

    def display_log(self, record):
        """スクロールドテキストへのログ表示"""

        # 読み取り専用から書き込み可能に状態変更
        self.scrolled_text.configure(state='normal')
        # format()によりログのフォーマット適用/str型変換
        message = self.queue_handler.format(record)
        # ログの挿入(表示)/ログレベルをタグとして設定
        self.scrolled_text.insert(tk.END, message + '\n', record.levelname)
        # 書き込み可能から読み取り専用に状態変更
        self.scrolled_text.configure(state='disabled')
        # スクロールドテキストを末尾にy軸移動
        self.scrolled_text.yview(tk.END)


class App(object):
    """
    GUIの全体管理

    Note
        レイアウトイメージについて
            全体のレイアウトは、上部にCrawlerコントロール、下部にログウィンドウ

            初めに土台として縦方向のPanedWindowを配置
            その上に上記レイアウト用のLabelFrameを上下に配置するイメージ

        row/column configure()について
            伸縮比率weightを設定
            デフォルトの0(伸縮しない)から変更することで、
            GUIウィンドウに連動して内部widget(ここではLabelFrame)も伸縮
    """

    def __init__(self, master):
        self.master = master

        # フォントの一括設定
        font_family = 'MSゴシック'
        font_size = 11
        # tkの設定
        self.master.option_add('*font', [font_family, font_size])
        # ttkの設定
        style = ttk.Style()
        style.configure('Font.TLabelframe.Label', font=(font_family, font_size))

        # 大元になるTkオブジェクトに設定することでGUI内の要素とウィンドウが連動
        # frameやwidgetだけに設定してもウィンドウサイズと連動せず伸縮もしない
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        # Crawlerモジュールのインスタンス化
        crawler = Crawler()

        # log_handlerの属性定義
        log_handler = crawler.log_handler

        # 全体の土台として縦方向のPanedWindowを配置
        vertical_pane = ttk.PanedWindow(master, orient='vertical')
        vertical_pane.grid(column=0, row=0, sticky='nesw', padx=5, pady=5)

        # 「Crawlerコントロール」用のラベルフレーム
        control_frame = ttk.LabelFrame(
            vertical_pane, text='Crawlerコントロール', style='Font.TLabelframe')
        # frame幅をウィンドウ幅に広げて伸縮可能に(第一引数に列番号、第二引数はその列をどのくらい広げるかの割合)
        control_frame.columnconfigure(0, weight=1)
        # 前述のPanedWindowに配置
        vertical_pane.add(control_frame, weight=0)

        # 「ログウィンドウ」用のラベルフレーム
        log_window_frame = ttk.LabelFrame(
            vertical_pane, text='ログウィンドウ', style='Font.TLabelframe')
        # frame幅をウィンドウ幅に広げて伸縮可能に(第一引数に列番号、第二引数はその列をどのくらい広げるかの割合)
        log_window_frame.columnconfigure(0, weight=1)
        # frame高をウィンドウ高に広げて伸縮可能に(第一引数に行番号、第二引数はその行をどのくらい広げるかの割合)
        log_window_frame.rowconfigure(0, weight=1)
        # 前述のPanedWindowに配置
        vertical_pane.add(log_window_frame, weight=1)

        # LogWindowクラスのインスタンス化(widgetの定義/表示)
        self.log_window = LogWindowUi(log_window_frame, crawler, log_handler)

        # ControlUiクラスのインスタンス化(widgetの定義/表示)
        self.control = ControlUi(
            control_frame, crawler, master, self.log_window, log_handler
        )

        # ウィンドウ「✕」ボタンの処理(WM_DELETE_WINDOW)を特定の処理に置き換える
        master.protocol('WM_DELETE_WINDOW', self.control.quit)


def main():
    # tkinterのインスタンス化
    root = tk.Tk()
    # ウィンドウに表示するアプリ名
    root.title('Crawler GUI')
    # ウィンドウの横幅
    app_w = 600
    # ウィンドウの縦幅
    app_h = 600
    # 実行環境(PC)の画面サイズ(横)を取得
    pc_w = root.winfo_screenwidth()
    # ウィンドウの表示サイズ/表示位置を指定
    root.geometry(
        # 横サイズ×縦サイズ+表示位置x座標(画面中央)+表示位置y座標(画面上から+10)
        f'{app_w}x{app_h}+{int((pc_w - app_w) * .5)}+10'
    )
    # ウィンドウの最小サイズ
    root.minsize(width=app_w, height=app_h)
    # ウィンドウに表示するアイコン
    try:
        root.iconbitmap('images/icon.ico')
    except tk.TclError:
        # ファイルが読み込めない場合はpassしてtkinterのデフォルトアイコンを表示
        pass
    # Appクラスのインスタンス化によりGUI全体を定義
    app = App(master=root)
    # ループによりGUI表示
    app.master.mainloop()


if __name__ == '__main__':
    main()
