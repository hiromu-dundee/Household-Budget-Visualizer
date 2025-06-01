# complete

import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import json
from tkinter import messagebox
import japanize_matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from tkinter import scrolledtext


class BudgetCarouselApp:
    def __init__(self, root):
        self.root = root
        self.root.title("月別家計簿カルーセルビューア")

        self.data_by_month = []
        self.month_labels = []
        self.data_by_day = []
        self.day_labels = []
        self.current_index = 0
        self.current_filename = None
        self.budget_data = {}
        self.is_circle = False
        self.is_day_mode = False

        self.fixed_categories = []
        self.variable_categories = []
        self.monthly_income_data = {}
        colors_map = plt.colormaps["tab20"]  # カテゴリごとの色マップ
        self.category_colors = [colors_map(i / 30) for i in range(30)]

        # ボタンを配置するフレームを作成
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)  # フレーム全体の上部に少し余白

        self.btn_load = tk.Button(
            button_frame, text="CSVを読み込む", command=self.load_csv
        )
        self.btn_load.pack(side=tk.LEFT, padx=5)  # 左から配置し、左右に少し余白

        self.btn_set_budget = tk.Button(
            button_frame, text="予算を設定", command=self.open_budget_settings
        )
        self.btn_set_budget.pack(side=tk.LEFT, padx=5)  # 左から配置し、左右に少し余白

        self.btn_set_fv_config = tk.Button(
            button_frame,
            text="固定費・変動費設定",
            command=self.open_fixed_variable_settings,
        )
        self.btn_set_fv_config.pack(
            side=tk.LEFT, padx=5
        )  # 左から配置し、左右に少し余白

        # 新しいボタン：カテゴリ別推移グラフ
        self.btn_category_trends = tk.Button(
            button_frame,
            text="カテゴリ別推移グラフ",
            command=self.show_category_trends,
            state=tk.DISABLED,
        )
        self.btn_category_trends.pack(side=tk.LEFT, padx=5)

        self.frame_plot = tk.Frame(root)
        self.frame_plot.pack(fill=tk.BOTH, expand=True)

        self.frame_controls = tk.Frame(root)
        self.frame_controls.pack()

        self.btn_prev = tk.Button(
            self.frame_controls,
            text="◀ 前へ",
            command=self.prev_month,
            state=tk.DISABLED,
        )
        self.btn_prev.pack(side=tk.LEFT, padx=5)

        self.label_month = tk.Label(self.frame_controls, text="読み込み待ち")
        self.label_month.pack(side=tk.LEFT, padx=5)

        self.btn_next = tk.Button(
            self.frame_controls,
            text="次へ ▶",
            command=self.next_month,
            state=tk.DISABLED,
        )
        self.btn_next.pack(side=tk.LEFT, padx=5)

        self.btn_circle = tk.Button(
            self.frame_controls,
            text="棒グラフに切り替え" if self.is_circle else "円グラフに切り替え",
            command=self.toggle_graph,
            state=tk.DISABLED,
        )
        self.btn_circle.pack(side=tk.LEFT, padx=5)

        # self.btn_expense = tk.Button(self.frame_controls, text="支出追加", command=self._open_expense_input_window, state=tk.DISABLED)
        # self.btn_expense.pack(side=tk.LEFT, padx=5)

        self.btn_expense = tk.Button(
            self.frame_controls,
            text="支出追加",
            command=self._open_expense_input_window,
            state=tk.DISABLED,
        )
        self.btn_expense.pack(side=tk.LEFT, padx=5)

        # ボタン追加
        self.btn_toggle_day = tk.Button(
            self.frame_controls,
            text="日別表示",
            command=self.toggle_day_mode,
            state=tk.DISABLED,
        )
        self.btn_toggle_day.pack(side=tk.LEFT, padx=5)

        self.label_warning = tk.Label(
            self.frame_controls, text="", fg="red", font=("Helvetica", 12, "bold")
        )
        self.label_warning.pack(side=tk.LEFT, padx=10)

        # # --- データ入力と書き込み部分 ---
        # # ここに self.frame_input の定義を移動します
        # self.frame_input = tk.LabelFrame(root, text="新しい支出の追加") # ラベルフレームで囲む
        # self.frame_input.pack(pady=10, padx=10, fill=tk.X)

        # # 入力フィールドのラベルとエントリー
        # tk.Label(self.frame_input, text="日付 (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        # self.entry_date = tk.Entry(self.frame_input, width=20)
        # self.entry_date.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        # tk.Label(self.frame_input, text="値段:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        # self.entry_price = tk.Entry(self.frame_input, width=20)
        # self.entry_price.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # tk.Label(self.frame_input, text="物品:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        # self.entry_item = tk.Entry(self.frame_input, width=20)
        # self.entry_item.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        # tk.Label(self.frame_input, text="カテゴリ:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        # self.entry_category = tk.Entry(self.frame_input, width=20)
        # self.entry_category.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        # self.selected_input_category = tk.StringVar(self.frame_input)
        # self.selected_input_category.set("カテゴリを選択") # 初期表示テキスト
        # self.category_options_menu = tk.OptionMenu(
        #     self.frame_input,
        #     self.selected_input_category,
        #     "カテゴリを選択", # 最初のダミーオプション
        #     command=self._on_category_select # 選択時のコールバック
        # )
        # self.category_options_menu.config(width=15) # 幅を調整
        # self.category_options_menu.grid(row=3, column=2, padx=5, pady=2, sticky="w")

        # tk.Label(self.frame_input, text="備考:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        # self.entry_notes = tk.Entry(self.frame_input, width=20)
        # self.entry_notes.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        # self.btn_write = tk.Button(self.frame_input, text="データを書き込む", command=self.write_data_to_csv, state=tk.DISABLED)
        # self.btn_write.grid(row=5, column=0, columnspan=2, pady=5)

        # --- 検索機能のUIを追加 (重複部分を削除し、適切な位置に配置) ---
        self.frame_search = tk.Frame(self.root)  # self.root を指定
        self.frame_search.pack(pady=10)

        self.label_search = tk.Label(self.frame_search, text="備考検索:")
        self.label_search.pack(side=tk.LEFT, padx=5)

        self.entry_search_remark = tk.Entry(self.frame_search, width=15)
        self.entry_search_remark.pack(side=tk.LEFT, padx=5)

        # 日付範囲検索フィールド
        self.label_start_date = tk.Label(self.frame_search, text="開始日 (YYYY-MM-DD):")
        self.label_start_date.pack(side=tk.LEFT, padx=5)
        self.entry_start_date = tk.Entry(self.frame_search, width=15)
        self.entry_start_date.pack(side=tk.LEFT, padx=5)

        self.label_end_date = tk.Label(self.frame_search, text="終了日 (YYYY-MM-DD):")
        self.label_end_date.pack(side=tk.LEFT, padx=5)
        self.entry_end_date = tk.Entry(self.frame_search, width=15)
        self.entry_end_date.pack(side=tk.LEFT, padx=5)

        self.btn_search_remark = tk.Button(
            self.frame_search, text="検索", command=self.search_remark
        )
        self.btn_search_remark.pack(side=tk.LEFT, padx=5)

        self.text_search_results = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, height=10, width=80
        )

        self.load_budget_data()
        self.load_fixed_variable_config()  # 固定費・変動費の設定を読み込む

    def load_csv(self, answer=0):  # answer引数はそのまま
        if answer == 0:
            filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
            if not filename:  # ファイル選択がキャンセルされた場合
                return
            self.current_filename = filename
        else:
            filename = self.current_filename

        if not filename:  # current_filenameがNoneの場合など
            return

        self.process_csv_data(filename)  # CSVデータの処理を行う

        money_data = {}
        try:
            with open(filename, encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames or not all(
                    col in reader.fieldnames for col in ["日付", "値段", "カテゴリ"]
                ):
                    print(
                        "エラー: CSVファイルに必要な列（日付, 値段, カテゴリ）が含まれていません。"
                    )
                    return

                for row in reader:
                    try:
                        date_str = row["日付"]
                        price_str = row["値段"]
                        category = row["カテゴリ"]

                        if (
                            not date_str or not price_str or category is None
                        ):  # 空のデータをスキップ
                            print(f"警告: 不完全な行をスキップしました: {row}")
                            continue

                        date = date_str.split("-")
                        if len(date) < 2:  # YYYY-MM 形式でない場合
                            print(f"警告: 日付形式が不正な行をスキップしました: {row}")
                            continue
                        year, month, day = date[0], date[1], date[2]
                        price = int(price_str)

                        if year not in money_data:
                            money_data[year] = {}
                        if month not in money_data[year]:
                            money_data[year][month] = {}
                        if day not in money_data[year][month]:
                            money_data[year][month][day] = {}
                        if category not in money_data[year][month][day]:
                            money_data[year][month][day][category] = []
                        money_data[year][month][day][category].append(price)
                    except ValueError:
                        print(
                            f"警告: '値段'の変換に失敗した行をスキップしました: {row}"
                        )
                        continue
                    except Exception as e:
                        print(
                            f"警告: 行の処理中にエラーが発生しました: {row}, エラー: {e}"
                        )
                        continue
        except FileNotFoundError:
            print(f"エラー: ファイルが見つかりません: {filename}")
            return
        except Exception as e:
            print(f"エラー: CSVファイルの読み込み中に予期せぬエラーが発生しました: {e}")
            return

        if not money_data:
            print("読み込むデータがありませんでした。")
            return

        # データ整理
        # for year in money_data:
        #     for month in money_data[year]:
        #         for category in money_data[year][month]:
        #             money_data[year][month][category] = sum(money_data[year][month][category])

        all_categories = sorted(
            set(
                c
                for y_data in money_data.values()
                for m_data in y_data.values()
                for d_data in m_data.values()
                for c in d_data
                if c != "収入"
            )
        )
        self.all_categories = all_categories
        self.money_data = money_data  # 他のメソッドで使えるように保存

        # --- カテゴリごとに色を固定 ---
        colors_map = plt.colormaps["tab20"]
        self.category_color_dict = {
            c: colors_map(i / max(1, len(all_categories)))
            for i, c in enumerate(all_categories)
        }

        # --- 日別データ ---
        self.data_by_day = []
        self.day_labels = []
        sorted_days = sorted(
            f"{year}-{month}-{day}"
            for year in money_data
            for month in money_data[year]
            for day in money_data[year][month]
        )
        for d in sorted_days:
            y, mo, da = d.split("-")
            day_data = money_data.get(y, {}).get(mo, {}).get(da, {})
            values = []
            for c in all_categories:
                v = day_data.get(c, 0)
                if isinstance(v, dict):
                    v = sum(v.values())
                elif isinstance(v, list):
                    v = sum(v)
                values.append(v)
            self.data_by_day.append((list(all_categories), list(values)))
            self.day_labels.append(d)

        # --- 月別データ ---
        self.data_by_month = []
        self.month_labels = []
        sorted_months = sorted(
            f"{year}-{month}" for year in money_data for month in money_data[year]
        )
        for m in sorted_months:
            y, mo = m.split("-")
            # 月内の全日・全カテゴリを合計する
            month_data = {}
            for day in money_data.get(y, {}).get(mo, {}):
                for c in all_categories:
                    v = money_data[y][mo][day].get(c, 0)
                    if isinstance(v, dict):
                        v = sum(v.values())
                    elif isinstance(v, list):
                        v = sum(v)
                    month_data[c] = month_data.get(c, 0) + v
            values = [month_data.get(c, 0) for c in all_categories]
            self.data_by_month.append((list(all_categories), list(values)))
            self.month_labels.append(m)

        self.current_index = 0
        self.btn_circle.config(state=tk.NORMAL)
        # self.btn_write.config(state=tk.NORMAL)
        self.btn_toggle_day.config(state=tk.NORMAL)  # aaaaaaaaaaaaaaaaaaaaaa
        self.btn_expense.config(state=tk.NORMAL)
        self.update_buttons()
        self.draw_plot()

        # # 月別データ準備
        # self.data_by_month = []
        # self.month_labels = []
        # all_categories = sorted(list(set(
        #     c for y_data in money_data.values()
        #       for m_data in y_data.values()
        #       for c in m_data if c != '収入' # '収入'を除外
        # )))
        # self.all_categories = all_categories  # 全カテゴリを保存 (収入以外)

        # 年と月を数値としてソートするためにキーを生成
        def sort_key_month(ym_str):
            y, m = map(int, ym_str.split("-"))
            return y * 100 + m

        # sorted_monthsの生成を修正
        # money_dataのキー（年、月）は文字列なので、適切にソートするために数値変換を考慮
        raw_months = []
        for year_str, months_data in money_data.items():
            for month_str in months_data.keys():
                raw_months.append(f"{year_str}-{month_str}")

        self.sorted_months = sorted(list(set(raw_months)), key=sort_key_month)

        for m_label in self.sorted_months:
            y, mo = m_label.split("-")
            month_data = money_data.get(y, {}).get(mo, {})
            values = [
                month_data.get(c, 0) for c in self.all_categories
            ]  # all_categoriesは収入以外
            self.data_by_month.append((self.all_categories, values))  # ここは元のまま
            self.month_labels.append(m_label)  # month_labelsも更新

        self.current_index = 0
        self.update_buttons()  # 既存のボタン更新処理
        self.draw_plot()  # 既存のプロット更新処理

        self.btn_circle.config(state=tk.NORMAL)
        self.btn_expense.config(state=tk.NORMAL)
        # self.btn_write.config(state=tk.NORMAL)
        # self.btn_category_trends.config(state=tk.NORMAL) # ★ 新しいボタンを有効化

    def draw_plot(self):
        for widget in self.frame_plot.winfo_children():
            widget.destroy()

        if self.is_day_mode:
            categories, actual_values = self.data_by_day[self.current_index]
            label = self.day_labels[self.current_index]
        else:
            categories, actual_values = self.data_by_month[self.current_index]
            label = self.month_labels[self.current_index]

        # categories, actual_values = self.data_by_month[self.current_index]

        fig, ax = plt.subplots(figsize=(8, 6))  # グラフサイズを少し大きくして見やすく

        bar_width = 0.35
        index = range(len(categories))

        budget_values = [self.budget_data.get(c, 0) for c in categories]

        # --- カテゴリの色分けロジックを固定費/変動費で変更 ---
        actual_bar_colors = []
        for category in categories:
            if category in self.fixed_categories:
                actual_bar_colors.append("#4CAF50")  # 固定費の色 (緑系)
            elif category in self.variable_categories:
                actual_bar_colors.append("#FF5722")  # 変動費の色 (オレンジ系)
            else:
                actual_bar_colors.append("gray")  # どちらにも属さないカテゴリ

        # 実績の棒 (左側)
        rects1 = ax.bar(
            [i - bar_width / 2 for i in index],
            actual_values,
            bar_width,
            label="実績",
            color=actual_bar_colors,
        )

        # 予算の棒 (右側)
        rects2 = ax.bar(
            [i + bar_width / 2 for i in index],
            budget_values,
            bar_width,
            label="予算",
            color="lightcoral",
        )

        # --- 凡例を修正 ---
        # 実績の色はカテゴリごとに異なるので、カテゴリの凡例は削除
        # 固定費・変動費の色を示すためのダミープロットを追加して凡例を作成
        legend_elements = [
            plt.Line2D([0], [0], color="#4CAF50", lw=4, label="実績（固定費）"),
            plt.Line2D([0], [0], color="#FF5722", lw=4, label="実績（変動費）"),
            plt.Line2D([0], [0], color="lightcoral", lw=4, label="予算"),
        ]
        # ax.legend(handles=legend_elements, title='凡例', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.legend(
            handles=legend_elements,
            title="凡例",
            bbox_to_anchor=(0.7, 0.9),
            loc="center left",
            borderaxespad=1,
        )
        # --- 凡例修正ここまで ---

        if self.is_day_mode:
            date = label.split("-")
            ax.set_title(
                f"{date[0]}年{date[1]}月{date[2]}日 の日別支出実績と予算", x=0.5, y=1.05
            )
        else:
            date = label.split("-")
            ax.set_title(f"{date[0]}年{date[1]}月 の月別支出実績と予算", x=0.5, y=1.05)
        ax.set_ylabel("金額（円）")
        ax.set_xlabel("カテゴリ")
        ax.set_xticks(index)  # X軸のティック位置をカテゴリのインデックスに合わせる
        ax.set_xticklabels(categories, rotation=45)

        canvas = FigureCanvasTkAgg(fig, master=self.frame_plot)
        canvas.draw()
        canvas.get_tk_widget().pack()

        self.label_month.config(text=label)

    def draw_circle(self):
        for widget in self.frame_plot.winfo_children():
            widget.destroy()

        if self.is_day_mode:
            categories, values = self.data_by_day[self.current_index]
            label = self.day_labels[self.current_index]
        else:
            categories, values = self.data_by_month[self.current_index]
            label = self.month_labels[self.current_index]

        # categories, values = self.data_by_month[self.current_index]

        # 0円以外のみ抽出
        filtered = [(c, v) for c, v in zip(categories, values) if v > 0]
        if filtered:
            filtered_categories, filtered_values = zip(*filtered)
        else:
            filtered_categories, filtered_values = [], []

        # pie_colors = [self.category_color_dict[c] for c in filtered_categories]

        fig, ax = plt.subplots(figsize=(8, 6))

        if filtered_values:
            pie_colors = [self.category_color_dict[c] for c in filtered_categories]
            ax.pie(
                filtered_values,
                labels=filtered_categories,
                autopct="%1.1f%%",
                startangle=90,
                counterclock=False,
                colors=pie_colors,
            )

            ax.axis("equal")
            fig.legend()
        else:
            ax.text(
                0.5, 0.5, "データがありません", ha="center", va="center", fontsize=18
            )
            ax.axis("off")

        if self.is_day_mode:
            date = label.split("-")
            ax.set_title(
                f"{date[0]}年{date[1]}月{date[2]}日 の日別支出割合", x=0.5, y=1.05
            )
        else:
            date = label.split("-")
            ax.set_title(f"{date[0]}年{date[1]}月 の月別支出割合", x=0.5, y=1.05)

        canvas = FigureCanvasTkAgg(fig, master=self.frame_plot)
        canvas.draw()
        canvas.get_tk_widget().pack()

        self.label_month.config(text=label)

    def draw_graph(self):
        if self.is_circle:
            self.draw_circle()
        else:
            self.draw_plot()

        self._update_balance_display()  # グラフ描画後に収支表示を更新

    def toggle_graph(self):
        # グラフの状態を切り替えて再描画
        self.is_circle = not self.is_circle
        (
            self.btn_circle.config(text="棒グラフに切り替え")
            if self.is_circle
            else self.btn_circle.config(text="円グラフに切り替え")
        )
        self.draw_graph()

    def toggle_day_mode(self):
        self.is_day_mode = not self.is_day_mode
        if self.is_day_mode:
            # 月別→日別に切り替えるとき
            if self.month_labels and self.day_labels:
                # 現在の月の1日目を探す
                current_month = self.month_labels[self.current_index]
                # 例: "2024-05"
                for i, d in enumerate(self.day_labels):
                    if d.startswith(current_month + "-"):
                        self.current_index = i
                        break
                else:
                    self.current_index = 0  # 見つからなければ0
            else:
                self.current_index = 0
        else:
            # 日別→月別に戻すときは、その日の月に合わせる
            if self.day_labels and self.month_labels:
                current_day = self.day_labels[self.current_index]
                current_month = current_day[:7]  # "YYYY-MM"
                for i, m in enumerate(self.month_labels):
                    if m == current_month:
                        self.current_index = i
                        break
                else:
                    self.current_index = 0
            else:
                self.current_index = 0

        self.btn_toggle_day.config(text="月別表示" if self.is_day_mode else "日別表示")
        self.draw_graph()
        self.update_buttons()

    def prev_month(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_buttons()
            self.draw_graph()

    def next_month(self):
        data_len = (
            len(self.data_by_day) if self.is_day_mode else len(self.data_by_month)
        )
        if self.current_index < data_len - 1:
            self.current_index += 1
            self.update_buttons()
            self.draw_graph()

    def update_buttons(self):
        data_len = (
            len(self.data_by_day) if self.is_day_mode else len(self.data_by_month)
        )
        self.btn_prev.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.btn_next.config(
            state=tk.NORMAL if self.current_index < data_len - 1 else tk.DISABLED
        )

    # def write_data_to_csv(self):
    #     if not self.current_filename:
    #         # ファイルが選択されていない場合のエラー処理
    #         return

    #     prev_index = self.current_index
    #     prev_is_circle = self.is_circle

    #     # 入力フィールドからデータを取得
    #     date = self.entry_date.get()
    #     price = self.entry_price.get()
    #     item = self.entry_item.get()
    #     category = self.entry_category.get()
    #     notes = self.entry_notes.get()

    #     # データの検証 (例: 空でないか、数値であるか)
    #     if not all([date, price, item, category]):
    #         # 必須フィールドが空の場合のエラー処理
    #         return

    #     try:
    #         price = int(price)  # 値段を整数に変換
    #     except ValueError:
    #         # 値段が数値でない場合のエラー処理
    #         return

    #     # CSVファイルにデータを追記
    #     try:
    #         with open(self.current_filename, 'a', encoding='utf-8', newline='') as f:
    #             writer = csv.writer(f)
    #             writer.writerow([date, price, item, category, notes])

    #         # 書き込み成功後の処理 (例: メッセージボックスの表示、グラフの更新)

    #     except Exception as e:
    #         # ファイル書き込みエラー処理
    #         print(f"ファイル書き込みエラー: {e}")

    #     self.load_csv(answer=1)  # 書き込み後にデータを再読み込みして更新
    #     self.current_index = min(prev_index, len(self.data_by_month) - 1)
    #     self.is_circle = prev_is_circle
    #     self.draw_graph()

    # --- 予算設定関連のメソッド群 ---

    def load_budget_data(self):
        """
        予算データを 'budget.json' から読み込む。
        ファイルが存在しない場合は空の辞書を初期化する。
        """
        try:
            with open("budget.json", "r", encoding="utf-8") as f:
                self.budget_data = json.load(f)
        except FileNotFoundError:
            self.budget_data = {}  # ファイルがない場合は空の辞書で初期化
        except json.JSONDecodeError:
            messagebox.showwarning(
                "警告",
                "予算ファイル (budget.json) の形式が不正です。新しく作成します。",
            )
            self.budget_data = {}
        except Exception as e:
            messagebox.showerror(
                "エラー", f"予算データの読み込み中にエラーが発生しました: {e}"
            )
            self.budget_data = {}

    def save_budget_data(self):
        """
        現在の予算データを 'budget.json' に保存する。
        """
        try:
            with open("budget.json", "w", encoding="utf-8") as f:
                json.dump(self.budget_data, f, indent=4, ensure_ascii=False)

            self._initialize_budget_for_new_categories()  # 新しいカテゴリの初期化
            self.load_budget_data()  # 保存後に再読み込みして最新の状態にする
            self.draw_plot()  # グラフを更新
            messagebox.showinfo("予算保存", "予算データが保存されました。")
        except Exception as e:
            messagebox.showerror(
                "エラー", f"予算データの保存中にエラーが発生しました: {e}"
            )

    def _initialize_budget_for_new_categories(self):
        """
        新しく読み込まれたカテゴリで、まだ予算が設定されていないものがあれば、
        予算データに0円で初期化する。
        """
        if not hasattr(self, "all_categories") or not self.all_categories:
            return  # カテゴリがまだない場合は何もしない

        for category in self.all_categories:
            if category not in self.budget_data:
                self.budget_data[category] = 0
        # 新しいカテゴリが追加された場合、自動的に保存しない。
        # ユーザーが明示的に「予算を保存」したときに保存される。

    def open_budget_settings(self):
        """
        予算設定用の新しいウィンドウを開く。月ごとの予算は等しいものと仮定する。
        """
        budget_window = tk.Toplevel(self.root)
        budget_window.title("月別カテゴリ予算設定 (共通)")
        budget_window.transient(self.root)
        budget_window.grab_set()

        # 利用可能なカテゴリを取得
        # CSVが読み込まれていない場合は、カテゴリが空になる可能性があるので注意
        available_categories = (
            self.all_categories if hasattr(self, "all_categories") else []
        )
        available_categories = [c for c in available_categories if c != "収入"]

        if not available_categories:
            messagebox.showwarning(
                "警告",
                "CSVデータが読み込まれていないか、支出カテゴリが見つかりません。",
            )
            budget_window.destroy()
            return

        tk.Label(
            budget_window, text="以下のカテゴリの共通月間予算を設定してください:"
        ).pack(pady=5)

        self.budget_entries = {}  # {カテゴリ名: Entryウィジェット} を保持
        self.budget_entry_vars = {}  # {カテゴリ名: StringVar} を保持

        self.frame_budget_entries = tk.Frame(budget_window)
        self.frame_budget_entries.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # 全カテゴリの現在の予算を読み込み、エントリーウィジェットを作成
        # budget_dataは直接カテゴリをキーとして持つようになる
        for i, category in enumerate(available_categories):
            tk.Label(self.frame_budget_entries, text=f"{category}:").grid(
                row=i, column=0, padx=5, pady=2, sticky="w"
            )
            var = tk.StringVar(self.frame_budget_entries)
            # 既存の予算があればそれを設定 (budget_dataはカテゴリが直接キーになる)
            var.set(
                str(self.budget_data.get(category, 0))
            )  # 予算データから直接カテゴリの値を読み込む

            entry = tk.Entry(self.frame_budget_entries, textvariable=var, width=15)
            entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
            self.budget_entries[category] = entry
            self.budget_entry_vars[category] = var

        btn_frame = tk.Frame(budget_window)
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="予算を保存",
            command=lambda: self._save_budget_from_entries_common(budget_window),
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="閉じる", command=budget_window.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def _save_budget_from_entries_common(self, budget_window):
        """
        共通月間予算設定ウィンドウのエントリーから予算データを取得し、保存する。
        """
        new_common_budget = {}
        for category, var in self.budget_entry_vars.items():
            budget_str = var.get()
            if budget_str:
                try:
                    budget_val = int(budget_str)
                    if budget_val < 0:
                        messagebox.showerror(
                            "エラー",
                            f"{category} の予算は0以上の数値で入力してください。",
                        )
                        return
                    new_common_budget[category] = budget_val
                except ValueError:
                    messagebox.showerror(
                        "エラー", f"{category} の予算は数値で入力してください。"
                    )
                    return
            else:
                new_common_budget[category] = 0  # 空欄の場合は0とする

        self.budget_data = new_common_budget  # 予算データを更新
        self.save_budget_data()  # JSONファイルに保存
        budget_window.destroy()  # 予算設定ウィンドウを閉じる

    def _on_category_select(self, selected_category):
        """
        カテゴリ選択ドロップダウンで項目が選択されたときに呼び出される
        選択されたカテゴリをentry_categoryに設定する
        """
        if selected_category != "カテゴリを選択":  # ダミーオプションでなければ
            self.entry_category.delete(0, tk.END)  # 現在の入力値をクリア
            self.entry_category.insert(0, selected_category)  # 選択された値を挿入

    def _update_category_dropdown(self):
        """
        all_categoriesが更新された際に、カテゴリ選択ドロップダウンを更新する
        """
        # 既存のメニューを削除
        if not hasattr(self, "category_options_menu"):
            return

        self.category_options_menu["menu"].delete(0, "end")

        # 新しいカテゴリを追加
        if not self.all_categories:  # カテゴリがない場合
            self.category_options_menu["menu"].add_command(
                label="カテゴリなし",
                command=tk._setit(self.selected_input_category, "カテゴリなし"),
            )
            self.selected_input_category.set("カテゴリなし")
            return

        for category in [
            "カテゴリを選択"
        ] + self.all_categories:  # ダミーオプションを先頭に追加
            self.category_options_menu["menu"].add_command(
                label=category,
                command=tk._setit(self.selected_input_category, category),
            )

        # 選択中の値をリセット (オプション)
        self.selected_input_category.set("カテゴリを選択")

    def load_fixed_variable_config(self):
        """
        固定費・変動費のカテゴリ設定を 'fv_config.json' から読み込む。
        """
        try:
            with open("fv_config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                self.fixed_categories = config.get("fixed_categories", [])
                self.variable_categories = config.get("variable_categories", [])
        except FileNotFoundError:
            # ファイルがない場合はデフォルト値を設定 (空リスト)
            self.fixed_categories = []
            self.variable_categories = []
        except json.JSONDecodeError:
            messagebox.showwarning(
                "警告",
                "固定費・変動費設定ファイル (fv_config.json) の形式が不正です。新しく作成します。",
            )
            self.fixed_categories = []
            self.variable_categories = []
        except Exception as e:
            messagebox.showerror(
                "エラー", f"固定費・変動費設定の読み込み中にエラーが発生しました: {e}"
            )
            self.fixed_categories = []
            self.variable_categories = []

    def save_fixed_variable_config(self):
        """
        現在の固定費・変動費のカテゴリ設定を 'fv_config.json' に保存する。
        """
        config = {
            "fixed_categories": self.fixed_categories,
            "variable_categories": self.variable_categories,
        }
        try:
            with open("fv_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("設定保存", "固定費・変動費設定が保存されました。")
            # 設定変更後、グラフを再描画して反映
            self.load_fixed_variable_config()
            self.draw_plot()  # グラフを更新
        except Exception as e:
            messagebox.showerror(
                "エラー", f"固定費・変動費設定の保存中にエラーが発生しました: {e}"
            )

    def open_fixed_variable_settings(self):
        """
        固定費・変動費設定用の新しいウィンドウを開く。
        """
        # CSVが読み込まれていない、または支出カテゴリがない場合は警告
        if not self.all_categories:
            messagebox.showwarning(
                "警告",
                "CSVデータが読み込まれていないか、支出カテゴリが見つかりません。先にCSVを読み込むか、支出データを追加してください。",
            )
            return

        fv_window = tk.Toplevel(self.root)
        fv_window.title("固定費・変動費カテゴリ設定")
        fv_window.transient(self.root)
        fv_window.grab_set()

        tk.Label(
            fv_window, text="各カテゴリが固定費か変動費かを選択してください:"
        ).pack(pady=5)

        self.fv_vars = {}  # {カテゴリ名: StringVar(ラジオボタンの値)} を保持

        self.frame_fv_entries = tk.Frame(fv_window)
        self.frame_fv_entries.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self._create_fv_category_widgets(
            self.frame_fv_entries, self.all_categories
        )  # 全カテゴリを渡す

        btn_frame = tk.Frame(fv_window)
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="設定を保存",
            command=lambda: self._save_fv_settings_from_entries(fv_window),
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="閉じる", command=fv_window.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def _create_fv_category_widgets(self, parent_frame, categories):
        """
        カテゴリごとに固定費/変動費選択用のラジオボタンを作成するヘルパーメソッド。
        """
        for widget in parent_frame.winfo_children():
            widget.destroy()  # 既存のウィジェットをクリア

        self.fv_vars = {}  # リセット

        for i, category in enumerate(categories):
            # 収入カテゴリは選択対象外とする
            if category == "収入":
                continue

            tk.Label(parent_frame, text=f"{category}:").grid(
                row=i, column=0, padx=5, pady=2, sticky="w"
            )

            var = tk.StringVar(parent_frame)
            self.fv_vars[category] = var

            # 現在の設定に基づいてラジオボタンの初期値を選択
            if category in self.fixed_categories:
                var.set("固定費")
            elif category in self.variable_categories:
                var.set("変動費")
            else:  # どちらにも属さない場合はデフォルトで変動費に設定
                var.set("変動費")

            tk.Radiobutton(
                parent_frame, text="固定費", variable=var, value="固定費"
            ).grid(row=i, column=1, padx=5, pady=2, sticky="w")
            tk.Radiobutton(
                parent_frame, text="変動費", variable=var, value="変動費"
            ).grid(row=i, column=2, padx=5, pady=2, sticky="w")

    def _save_fv_settings_from_entries(self, fv_window):
        """
        固定費・変動費設定ウィンドウの選択結果を取得し、保存する。
        """
        new_fixed = []
        new_variable = []

        for category, var in self.fv_vars.items():
            selection = var.get()
            if selection == "固定費":
                new_fixed.append(category)
            elif selection == "変動費":
                new_variable.append(category)
            # どちらも選択されていない場合は、そのカテゴリはどちらのリストにも含まれないまま

        self.fixed_categories = new_fixed
        self.variable_categories = new_variable

        self.save_fixed_variable_config()  # JSONファイルに保存
        fv_window.destroy()  # ウィンドウを閉じる

    # --- カテゴリ別推移グラフメソッド ---
    def show_category_trends(self):
        # CSVデータが読み込まれていない、または支出カテゴリがない場合のチェック
        if not hasattr(self, "money_data") or not self.money_data:
            messagebox.showwarning(
                "警告", "データが読み込まれていません。先にCSVを読み込んでください。"
            )
            return
        if not self.all_categories:
            messagebox.showwarning("警告", "表示する支出カテゴリがありません。")
            return

        trends_window = tk.Toplevel(self.root)
        trends_window.title("カテゴリ別 消費推移 (折れ線グラフ)")
        trends_window.geometry("800x600")

        # スクロール可能な領域の準備
        main_frame = tk.Frame(trends_window)
        main_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # X軸のラベル (月)
        # self.sorted_months は process_csv_data で設定されているはず
        month_labels_for_plot = self.sorted_months
        if not month_labels_for_plot:
            messagebox.showwarning(
                "警告", "グラフを表示するための月データがありません。"
            )
            trends_window.destroy()
            return

        # 各カテゴリのグラフを生成
        num_all_categories = len(self.all_categories)
        colors_map = plt.colormaps["tab20"]  # カテゴリごとの色マップ

        # 各カテゴリのグラフ描画
        for i, category in enumerate(
            self.all_categories
        ):  # '収入'は既に除外されているはず
            # カテゴリごとのデータを抽出
            category_values = []
            for month_label in month_labels_for_plot:
                year, month = month_label.split("-")
                amount = self.money_data.get(year, {}).get(month, {}).get(category, 0)
                category_values.append(amount)

            if not any(category_values):  # そのカテゴリの支出が全期間0ならスキップ
                continue

            # グラフ描画
            fig = Figure(figsize=(7, 3), dpi=100)  # 幅を少し広げ、高さを調整
            ax = fig.add_subplot(111)

            # 折れ線グラフに変更
            ax.plot(
                range(len(month_labels_for_plot)),  # X軸の数値インデックス
                category_values,
                marker="o",  # ポイントに丸いマーカー
                linestyle="-",  # 線種
                color=colors_map(i / num_all_categories),  # カテゴリごとの色
            )

            ax.set_title(f"カテゴリ: {category} の推移", fontsize=10)  # タイトルを修正
            ax.set_xlabel("月", fontsize=8)
            ax.set_ylabel("金額 (円)", fontsize=8)
            ax.set_xticks(
                range(len(month_labels_for_plot))
            )  # X軸のティックを数値インデックスに
            ax.set_xticklabels(
                month_labels_for_plot, rotation=45, ha="right", fontsize=7
            )
            ax.tick_params(axis="y", labelsize=7)

            # グリッド線を追加
            ax.grid(True, linestyle="--", alpha=0.6)

            fig.tight_layout()  # レイアウトを自動調整

            chart_canvas = FigureCanvasTkAgg(fig, master=scrollable_frame)
            chart_canvas.draw()
            chart_canvas.get_tk_widget().pack(pady=5, padx=10, fill=tk.X, expand=False)

        # スクロール領域を更新するためにウィジェットの配置が終わるのを待つ
        trends_window.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def search_remark(self):
        search_term = self.entry_search_remark.get().strip()
        start_date_str = self.entry_start_date.get().strip()
        end_date_str = self.entry_end_date.get().strip()

        # 検索結果表示エリアをクリア
        self.text_search_results.delete(1.0, tk.END)
        self.text_search_results.pack_forget()

        # 検索条件が何もない場合は警告
        if not search_term and not start_date_str and not end_date_str:
            messagebox.showwarning(
                "警告", "検索する文字列、または日付期間を入力してください。"
            )
            return

        start_date = None
        end_date = None

        # 日付文字列をdatetimeオブジェクトに変換
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("エラー", "開始日の形式が不正です。(YYYY-MM-DD)")
                return

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("エラー", "終了日の形式が不正です。(YYYY-MM-DD)")
                return

        # 日付範囲の妥当性チェック
        if start_date and end_date and start_date > end_date:
            messagebox.showerror("エラー", "開始日が終了日より後の日付になっています。")
            return

        found_records = []
        for record in self.all_expense_records:
            # 備考の文字列チェック
            remark_match = True
            if search_term:  # 検索文字列が入力されている場合のみチェック
                if search_term.lower() not in record["備考"].lower():
                    remark_match = False

            # 日付範囲のチェック
            date_match = True
            try:
                record_date = datetime.strptime(record["日付"], "%Y-%m-%d")
            except ValueError:
                # CSVファイルに不正な日付形式のデータがある場合
                print(
                    f"警告: レコード '{record['日付']}' の日付形式が不正です。スキップされます。"
                )
                date_match = False  # 不正な日付はマッチしないとする

            if start_date and date_match:  # 開始日が指定されている場合
                if record_date < start_date:
                    date_match = False

            if end_date and date_match:  # 終了日が指定されている場合
                if record_date > end_date:
                    date_match = False

            # 両方の条件を満たした場合にレコードを追加
            if remark_match and date_match:
                found_records.append(record)

        if found_records:
            self.text_search_results.pack(pady=10)

            # 検索条件の表示を改善
            search_summary = []
            if search_term:
                search_summary.append(f"備考に'{search_term}'")
            if start_date_str and end_date_str:
                search_summary.append(f"期間:{start_date_str} 〜 {end_date_str}")
            elif start_date_str:
                search_summary.append(f"期間: {start_date_str} 以降")
            elif end_date_str:
                search_summary.append(f"期間: {end_date_str} 以前")

            self.text_search_results.insert(
                tk.END,
                f"検索結果 ({' AND '.join(search_summary) if search_summary else '全期間'}) :\n\n",
            )

            for record in found_records:
                self.text_search_results.insert(tk.END, f"日付: {record['日付']}, ")
                self.text_search_results.insert(tk.END, f"値段: {record['値段']:,}円, ")
                self.text_search_results.insert(
                    tk.END, f"カテゴリ: {record['カテゴリ']}, "
                )
                self.text_search_results.insert(tk.END, f"物品: {record['物品']}, ")
                self.text_search_results.insert(tk.END, f"備考: {record['備考']}\n")
            self.text_search_results.yview(tk.END)
        else:
            messagebox.showinfo("情報", f"指定された条件の支出は見つかりませんでした。")
            self.text_search_results.pack_forget()

    def _reset_search_results(self):
        """検索結果表示エリアと入力フィールドをリセットするヘルパーメソッド"""
        self.entry_search_remark.delete(0, tk.END)
        self.entry_start_date.delete(0, tk.END)  # 追加
        self.entry_end_date.delete(0, tk.END)  # 追加
        self.text_search_results.delete(1.0, tk.END)
        self.text_search_results.pack_forget()

    def process_csv_data(self, filename):
        money_data_raw = {}  # 全てのカテゴリ（収入含む）の生データを一時的に保持
        self.monthly_income_data = {}  # 各月の収入合計をリセット
        self.all_expense_records = []

        try:
            with open(filename, encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames or not all(
                    k in reader.fieldnames
                    for k in ["日付", "値段", "物品", "カテゴリ", "備考"]
                ):
                    messagebox.showerror(
                        "エラー",
                        "CSVファイルに必要なヘッダー（日付,値段,物品,カテゴリ,備考）がありません。",
                    )
                    return

                for row in reader:
                    if not all(
                        k in row and row[k] for k in ["日付", "値段", "カテゴリ"]
                    ):
                        continue

                    date_str = row["日付"]
                    try:
                        parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
                        year_month = parsed_date.strftime("%Y-%m")  # YYYY-MM 形式
                    except ValueError:
                        messagebox.showwarning(
                            "警告",
                            f"日付 '{date_str}' の形式が不正です。この行はスキップされます。",
                        )
                        continue

                    try:
                        price = int(row["値段"])
                    except ValueError:
                        messagebox.showwarning(
                            "警告",
                            f"値段 '{row['値段']}' が不正です。この行はスキップされます。",
                        )
                        continue

                    category = row["カテゴリ"]
                    item = row.get("物品", "")  # '物品'が存在しない場合も考慮
                    remark = row.get("備考", "")  # '備考'が存在しない場合も考慮

                    # money_data_raw に収入も全て格納
                    if year_month not in money_data_raw:
                        money_data_raw[year_month] = {}
                    if category not in money_data_raw[year_month]:
                        money_data_raw[year_month][category] = []
                    money_data_raw[year_month][category].append(price)

                    # 支出の場合のみ、詳細なレコードを保存
                    if category != "収入":
                        self.all_expense_records.append(
                            {
                                "日付": date_str,
                                "値段": price,
                                "物品": item,
                                "カテゴリ": category,
                                "備考": remark,
                            }
                        )

        except FileNotFoundError:
            messagebox.showerror("エラー", "指定されたファイルが見つかりません。")
            return
        except Exception as e:
            messagebox.showerror(
                "エラー", f"CSVファイルの読み込み中にエラーが発生しました: {e}"
            )
            return

        # money_data_raw から支出と収入をそれぞれ集計
        self.money_data = {}  # 支出のみの集計 (グラフ用)
        for ym_key, categories_data in money_data_raw.items():
            year, month = ym_key.split("-")
            self.money_data.setdefault(year, {}).setdefault(month, {})
            self.monthly_income_data.setdefault(year, {}).setdefault(month, 0)

            for category, prices in categories_data.items():
                total_price = sum(prices)
                if category == "収入":
                    self.monthly_income_data[year][month] += total_price
                    # print(f"収入データ: {year}-{month} の {category} は {total_price} 円")
                else:
                    self.money_data[year][month][category] = total_price

        # self.money_data (支出のみの集計) のカテゴリリストを生成
        all_categories_set = set()
        for y_data in self.money_data.values():
            for m_data in y_data.values():
                for c in m_data.keys():
                    all_categories_set.add(c)
        self.all_categories = sorted(list(all_categories_set))  # クラス変数として保持

        self._initialize_budget_for_new_categories()
        # self._update_category_dropdown()

        self.sorted_months = sorted(
            [f"{y}-{m}" for y, m_data in self.money_data.items() for m in m_data.keys()]
        )  # sorted_months もクラス変数に

        # data_by_month (グラフ用) の準備 (支出のみ)
        self.data_by_month = []
        self.month_labels = []
        for m in self.sorted_months:
            y, mo = m.split("-")
            month_data = self.money_data.get(y, {}).get(mo, {})  # 支出データのみ
            values = [month_data.get(c, 0) for c in self.all_categories]
            self.data_by_month.append((self.all_categories, values))
            self.month_labels.append(m)

        self.current_index = 0
        self.update_buttons()
        if self.data_by_month:
            self.draw_graph()  # グラフを描画
        else:
            for widget in self.frame_plot.winfo_children():
                widget.destroy()
            self.label_month.config(text="データなし")
            messagebox.showinfo(
                "情報", "選択されたCSVファイルには支出データが見つかりませんでした。"
            )

    def _update_balance_display(self):
        """
        現在の月の収支を計算し、表示ラベルと警告を更新する。
        """
        if not self.month_labels:  # まだデータがない場合
            self.label_warning.config(text="")
            return

        if not self.is_day_mode:
            current_month_label = self.month_labels[self.current_index]
            year, month = current_month_label.split("-")

            # その月の支出合計
            current_month_expense_sum = sum(
                self.data_by_month[self.current_index][1]
            )  # valuesの合計

            # その月の収入合計
            current_month_income_sum = self.monthly_income_data.get(year, {}).get(
                month, 0
            )

            print(current_month_income_sum, current_month_expense_sum)  # デバッグ用

            balance = current_month_income_sum - current_month_expense_sum

            if not self.is_day_mode:
                if balance < 0:
                    self.label_warning.config(text=f"赤字！ {balance:,}円", fg="red")
                else:
                    self.label_warning.config(text=f"黒字！ +{balance:,}円", fg="blue")
        else:
            self.label_warning.config(text="日別では収支を表示しません", fg="black")

        # グラフ描画後、label_monthを更新するタイミングで収支も表示
        # self.label_month.config(text=f"{current_month_label} (収支: {balance:,}円)")

    def _open_expense_input_window(self):
        """
        新しい支出を入力するための別ウィンドウを開く。
        """
        # 新しいトップレベルウィンドウを作成
        self.expense_input_window = tk.Toplevel(self.root)
        self.expense_input_window.title("新しい支出を追加")
        self.expense_input_window.transient(self.root)  # メインウィンドウを親にする
        self.expense_input_window.grab_set()  # モーダルにする（メインウィンドウを操作できなくする）

        # 入力フレームを新しいウィンドウ内に作成
        frame_input = tk.LabelFrame(self.expense_input_window, text="支出データの入力")
        frame_input.pack(pady=10, padx=10, fill=tk.X)

        # 日付入力
        tk.Label(frame_input, text="日付 (YYYY-MM-DD):").grid(
            row=0, column=0, padx=5, pady=2, sticky="w"
        )
        self.entry_date = tk.Entry(frame_input, width=25)
        self.entry_date.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        # 今日の日付をデフォルトで設定
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # 値段入力
        tk.Label(frame_input, text="値段:").grid(
            row=1, column=0, padx=5, pady=2, sticky="w"
        )
        self.entry_price = tk.Entry(frame_input, width=25)
        self.entry_price.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # 物品入力
        tk.Label(frame_input, text="物品:").grid(
            row=2, column=0, padx=5, pady=2, sticky="w"
        )
        self.entry_item = tk.Entry(frame_input, width=25)
        self.entry_item.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        # カテゴリ入力
        tk.Label(frame_input, text="カテゴリ:").grid(
            row=3, column=0, padx=5, pady=2, sticky="w"
        )
        self.entry_category = tk.Entry(frame_input, width=25)
        self.entry_category.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        # カテゴリ選択プルダウンメニュー
        # _update_category_options メソッドが存在し、カテゴリリストを保持していると仮定
        # ここでは仮のカテゴリリストを使用しますが、実際には self.categories_from_csv などから取得してください
        if hasattr(self, "categories_from_csv") and self.categories_from_csv:
            initial_category_options = ["カテゴリを選択"] + sorted(
                list(self.categories_from_csv)
            )
        else:
            initial_category_options = [
                "カテゴリを選択",
                "食費",
                "交通費",
                "娯楽費",
                "家賃",
            ]  # 例

        self.selected_input_category = tk.StringVar(frame_input)
        self.selected_input_category.set(
            initial_category_options[0]
        )  # デフォルト値を設定

        # OptionMenuは、値が変更されたときに _on_category_select を呼び出すように設定
        # _on_category_select メソッドを、新しいウィンドウの Entry に値をセットするように修正する必要があります
        self.category_options_menu = tk.OptionMenu(
            frame_input,
            self.selected_input_category,
            *initial_category_options,  # リストの要素を展開して渡す
            command=self._on_category_select_for_input,  # 新しいメソッド名に変更
        )
        self.category_options_menu.config(width=20)  # 幅を調整
        self.category_options_menu.grid(row=3, column=2, padx=5, pady=2, sticky="w")

        # カテゴリリストの更新（必要であれば、ここで最新のカテゴリをロードしてメニューを再設定する）
        # self._update_category_options() # 例：カテゴリが変動するアプリの場合

        # 備考入力
        tk.Label(frame_input, text="備考:").grid(
            row=4, column=0, padx=5, pady=2, sticky="w"
        )
        self.entry_notes = tk.Entry(frame_input, width=25)
        self.entry_notes.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        # データ書き込みボタン
        # command は self.write_data_to_csv を呼び出す
        self.btn_write = tk.Button(
            frame_input, text="データを書き込む", command=self.write_data_to_csv
        )
        self.btn_write.grid(row=5, column=0, columnspan=3, pady=10)  # 3列にまたがる

        # ウィンドウが閉じられたときの処理（オプション）
        self.expense_input_window.protocol(
            "WM_DELETE_WINDOW", self._on_input_window_close
        )

    # --- 変更点2: write_data_to_csv 関数の修正 ---
    # (これはあなたのクラスのメソッドとして定義されます)
    def write_data_to_csv(self):
        """
        入力フィールドからデータを取得し、CSVファイルに追記する。
        処理後、入力ウィンドウを閉じ、メインウィンドウのグラフを更新する。
        """
        if not self.current_filename:
            messagebox.showerror("エラー", "ファイルが選択されていません。")
            return

        # 現在のインデックスと表示モードを保存（グラフ更新後に復元するため）
        prev_index = self.current_index
        prev_is_circle = self.is_circle

        # 入力フィールドからデータを取得
        date = self.entry_date.get()
        price = self.entry_price.get()
        item = self.entry_item.get()
        category = self.entry_category.get()
        notes = self.entry_notes.get()

        # データの検証
        if not all([date, price, item, category]):
            messagebox.showwarning(
                "入力エラー", "日付、値段、物品、カテゴリは必須項目です。"
            )
            return

        try:
            # 日付形式の検証 (YYYY-MM-DD)
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning(
                "入力エラー", "日付の形式がYYYY-MM-DDではありません。"
            )
            return

        try:
            price = int(price)  # 値段を整数に変換
            if price <= 0:
                messagebox.showwarning(
                    "入力エラー", "値段は正の整数で入力してください。"
                )
                return
        except ValueError:
            messagebox.showwarning("入力エラー", "値段は数値で入力してください。")
            return

        # CSVファイルにデータを追記
        try:
            with open(self.current_filename, "a", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([date, price, item, category, notes])

            messagebox.showinfo("成功", "データが正常に書き込まれました。")

            # グラフ更新の前にウィンドウを閉じる
            if (
                hasattr(self, "expense_input_window")
                and self.expense_input_window.winfo_exists()
            ):
                self.expense_input_window.grab_release()  # グラブ解除をdestroyの前に
                self.expense_input_window.destroy()

            # メインウィンドウのデータを再読み込みし、グラフを更新
            self.load_csv(answer=1)
            self.current_index = (
                min(prev_index, len(self.data_by_month) - 1)
                if self.data_by_month
                else 0
            )
            self.is_circle = prev_is_circle
            self.draw_graph()

        except Exception as e:
            messagebox.showerror(
                "ファイル書き込みエラー",
                f"データの書き込み中にエラーが発生しました: {e}",
            )
            # エラーが発生した場合もウィンドウを閉じたいならここに追加
            if (
                hasattr(self, "expense_input_window")
                and self.expense_input_window.winfo_exists()
            ):
                self.expense_input_window.grab_release()
                self.expense_input_window.destroy()

    # --- 変更点3: 新しいカテゴリ選択のコールバック関数を追加 ---
    # (これもあなたのクラスのメソッドとして定義されます)
    def _on_category_select_for_input(self, selected_category):
        """
        支出入力ウィンドウのカテゴリプルダウンで項目が選択されたときに呼び出される。
        選択されたカテゴリを入力Entryに設定する。
        """
        if selected_category != "カテゴリを選択":
            self.entry_category.delete(0, tk.END)
            self.entry_category.insert(0, selected_category)

    # --- 変更点4: 入力ウィンドウが閉じられたときの処理 (オプション) ---
    # (これもあなたのクラスのメソッドとして定義されます)
    def _on_input_window_close(self):
        """
        支出入力ウィンドウが閉じられたときにグラブを解除する。
        """
        if (
            hasattr(self, "expense_input_window")
            and self.expense_input_window.winfo_exists()
        ):
            self.expense_input_window.grab_release()
            self.expense_input_window.destroy()


# 実行
if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetCarouselApp(root)
    root.mainloop()
