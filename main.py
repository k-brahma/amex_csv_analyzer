"""
amex csv analyzer

concatenates multiple csv files in data dir into one and analyzes corporate transactions
using a merchant configuration file
"""

import os
import pandas as pd

# データディレクトリとマスターデータの設定
DATA_DIR = 'data'
RESULT_DIR = 'results'
MERCHANT_CONFIG = 'config/merchants.csv'

# create DATA_DIR and RESULT_DIR if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)


def load_merchant_config():
    """
    法人取引判定用のマスターデータを読み込む
    merchants.csvには法人取引先の定義が含まれる
    """
    try:
        merchants_df = pd.read_csv(MERCHANT_CONFIG)
        print(f"法人取引マスターデータを読み込みました: {len(merchants_df)}件")
        return merchants_df
    except FileNotFoundError:
        print(f"警告: {MERCHANT_CONFIG}が見つかりません。法人取引の判定はスキップされます。")
        return None


def identify_corporate_transactions(df, merchants_df):
    """
    取引データに法人/個人取引フラグとカテゴリを付与します。

    フラグの値は取引の性質を示します：
    - 3: 明確な法人取引（例：クラウドサービス、開発ツール）
    - 2: 明確な個人取引（例：スーパーマーケット、レストラン）
    - 1: 法人・個人両方の可能性がある取引
    - 0: 不明・その他
    """
    if merchants_df is None:
        df['is_corporate'] = 0
        df['merchant_category'] = 'unknown'
        return df

    def match_merchant(transaction):
        for _, merchant in merchants_df.iterrows():
            if merchant['merchant_name'] in transaction:
                return pd.Series([merchant['is_corporate'], merchant['category']])
        return pd.Series([0, ''])

    df[['is_corporate', 'merchant_category']] = df['ご利用内容'].apply(match_merchant)
    # 結果を整数型に変換
    df['is_corporate'] = df['is_corporate'].astype(int)
    return df


def load_transaction_data(data_dir):
    """
    指定されたディレクトリから全てのCSVファイルを読み込み、結合します。

    Args:
        data_dir (str): CSVファイルが格納されているディレクトリパス

    Returns:
        pd.DataFrame: 結合された取引データ
    """
    files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    print(f"処理対象ファイル: {files}")

    dfs = []
    for file in files:
        df = pd.read_csv(os.path.join(data_dir, file), encoding='cp932')
        dfs.append(df)

    return pd.concat(dfs).sort_values('ご利用日')


def preprocess_transaction_data(df):
    """
    取引データの前処理を行います。金額の正規化や海外通貨の処理、文字列のクリーニングを含みます。
    """
    # まず取引内容の末尾スペースを削除
    df['ご利用内容'] = df['ご利用内容'].str.rstrip()

    # 金額の前処理（既存の処理）
    df['金額'] = df['金額'].str.replace('"', '').str.replace(',', '').astype(int)

    # 海外通貨関連の処理（既存の処理）
    df['海外通貨利用金額'] = df['海外通貨利用金額'].str.replace('"', '').str.replace(',', '')
    df['現地通貨建て金額'] = df['海外通貨利用金額'].str.split().str[0]
    df['通貨'] = df['海外通貨利用金額'].str.split().str[1]
    df = df.drop(columns=['海外通貨利用金額'])

    # 2024年のデータのみを抽出（既存の処理）
    return df[df['ご利用日'].str.contains('2024')]


def analyze_transaction_frequency(df):
    """
    取引の頻度、金額、および法人情報を取引先ごとに集計します。

    Args:
        df (pd.DataFrame): 前処理済みの取引データ。
            is_corporate(int): 法人取引フラグ (0 or 1)
            merchant_category(str): 取引先カテゴリ

    Returns:
        pd.DataFrame: 取引先ごとの利用回数、合計金額、法人フラグの集計結果
    """
    return (df.groupby('ご利用内容')
            .agg({
        'ご利用内容': 'count',
        '金額': 'sum',
        'is_corporate': 'first',  # 各取引先の法人フラグを取得
        'merchant_category': 'first'  # 各取引先のカテゴリを取得
    })
            .rename(columns={
        'ご利用内容': '回数',
        '金額': '合計金額',
        'is_corporate': '法人取引',
        'merchant_category': 'カテゴリ'
    })
            .sort_values('回数', ascending=False))


def analyze_corporate_transactions(df):
    """
    法人取引をカテゴリごとに集計します。

    Args:
        df (pd.DataFrame): 前処理済みの取引データ

    Returns:
        pd.DataFrame: カテゴリごとの法人取引の集計結果
    """
    df_corporate = df[df['is_corporate'] == 1]
    return (df_corporate.groupby('merchant_category')
    .agg({
        'ご利用内容': 'count',
        '金額': 'sum'
    })
    .rename(columns={
        'ご利用内容': '取引回数',
        '金額': '合計金額'
    }))


def get_foreign_transactions(df):
    """
    海外での取引データを抽出します。

    Args:
        df (pd.DataFrame): 前処理済みの取引データ

    Returns:
        pd.DataFrame: 海外取引のデータ
    """
    return df[df['現地通貨建て金額'].notnull()].copy()


def main():
    """
    メインの処理フローを制御します。
    データの準備、前処理、そして各種分析を順番に実行します。
    """
    # データの準備
    merchants_df = load_merchant_config()
    df = load_transaction_data(DATA_DIR)

    # データの前処理
    df = preprocess_transaction_data(df)
    df = identify_corporate_transactions(df, merchants_df)

    # 基本データの保存
    df.to_csv(os.path.join(RESULT_DIR, 'concatenated.csv'), index=False)

    # 取引先ごとに group by して集計
    transaction_frequency = analyze_transaction_frequency(df)
    transaction_frequency.to_csv(os.path.join(RESULT_DIR, 'grouped.csv'))

    # 法人取引の集計
    corporate_analysis = analyze_corporate_transactions(df)
    corporate_analysis.to_csv(os.path.join(RESULT_DIR, 'corporate_summary.csv'))

    # 海外取引の抽出
    foreign_transactions = get_foreign_transactions(df)
    foreign_transactions.to_csv(os.path.join(RESULT_DIR, 'foreign.csv'), index=False)


if __name__ == "__main__":
    main()
