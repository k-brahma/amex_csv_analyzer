"""
AMEX CSV Analyzer のテスト
"""

import os
import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

# テスト対象のモジュールをインポート
# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import main
from config import MODE_TEST


class TestProductionEnvironmentCheck:
    """本番環境のチェック機能のテスト"""

    @patch("os.path.exists")
    @patch("os.listdir")
    def test_missing_data_dir(self, mock_listdir, mock_exists):
        """dataディレクトリがない場合のテスト"""
        # os.path.exists の戻り値を設定
        mock_exists.side_effect = lambda path: path != "data"

        # 関数を実行
        result = main.check_production_environment()

        # 結果を検証
        assert result is False
        # 'merchants' と 'merchants/merchants.csv' のチェックは行われないはず
        assert mock_exists.call_count == 1

    @patch("os.path.exists")
    @patch("os.listdir")
    def test_missing_merchants_dir(self, mock_listdir, mock_exists):
        """merchantsディレクトリがない場合のテスト"""
        # os.path.exists の戻り値を設定
        mock_exists.side_effect = lambda path: path != "merchants"

        # 関数を実行
        result = main.check_production_environment()

        # 結果を検証
        assert result is False
        # 'data' と 'merchants' のチェックは行われるが、'merchants/merchants.csv' のチェックは行われないはず
        assert mock_exists.call_count == 2

    @patch("os.path.exists")
    @patch("os.listdir")
    def test_missing_merchants_csv(self, mock_listdir, mock_exists):
        """merchants.csvファイルがない場合のテスト"""
        # os.path.exists の戻り値を設定
        mock_exists.side_effect = lambda path: path != "merchants/merchants.csv"

        # 関数を実行
        result = main.check_production_environment()

        # 結果を検証
        assert result is False
        # すべてのパスのチェックが行われるはず
        assert mock_exists.call_count == 3

    @patch("os.path.exists")
    @patch("os.listdir")
    def test_empty_data_dir(self, mock_listdir, mock_exists):
        """dataディレクトリにCSVファイルがない場合のテスト"""
        # os.path.exists の戻り値を設定（すべて存在する）
        mock_exists.return_value = True

        # os.listdir の戻り値を設定（空のリスト）
        mock_listdir.return_value = []

        # 関数を実行
        result = main.check_production_environment()

        # 結果を検証
        assert result is False
        # すべてのパスのチェックが行われるはず
        assert mock_exists.call_count == 3
        assert mock_listdir.call_count == 1

    @patch("os.path.exists")
    @patch("os.listdir")
    def test_valid_environment(self, mock_listdir, mock_exists):
        """有効な環境の場合のテスト"""
        # os.path.exists の戻り値を設定（すべて存在する）
        mock_exists.return_value = True

        # os.listdir の戻り値を設定（CSVファイルあり）
        mock_listdir.return_value = ["file1.csv", "file2.csv"]

        # 関数を実行
        result = main.check_production_environment()

        # 結果を検証
        assert result is True
        # すべてのパスのチェックが行われるはず
        assert mock_exists.call_count == 3
        assert mock_listdir.call_count == 1


