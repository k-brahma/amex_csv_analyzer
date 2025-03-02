"""
AMEX CSV Analyzer の設定ファイル
"""

# テストモード設定
# True: サンプルデータを使用する
# False: 実際のデータを使用する
MODE_TEST = True

# その他の設定
TARGET_YEAR = "2024"  # 分析対象年

# 以下は編集の必要はありません
# ディレクトリ設定
DATA_DIR = "samples/data" if MODE_TEST else "data"
RESULT_DIR = "results"
MERCHANT_CONFIG = (
    "samples/merchants/merchants_sample.csv" if MODE_TEST else "merchants/merchants.csv"
)
