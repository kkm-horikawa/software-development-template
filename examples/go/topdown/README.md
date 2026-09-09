# Goで入口から段を下りる最小例

FastAPIの主例と同じ作業開始を、GoのCLIで表した比較用の例です。

```text
cmd/example
  → cli.Entry.Run
      → 開始命令を読む
      → 作業開始の手順へ渡す
      → 結果を書く
  → usecase.StartWork.Run
      → 作業名を作る
      → 作業を始める
      → 保存を依頼する
  → domain.Activity
  ← repository/memory
```

```console
$ go run ./cmd/example start "設計を書く"
開始: 設計を書く
```

`internal/architecture` はGoの構文木を読み、入口と利用の手順が自分の型の段だけを呼ぶことを検査します。この例を製品の土台として強制せず、採用言語にかかわらず保つ読み順を見比べるために使います。
