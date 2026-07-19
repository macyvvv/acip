# music_platform static site mock

UX順序確認用の静的HTMLプロダクトモック。

## Scope

- 実サイト実装ではない
- API、認証、通知送信、永続化はない
- `SITE_PAGE_FLOW.mmd` のページ順序を確認するためのハードコード済み画面

## Run

```bash
cd businesses/music_platform/platform/mockups/static_site
python3 -m http.server 8787
```

Open:

```text
http://localhost:8787/
```

## Canonical assumptions

- 演奏参加は事前登録者のみ
- 飛び入り演奏参加なし
- 参加締切は開催日前
- 会への参加登録と曲への参加登録を分離
- 未成立救済の通常通知は機械が担う
- `dry_run` と通知エンジン操作は Platform Super User のみ
- スロット記号は `■` 充足済み/参加済み、`△` 空き枠

## Information hierarchy

このモックでは、実物に近い判断ができるように情報を3種類へ分ける。

1. `System record`: DB、監査ログ、運用責務として残る情報。
   - 例: 参加締切、参加可能パート、通知許可、担当上限、曲への参加登録、推薦監査。
2. `Current state`: その時点の状態表示。
   - 例: 参加登録済み、締切前、承諾待ち、候補ゼロ、送信不可。
3. `Guidance`: 判断を助ける補足説明。責務や保存対象ではない。
   - 例: 技術審査ではない、推薦は断れる、参加費は演奏参加コスト。

`Guidance` は常時表示せず、画面上の `i` ヘルプをタップ、hover、focus したときだけ
フローティング表示する。常時表示されるカードは `System record` または
`Current state` として扱う。心理的に重要な安心材料だけは短い常時表示バナーにする。

## Static route mapping

このモックは静的HTMLなので `.html` ルートを使う。正本Sitemapの抽象ルートとは
次の対応で読む。

| Static mock | Canonical intent |
| --- | --- |
| `/index.html` | `/` |
| `/events/index.html` | `/participant/discover` |
| `/events/show.html` | event detail under `/participant/discover` |
| `/participant/join.html` | 会への参加登録 section of `/participant/entry` |
| `/songs/index.html` | song discovery section of `/participant/build` |
| `/songs/show.html` | song detail under `/participant/build` |
| `/songs/entry.html` | 曲への参加登録 section of `/participant/entry` |
| `/songs/closed.html` | song-entry deadline blocked state |
| `/participant/my.html` | participant state hub |
| `/participant/recommendation.html` | recommendation decision under `/participant/build` |
| `/participant/recommendation-closed.html` | recommendation deadline blocked state |
| `/participant/run.html` | `/participant/run` |
| `/organizer/setup.html` | `/organizer/setup` |
| `/organizer/dashboard.html` | `/organizer/build` |
| `/organizer/rescue.html` | `/organizer/rescue` |
| `/organizer/run.html` | `/organizer/run` |
| `/platform/notification-gate.html` | `/platform/notification-gate` |
| `/emergency/index.html` | `/emergency` |
| `/timeline/index.html` | `/timeline` |

## Out of current mock scope

今回のモックは参加登録、曲参加、推薦、主催者救済、緊急連絡の順序確認に絞る。
次のSitemap要素は正本には残すが、この静的モックでは未作成。

- `/participant/review`
- `/organizer/review`
- `/review/retention`
- `/community/health`
- `/legal/*`
- `/run/recovery` の詳細分岐
