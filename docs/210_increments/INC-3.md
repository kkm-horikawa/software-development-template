# INC-3 バックエンドとCLIを分けて接続する

対応Issue: #3

> 作業記録アプリの変更例です。新しい製品では削除してください。

## 変更範囲

バックエンドをbackend、利用先をclientへ分け、CLIがHTTPの公開契約で作業開始を利用する形にします。Webやモバイルの入口は含めません。

## 設計と確認

CLIの入力・表示、利用手順、HTTP通信を分け、Pythonの内部コードやSQLiteを読み込まない形にします。公開契約はcontractsへ置きます。

外からは別プロセスのCLIをFastAPIへ接続して結果を確認します。境界では実HTTP応答と公開契約を確認します。現在の具体値と実行方法は受入例・テストへ置きます。

## 結果のありか

[PR #4](https://github.com/kkm-horikawa/software-development-template/pull/4)。当時の実装はPRの差分から確認します。
