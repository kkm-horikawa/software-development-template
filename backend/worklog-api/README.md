# FastAPIとSQLAlchemyのバックエンド例

独立して配備できる作業記録バックエンドです。作業を始めるHTTP APIを題材に、FastAPIの入口、利用の手順、業務の規則、SQLAlchemyの保存をつないでいます。

```text
POST /activities
  → ActivityEndpoint.post_activity
      → 作業名を読む
      → 作業開始の手順へ渡す
      → 応答へ変える
  → StartActivity.run
      → 作業名を作る
      → 作業を始める
      → 保存を依頼する
  → Activity（業務の型）
  ← SQLAlchemyActivityRepository（保存の実装）
```

## APIを動かす

```console
$ uv sync
$ uv run uvicorn worklog.main:factory --factory --reload
```

別の端末から作業を始めます。

```console
$ curl -i http://127.0.0.1:8000/activities \
    -H 'Content-Type: application/json' \
    -d '{"title":"設計を書く"}'
HTTP/1.1 201 Created
...
{"id":"...","title":"設計を書く","started_at":"..."}
```

既定では `activities.sqlite3` へ保存します。HTTPの確認を自動で通すには、リポジトリ直下から `just example` を実行します。これは使い捨てのSQLiteへ実際に保存し、応答と保存件数を表示します。

公開する要求と応答は [`contracts/worklog-api.openapi.json`](../../contracts/worklog-api.openapi.json) にあります。クライアントはこの契約へ依存し、このディレクトリのPythonコードを直接読み込みません。Goクライアントまでつなぐ例は、リポジトリ直下から `just example-go` を実行してください。

`tests/test_method_flow.py` はPythonの構文木を読み、HTTP入口と利用の手順が自分の型の段だけを呼ぶことを検査します。正常例と、外部処理や自由関数を直接呼ぶ違反例の両方があります。

この例は、すべての機能へ同じ層数を強制する雛形ではありません。業務規則が薄い処理では境界を減らしても、入口から同じ粒度で読む規則は保てます。
