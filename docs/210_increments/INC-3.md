# INC-3 バックエンドとクライアントを製品単位で分ける

対応Issue: #3
対応シナリオ: SC-001
対応要求: REQ-001、AC-002

> 作業記録アプリのサンプル増分です。新しい製品では最初のIssueへ着手する前に削除してください。

## 変える体験

開発者がトップ階層を見ると、独立して配備するバックエンドと、Web・モバイル・CLIなど独立して配布する利用先をすぐ見つけられる。GoのCLIから公開したHTTP契約でFastAPIへ要求し、SQLAlchemyへの保存まで実際に確かめられる。

## 外から見える振る舞いと確認

### SPEC-3-01: Goクライアントからバックエンドへ作業開始を依頼する [AC-002]

FastAPIを起動してGoのCLIへ `start "設計を書く"` を渡すと、CLIは `開始: 設計を書く` と表示し、バックエンドのSQLiteへ一件保存する。

### ST-3-01: 異なる実行単位をHTTPでつないで確認する [SPEC-3-01]

使い捨てのSQLiteと空きポートでFastAPIを起動し、別のGoプロセスから作業開始を要求する。CLIの表示とSQLAlchemyの保存件数を確認する。実在するテスト名は `test_st_3_01_go_client_starts_activity_through_fastapi`。

## 設計上の境界と確認

### AD-3-01: 各単位は相手の内部実装ではなくHTTPへ依存する [SPEC-3-01]

FastAPIとSQLAlchemyは `backend/worklog-api`、GoのCLIは `client/worklog-cli` に置く。それぞれが依存関係、起動、検査を自分の中へ持ち、Go側はバックエンドのPythonコードを読み込まずHTTPアダプタを使う。バックエンドの構成責任は `ApplicationFactory` へ閉じ、モジュール直下の自由関数へ流れを置かない。

### IT-3-01: GoのHTTPアダプタと公開する要求・応答を確認する [AD-3-01]

実際のHTTPサーバーへGoのアダプタから要求し、JSONの入力と、識別子、作業名、開始時刻を持つ応答を確認する。実在するテスト名は `TestIT_3_01_GatewayStartsActivityThroughHTTPContract`。

### AD-3-02: 単位をまたぐHTTP契約を実装の外へ公開する [SPEC-3-01]

バックエンドが生成するOpenAPI（HTTPの要求と応答の約束）を `contracts/worklog-api.openapi.json` に置き、クライアントが相手の内部実装を読まずに連携内容を判断できるようにする。

### IT-3-02: 公開した契約とFastAPIの実物を一致させる [AD-3-02]

FastAPIが生成するOpenAPIと公開した契約を比較し、要求、応答、データの形がずれた時点で失敗させる。実在するテスト名は `test_it_3_02_published_openapi_matches_backend`。

## 実装の段

```text
Go Entry.Run
  → 命令を読む
  → 作業開始を依頼する
  → 結果を書く

Go ActivityGateway.Start
  → HTTP要求を作る
  → バックエンドへ送る
  → 応答を読む
```

## 対象外

配置だけで別々の運用へ分けること、Web・モバイルの実装、認証、契約からのコード自動生成は行わない。個別配備やデータ所有を分ける理由が生まれるまでは、一つのリポジトリで扱う。

## 現在像の更新先

`110_requirements` のSC-001にGo CLIの入口別経路と例外を足し、REQ-001、AC-002を更新する。`150_system` の全体構造、SC-001のGo CLIシーケンス、データ所有の説明を更新する。作業そのものの保存形式は変わらないため、データの実体と不変条件は変更しない。
