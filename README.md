# AMEX CSV Analyzer

AMEXカードの利用明細CSVファイルを分析し、取引パターンを可視化するツールです。複数の明細ファイルを一括で処理し、法人取引と個人取引を区別しながら、カテゴリごとの支出分析を実現します。

## 概要

このツールは以下の機能を提供します：

- 複数のAMEX明細CSVファイルの一括処理と結合
- 法人取引と個人取引の自動分類
- 取引先ごとの利用頻度と金額の集計
- カテゴリ別の支出分析
- 海外取引の抽出と分析

## 必要環境

- Python 3.8以上
- pandas 2.2.3

## インストール方法

1. リポジトリをクローンまたはダウンロードします
   ```bash
   git clone https://github.com/k-brahma/amex_csv_analyzer
   cd amex_csv_analyzer
   ```

2. 仮想環境を作成し、有効化します（推奨）
   ```bash
   python -m venv .venv
   # Windowsの場合
   .venv\Scripts\activate
   # macOS/Linuxの場合
   source .venv/bin/activate
   ```

3. 必要なパッケージをインストールします
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

### クイックスタート（初めての方向け）

1. `config.py` を確認し、テストモードが有効になっていることを確認します：
   ```python
   MODE_TEST = True  # この値がTrueになっていることを確認
   ```

2. すぐに実行してみましょう：
   ```bash
   python main.py
   ```

3. 「※テストモードで実行しています。サンプルデータを使用します。」と表示され、サンプルデータを使った分析が実行されます。

4. 結果は `results/` ディレクトリに保存されます。

### 実データでの使用

実際のAMEX明細データを分析する場合：

1. データを準備します：
   - `data/` ディレクトリにAMEXの明細CSVファイルを配置（**必ずShift-JIS形式**）
   - `merchants/merchants.csv` に取引先の分類ルールを設定（**必ずShift-JIS形式**）

2. `config.py` を編集します：
   ```python
   MODE_TEST = False  # 実データを使用するためFalseに設定
   TARGET_YEAR = "2024"  # 分析したい年に設定
   ```

3. 実行します：
   ```bash
   python main.py
   ```

### 結果ファイル

処理が完了すると、`results/` ディレクトリに以下のファイルが生成されます：

- **concatenated.csv**: 全取引データ（前処理済み）
- **grouped.csv**: 取引先ごとの集計結果
- **corporate_summary.csv**: 法人取引の分析
- **foreign.csv**: 海外取引データ

## テストモード

このツールはテストモードを備えており、実際のデータがなくてもサンプルデータで動作確認ができます。

### テストモードの有効化

`config.py` ファイルの `MODE_TEST` 変数を `True` に設定します：

```python
# テストモード設定
# True: サンプルデータを使用する
# False: 実際のデータを使用する
MODE_TEST = True
```

### 設定ファイル（config.py）の詳細

`config.py`ファイルには以下の重要な設定値があります：

```python
# テストモード設定
MODE_TEST = True  # True: サンプルデータ使用、False: 実データ使用

# ディレクトリ設定
DATA_DIR = "samples/data" if MODE_TEST else "data"  # データディレクトリ
RESULT_DIR = "results"  # 結果出力ディレクトリ
MERCHANT_CONFIG = (
    "samples/merchants/merchants_sample.csv" if MODE_TEST else "merchants/merchants.csv"
)  # 取引先マスターデータ

# 分析対象年設定
TARGET_YEAR = "2025"  # 分析対象年（この年のデータのみが処理されます）
```

**重要な設定値**:

1. **MODE_TEST**: テストモードの切り替え
   - `True`: サンプルデータを使用（初期設定）
   - `False`: 実際のデータを使用

2. **TARGET_YEAR**: 分析対象年
   - デフォルトは`"2024"`
   - この値を変更することで、異なる年のデータを分析できます
   - 例えば`"2024"`に設定すると、2024年の取引のみが分析対象になります
   - 複数年を対象にする場合は、この値を空文字列`""`に設定するか、コードを修正してください

3. **DATA_DIR**: データディレクトリ
   - テストモード時は`"samples/data"`
   - 実データモード時は`"data"`

4. **MERCHANT_CONFIG**: 取引先マスターデータファイル
   - テストモード時は`"samples/merchants/merchants_sample.csv"`
   - 実データモード時は`"merchants/merchants.csv"`

テストモードでは、以下のサンプルデータが使用されます：
- `samples/merchants/merchants_sample.csv`: サンプルの取引先マスターデータ
- `samples/data/`: サンプルの取引データCSVファイル

### サンプルデータの内容

サンプルデータには以下のような架空の取引情報が含まれています：
- クラウドサービス（AWS、さくらインターネットなど）
- 開発ツール（GitHub）
- 食品・コンビニ（まいばすけっと、セブンイレブンなど）
- 飲食店（マクドナルド、スターバックスなど）
- 海外取引（ZOOM.US）

### サンプルデータの文字コード

**重要**: サンプルデータは実際のAMEX明細データと同様に、CP932（Shift-JIS）形式で保存されています。これは日本語Windows環境での標準的なエンコードです。

サンプルデータを編集したり、新しいサンプルデータを作成する場合は、必ずCP932（Shift-JIS）エンコードで保存してください。UTF-8やその他のエンコードで保存すると、プログラムが正しく動作しません。

サンプルデータファイルのエンコードを確認・変更する方法：
1. テキストエディタ（メモ帳、VSCode、サクラエディタなど）でファイルを開く
2. 「名前を付けて保存」を選択
3. エンコードを「SHIFT-JIS」または「CP932」に設定して保存

