# music_platform static site

music_platform の公開HTMLサイト。

## ローカル確認

```bash
python3 -m http.server 8787 --bind 127.0.0.1 --directory businesses/music_platform/platform/mockups/static_site
```

http://127.0.0.1:8787/

## 主要導線

1. Home
2. Events
3. Event detail
4. Join
5. Songs
6. Song entry
7. My
8. Recommendation
9. Emergency
10. Organizer setup/build/run
11. Platform notification gate

## 設計原則

- SPファースト
- 状態・判断・操作を中心にする
- 会への参加登録と曲別エントリーを分離する
- 参加締切後の飛び入り演奏参加は扱わない
- 推薦通知は本人承諾なしにSongEntryへ変換しない
- 技術や曲品質を参加資格・推薦条件にしない
- dry_run/送信実行/停止判断はPlatform Super User専用
