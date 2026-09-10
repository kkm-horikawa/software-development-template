# GoのCLIクライアント例

`backend/worklog-api` へ作業開始を依頼する、独立して配布できるCLIクライアントです。バックエンドのPythonコードを読み込まず、公開されたHTTP契約を使います。

```text
worklog start <作業名>
  → cli.Entry.Run
      → 開始命令を読む
      → 作業開始の手順へ渡す
      → 結果を書く
  → usecase.StartWork.Run
      → 作業名を作る
      → HTTP境界へ開始を依頼する
  → api.ActivityGateway.Start
      → HTTP要求を作る
      → バックエンドへ送る
      → 応答を読む
```

## バックエンドへつなぐ

先に `backend/worklog-api` を起動し、このディレクトリで実行します。

```console
$ WORKLOG_API_BASE_URL=http://127.0.0.1:8000 go run ./cmd/worklog start '設計を書く'
開始: 設計を書く
```

リポジトリ直下から `just example-go` を実行すると、使い捨てのSQLiteと空きポートでFastAPIを起動し、このクライアントから要求して、保存件数まで確認できます。

`internal/architecture` はGoの構文木を読み、入口、利用の手順、HTTP境界が自分の型の段だけを呼ぶことを検査します。Webやモバイルのクライアントを増やすときも、別の `client/<製品>` として依存関係と配布周期を閉じ込めます。