エンコードが正しくない場合、プログラム実行時に以下のようなエラーが表示されます：
```
警告: マスターデータの読み込み中にエラーが発生しました: 'cp932' codec can't decode byte 0x85 in position 22: illegal multibyte sequence
```

## 取引先マスターデータの設定

`merchants/merchants.csv` には以下の形式で取引先情報を定義します：

```csv
merchant_name,is_corporate,category
AMAZON WEB SERVICES,3,cloud_services
GITHUB INC,3,developer_tools
まいばすけっと,2,個人買い物
```

**重要**: 取引先マスターデータファイルも必ずCP932（Shift-JIS）エンコードで保存してください。日本語を含むデータを正しく処理するために必要です。

### 取引区分（is_corporate）の値

- **3**: 明確な法人取引（例：クラウドサービス、開発ツール）
- **2**: 明確な個人取引（例：スーパーマーケット、レストラン）
- **1**: 法人・個人両方の可能性がある取引
- **0**: 不明・その他

### カテゴリ（category）

カテゴリは自由に定義できます。例：
- cloud_services
- developer_tools
- business_media
- 食品
- コンビニ
- 交通費

## カスタマイズ方法

### 1. 対象年度の変更

デフォルトでは2024年の取引のみを分析対象としています。他の年度を対象にする場合は、`config.py` の `TARGET_YEAR` 変数を変更してください：

```python
# その他の設定
TARGET_YEAR = '2023'  # 分析対象年を2023年に変更
```

複数年のデータを一度に分析したい場合は、空文字列を設定することで年度フィルタを無効化できます：

```python
# その他の設定
TARGET_YEAR = ''  # すべての年のデータを分析対象にする
```

**注意**: 年度フィルタは `ご利用日` 列に対して文字列検索で行われます。そのため、`TARGET_YEAR = '202'` とすると、2020年代のすべてのデータが対象になります。

### 2. 出力ファイルのカスタマイズ

追加の分析や異なる出力形式が必要な場合は、`main.py` の `main()` 関数を編集してください。

### 3. 新しい分析機能の追加

新しい分析機能を追加する場合は、適切な関数を `main.py` に実装し、`main()` 関数から呼び出してください。

## ファイル形式と文字コード

- **入力ファイル**: AMEXの明細CSVファイル（CP932/Shift-JIS形式）
- **サンプルデータ**: テスト用サンプルCSVファイル（CP932/Shift-JIS形式）
- **出力ファイル**: UTF-8形式のCSVファイル

**重要**: このツールはすべての入力CSVファイル（取引データと取引先マスターデータ）がCP932（Shift-JIS）エンコードであることを前提としています。UTF-8やその他のエンコードでは正しく動作しません。

### 新規ファイル作成時の注意点

新しいCSVファイルを作成する場合は、必ずCP932（Shift-JIS）エンコードで保存してください：

1. **Excelで作成する場合**:
   - 「名前を付けて保存」→「その他の形式」→「CSV（カンマ区切り）」を選択
   - 「ツール」→「Webオプション」→「エンコード」タブで「日本語（シフトJIS）」を選択

2. **テキストエディタで作成する場合**:
   - 「名前を付けて保存」時にエンコードを「SHIFT-JIS」または「CP932」に設定

3. **プログラムで作成する場合**:
   ```python
   # Pythonでの例
   with open('file.csv', 'w', encoding='cp932') as f:
       f.write('ヘッダー1,ヘッダー2\n')
       f.write('データ1,データ2\n')
   ```

エンコードが正しくないと、「'cp932' codec can't decode byte...」のようなエラーが発生します。

## ディレクトリ構造

```
amex_analyzer/
├── merchants/              # 取引先マスターデータ
│   ├── merchants.csv       # 取引先マスターデータ
│   └── merchants_sample.csv # サンプルマスターデータ
├── data/                   # 入力データディレクトリ（AMEXのCSVファイル）
├── samples/                # サンプルデータ
│   ├── merchants/          # サンプル取引先マスターデータ
│   │   └── merchants_sample.csv # サンプル取引先マスターデータ
│   └── data/               # サンプル取引データ
├── results/                # 出力結果ディレクトリ
├── .venv/                  # 仮想環境（gitignore対象）
├── main.py                 # メインスクリプト
├── config.py               # 設定ファイル
├── requirements.txt        # 依存パッケージリスト
└── README.md               # このファイル
```

## トラブルシューティング

### よくある問題

1. **ファイルが読み込めない場合**
   - CSVファイルの文字コードがCP932（Shift-JIS）であることを確認してください
   - UTF-8やその他のエンコードでは正しく動作しません
   - ファイル名に特殊文字が含まれていないか確認してください
   - テキストエディタでファイルを開き、「名前を付けて保存」でエンコードをShift-JISに変更してみてください

2. **「'cp932' codec can't decode byte...」エラーが表示される場合**
   - CSVファイルがUTF-8など、Shift-JIS以外のエンコードで保存されている可能性があります
   - ファイルをShift-JIS（CP932）エンコードで保存し直してください

3. **法人取引が正しく判定されない場合**
   - `merchants/merchants.csv` の内容を確認し、必要に応じて取引先情報を追加してください
   - マスターデータもShift-JIS（CP932）エンコードで保存されていることを確認してください

4. **エラー「pandas module not found」が表示される場合**
   - `pip install -r requirements.txt` を実行して依存パッケージをインストールしてください

## ライセンス

このプロジェクトはMITライセンスの下で公開しています。詳細については [LICENSE](LICENSE) ファイルを参照してください。

## 貢献

バグ報告や機能リクエストは、Issueトラッカーを通じてお知らせください。プルリクエストも歓迎します。

---

*注: このツールはAMEXカードの明細データを分析するための非公式ツールであり、American Express社とは一切関係ありません。*
