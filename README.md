# AMEX CSV Analyzer

AMEXカードの利用明細CSVファイルを分析し、取引パターンを可視化するツールです。  
複数の明細ファイルを一括で処理し、法人取引と個人取引を区別しながら、カテゴリごとの支出分析を実現します。

## 使い方

config/merchants.csv に取引先の分類ルールを設定してください。
data/ ディレクトリにAMEXの明細CSVファイルを配置し、以下のコマンドを実行してください。 results/ ディレクトリに結果が保存されます。

```bash
python main.py
```

## 生成されるファイル:

- concatenated.csv: 全取引データ（前処理済み）
- grouped.csv: 取引先ごとの集計結果
- corporate_summary.csv: 法人取引の分析
- foreign.csv: 海外取引データ

## セットアップ方法

### 必要な環境

- Python 3.8以上

### パッケージのインストール

```bash
pip install -r requirements.txt
```

### 取引先マスターデータについて

`config/merchants.csv` に取引先の分類ルールを定義します。フォーマットは以下の通りです：

```csv
merchant_name,is_corporate,category
AMAZON WEB SERVICES,3,cloud_services
GITHUB INC,3,developer_tools
まいばすけっと,2,個人買い物
```

取引区分（is_corporate）の値：

- 3: 明確な法人取引（例：クラウドサービス、開発ツール）
- 2: 明確な個人取引（例：スーパーマーケット、レストラン）
- 1: 法人・個人両方の可能性がある取引
- 0: 不明・その他

## カスタマイズ方法

### 1. 対象年度の変更

デフォルトでは2024年の取引のみを分析対象としています。他の年度も含める場合は、
`preprocess_transaction_data()` 関数内の以下の部分を修正してください：

```python
# 2024年のデータのみを抽出
return df[df['ご利用日'].str.contains('2024')]
```

### 文字コード

- AMEXの明細CSVファイルはCP932（Shift-JIS）でエンコードされているという前提で処理しています
- 出力ファイルはUTF-8で保存されます

## ライセンス

このプロジェクトはMITライセンスの下で公開します。
