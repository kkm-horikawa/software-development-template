# Software Development Template

要求から設計、実装、検証、Pull Requestまでを、一つの利用体験でつなぐための公開テンプレートです。

特定のフレームワークを先に選ぶのではなく、業務の言葉、変更を閉じ込める分割、内向きの依存、入口から順に読めるコードを基準にします。仕組みの厚さは、業務規則の複雑さと失敗時の影響に合わせます。

## 使い始める

1. GitHubの「Use this template」から新しいリポジトリを作ります。
2. このREADMEを、作る製品の説明へ書き換えます。
3. [開発の進め方](docs/000_process.md)を読み、最初のIssueを書きます。
4. [増分の雛形](docs/increments/_template.md)で設計とテストを対にします。
5. 実装後に `just check` を実行し、Pull Requestで観測した結果を返します。

```console
$ just check
文書の構造: OK
要求からテストの対応: OK
機密らしい文字列: OK
Python静的検査: OK
FastAPI実例: OK
Go実例: OK
トップダウン構造: OK
```

`just` がない環境では `./scripts/check-all.sh` でも同じ検査を実行できます。必要なのはPython 3、uv、Goです。

## このテンプレートが守ること

- Issueは、作る部品ではなく、誰の何がどう変わればよいかを書く。
- 一回の増分で、外から見える振る舞いとそのテスト、設計上の境界とそのテストを対にする。
- 機能単位で変更を閉じ込め、その内側で必要な分だけDDDとクリーンアーキテクチャを使う。
- 公開入口を実行できる目次にし、同じ粒度のメソッドを上から順に呼ぶ。
- Pull Requestは予定ではなく、実際に入力して観測した結果を書く。

詳しい判断基準は[設計原則](docs/010_design-principles.md)、コードの読み順は[実装構造](docs/020_code-structure.md)、確認方法は[テスト](docs/030_testing.md)にあります。

## 構成

```text
.github/                    Issue・Pull Request・自動検査
docs/                       開発の正典、増分、決定記録
examples/python/fastapi/    FastAPIとSQLAlchemyを使う実例
examples/go/topdown/        同じ読み順をGoで示す比較用の実例
scripts/                    ローカルとCIで共有する検査
AGENTS.md                   AIと人が最初に読む作業規則
```

FastAPIとSQLAlchemyを使う実例を主にし、GoのCLIを比較用に置いています。どちらも採用技術を強制するものではありません。別の言語やWebの道具へ置き換えるときも、入口から一段ずつ詳しくなる読み順と、依存を業務の規則へ向ける境界を保ってください。

## ライセンス

[MIT License](LICENSE)で利用できます。
