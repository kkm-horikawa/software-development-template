# INC-1 HTTPから作業を始める

対応Issue: #1
対応シナリオ: SC-001
対応要求: REQ-001、AC-SC001-01、AC-SC001-02

> 作業記録アプリのサンプル増分です。新しい製品では最初のIssueへ着手する前に削除してください。

## 変える体験

作業を記録する人が、FastAPIのHTTP入口へ作業名を渡し、SQLAlchemyを通して保存された結果を受け取れる。同じ利用の流れをGoのCLIクライアントからも使える。

## 外から見える振る舞いと確認

### SPEC-1-01: HTTPから作業を始め、保存した内容を返す [AC-SC001-01] [AC-SC001-02]

`POST /activities` へ `{"title":"設計を書く"}` を送ると、応答状態201と、識別子、作業名、開始時刻を返し、SQLAlchemyを通してSQLiteへ一件保存する。空の作業名は応答状態422と理由を返し、保存しない。

### ST-1-01: FastAPIの入口から応答と保存結果を確認する [SPEC-1-01]

固定した識別子と時刻でHTTP入口を実行し、正常な作業名には応答状態201と開始結果、空の作業名には応答状態422と理由が返ることを確認する。

- 実行物: `backend/worklog-api/tests/acceptance/sc_001/test_http_start_activity.py::test_http_start_activity`
- 実行物: `backend/worklog-api/tests/acceptance/sc_001/test_http_start_activity.py::test_http_start_activity`

### SPEC-1-02: GoのCLIで作業開始の流れを実行できる [AC-SC001-01] [AC-SC001-02]

GoのCLIへ `start "設計を書く"` を渡すと、作業開始の利用手順へ渡し、返された結果を `開始: 設計を書く` と表示する。空の作業名は理由を標準エラーへ返し、開始結果を表示しない。

### ST-1-02: GoのCLI入口から開始結果を確認する [SPEC-1-02]

使い捨ての保存先でFastAPIを起動し、別プロセスのGo CLIへ正常な作業名と空の作業名を渡して、標準出力、標準エラー、終了状態を確認する。

- 実行物: `tests/acceptance/sc_001/test_cli_start_activity.py::test_sc001_ex02_cli_reports_started_activity`
- 実行物: `tests/acceptance/sc_001/test_cli_start_activity.py::test_sc001_ex04_cli_rejects_empty_title`

## 設計上の境界と確認

### AD-1-01: 入口、利用の手順、業務の規則、保存を内向きの依存で分ける [SPEC-1-01]

FastAPIの入口は入力と応答を受け持ち、利用の手順へ作業名を渡す。利用の手順は業務の型を作り、保存の境界へ依頼する。SQLAlchemyはその境界を実装し、業務の型はFastAPIと保存方法を知らない。入口の `post_activity` と利用の手順の `run` は、自分の型にある同じ粒度の段だけを呼ぶ。

### IT-1-01: 利用の手順と保存実装をつないで確認する [AD-1-01]

固定した識別子と時刻を渡した開始処理とSQLAlchemyの保存実装をつなぎ、作業名と開始時刻を持つ作業がSQLiteへ一件保存されることを確認する。

- 実行物: `backend/worklog-api/tests/test_sqlalchemy_repository.py::test_start_activity_persists_through_sqlalchemy`

### AD-1-02: Goでも同じ依存方向と読み順を保つ [SPEC-1-02]

GoのCLI、利用の手順、業務の型、HTTP境界を内向きの依存で分ける。入口と利用の手順の `Run` は、自分の型にある同じ粒度の段だけを呼ぶ。

### IT-1-02: Goの利用手順とHTTP境界をつないで確認する [AD-1-02]

固定した応答を返すHTTP境界を開始処理へ渡し、整えた作業名を境界へ依頼して、識別子と開始時刻を持つ結果を返すことを確認する。

- 実行物: `client/worklog-cli/internal/usecase/work/start_work_test.go::TestStartWorkRequestsStartedActivity`

## 実装の段

```text
ActivityEndpoint.post_activity
  → 作業名を読む
  → 作業開始の手順へ渡す
  → 応答へ変える

StartActivity.run
  → 作業名を作る
  → 作業を始める
  → 保存を依頼する

Goの Entry.Run、StartWork.Run、ActivityGateway.Start も同じ粒度の段で進む
```

## 対象外

本番向けの認証、一覧や終了などの別機能、データベース移行、TypeScriptの実例は作らない。二つの例は、設計と言語の関係を見比べるための小さな実証として置く。

## 現在像の更新先

`110_requirements` のSC-001、REQ-001、受入条件と具体例と、`150_system` の全体構造、SC-001にあるHTTPとGo CLIの入口別シーケンス、データの構造を更新する。