class TestDataProcessing:
    """データ処理機能のテスト"""

    @pytest.fixture
    def sample_df(self):
        """テスト用のサンプルデータフレーム"""
        import pandas as pd

        return pd.DataFrame(
            {
                "ご利用日": ["2024/01/01", "2024/01/02", "2024/01/03"],
                "ご利用内容": ["AMAZON WEB SERVICES", "GITHUB INC", "コンビニ"],
                "金額": ["1,000", "2,000", "500"],
                "海外通貨利用金額": ["", "20.00 USD", ""],
            }
        )

    @pytest.fixture
    def processed_df(self):
        """前処理済みのテスト用データフレーム"""
        return pd.DataFrame(
            {
                "ご利用日": ["2024/01/01", "2024/01/02", "2024/01/03"],
                "ご利用内容": ["AMAZON WEB SERVICES", "GITHUB INC", "コンビニ"],
                "金額": [1000, 2000, 500],
                "現地通貨建て金額": [np.nan, "20.00", np.nan],
                "通貨": [np.nan, "USD", np.nan],
                "is_corporate": [3, 3, 0],
                "merchant_category": ["cloud_services", "developer_tools", ""],
            }
        )

    def test_preprocess_transaction_data(self, sample_df):
        """取引データの前処理のテスト"""
        # 前処理を実行
        result_df = main.preprocess_transaction_data(sample_df)

        # 結果を検証
        assert len(result_df) == 3
        assert result_df["金額"].tolist() == [1000, 2000, 500]

        # NaNの場合は特別な検証が必要
        # 現地通貨建て金額の検証
        current_values = result_df["現地通貨建て金額"].tolist()
        assert pd.isna(current_values[0]) or current_values[0] == ""
        assert current_values[1] == "20.00"
        assert pd.isna(current_values[2]) or current_values[2] == ""

        # 通貨の検証
        currency_values = result_df["通貨"].tolist()
        assert pd.isna(currency_values[0]) or currency_values[0] == ""
        assert currency_values[1] == "USD"
        assert pd.isna(currency_values[2]) or currency_values[2] == ""

    @patch("pandas.read_csv")
    def test_load_merchant_config(self, mock_read_csv):
        """マスターデータ読み込みのテスト"""
        # モックの戻り値を設定
        mock_df = MagicMock()
        mock_read_csv.return_value = mock_df

        # 関数を実行
        result = main.load_merchant_config()

        # 結果を検証
        assert result is mock_df
        mock_read_csv.assert_called_once()

    def test_identify_corporate_transactions(self, sample_df):
        """法人取引判定のテスト"""
        import pandas as pd

        # マスターデータを作成
        merchants_df = pd.DataFrame(
            {
                "merchant_name": ["AMAZON WEB SERVICES", "GITHUB INC"],
                "is_corporate": [3, 3],
                "category": ["cloud_services", "developer_tools"],
            }
        )

        # 前処理を実行
        result_df = main.identify_corporate_transactions(sample_df, merchants_df)

        # 結果を検証
        assert result_df["is_corporate"].tolist() == [3, 3, 0]
        assert result_df["merchant_category"].tolist() == ["cloud_services", "developer_tools", ""]

    def test_analyze_transaction_frequency(self, processed_df):
        """取引頻度分析のテスト"""
        # 分析を実行
        result_df = main.analyze_transaction_frequency(processed_df)

        # 結果を検証
        assert len(result_df) == 3  # 3つの異なる取引先
        assert "回数" in result_df.columns
        assert "合計金額" in result_df.columns
        assert "法人取引" in result_df.columns
        assert "カテゴリ" in result_df.columns

        # AMAZONとGITHUBの合計金額が正しいか
        amazon_row = result_df.loc["AMAZON WEB SERVICES"]
        assert amazon_row["合計金額"] == 1000
        assert amazon_row["法人取引"] == 3
        assert amazon_row["カテゴリ"] == "cloud_services"

        github_row = result_df.loc["GITHUB INC"]
        assert github_row["合計金額"] == 2000
        assert github_row["法人取引"] == 3
        assert github_row["カテゴリ"] == "developer_tools"

    def test_analyze_corporate_transactions(self, processed_df):
        """法人取引分析のテスト"""
        # 分析を実行
        result_df = main.analyze_corporate_transactions(processed_df)

        # 結果を検証
        assert len(result_df) == 2  # 2つのカテゴリ（cloud_servicesとdeveloper_tools）
        assert "取引回数" in result_df.columns
        assert "合計金額" in result_df.columns

        # カテゴリごとの合計金額が正しいか
        assert result_df.loc["cloud_services"]["合計金額"] == 1000
        assert result_df.loc["developer_tools"]["合計金額"] == 2000

    def test_get_foreign_transactions(self, processed_df):
        """海外取引抽出のテスト"""
        # 海外取引を抽出
        result_df = main.get_foreign_transactions(processed_df)

        # 結果を検証
        assert len(result_df) == 1  # 1つの海外取引（GITHUB INC）
        assert result_df["ご利用内容"].iloc[0] == "GITHUB INC"
        assert result_df["現地通貨建て金額"].iloc[0] == "20.00"
        assert result_df["通貨"].iloc[0] == "USD"


class TestMainFunction:
    """メイン関数のテスト"""

    @patch("main.load_merchant_config")
    @patch("main.load_transaction_data")
    @patch("main.preprocess_transaction_data")
    @patch("main.identify_corporate_transactions")
    @patch("main.analyze_transaction_frequency")
    @patch("main.analyze_corporate_transactions")
    @patch("main.get_foreign_transactions")
    @patch("pandas.DataFrame.to_csv", MagicMock())  # to_csvをモックするが、呼び出し回数は検証しない
    def test_main_function_with_data(
        self,
        mock_get_foreign,
        mock_analyze_corporate,
        mock_analyze_frequency,
        mock_identify,
        mock_preprocess,
        mock_load_transaction,
        mock_load_merchant,
    ):
        """データがある場合のメイン関数のテスト"""
        # モックの戻り値を設定
        mock_merchants_df = MagicMock()
        mock_load_merchant.return_value = mock_merchants_df

        mock_transaction_df = pd.DataFrame(
            {"ご利用日": ["2024/01/01"], "ご利用内容": ["テスト"], "金額": [1000]}
        )
        mock_load_transaction.return_value = mock_transaction_df

        mock_preprocessed_df = MagicMock()
        mock_preprocess.return_value = mock_preprocessed_df

        mock_identified_df = MagicMock()
        mock_identify.return_value = mock_identified_df

        mock_frequency_df = MagicMock()
        mock_analyze_frequency.return_value = mock_frequency_df

        mock_corporate_df = MagicMock()
        mock_analyze_corporate.return_value = mock_corporate_df

        mock_foreign_df = MagicMock()
        mock_get_foreign.return_value = mock_foreign_df

        # メイン関数を実行
        main.main()

        # 各関数が呼び出されたことを検証
        mock_load_merchant.assert_called_once()
        mock_load_transaction.assert_called_once()
        mock_preprocess.assert_called_once_with(mock_transaction_df)
        mock_identify.assert_called_once_with(mock_preprocessed_df, mock_merchants_df)
        mock_analyze_frequency.assert_called_once_with(mock_identified_df)
        mock_analyze_corporate.assert_called_once_with(mock_identified_df)
        mock_get_foreign.assert_called_once_with(mock_identified_df)

    @patch("main.load_merchant_config")
    @patch("main.load_transaction_data")
    def test_main_function_no_data(self, mock_load_transaction, mock_load_merchant):
        """データがない場合のメイン関数のテスト"""
        # モックの戻り値を設定
        mock_merchants_df = MagicMock()
        mock_load_merchant.return_value = mock_merchants_df

        # 空のデータフレームを返す
        mock_load_transaction.return_value = pd.DataFrame()

        # メイン関数を実行
        main.main()

        # 各関数が呼び出されたことを検証
        mock_load_merchant.assert_called_once()
        mock_load_transaction.assert_called_once()
        # データがないので、他の処理関数は呼び出されないはず


if __name__ == "__main__":
    pytest.main(["-v"])
