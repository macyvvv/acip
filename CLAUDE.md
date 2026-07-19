# CLAUDE.md

本リポジトリで唯一の正本の運用指示書。`AGENTS.md` と `.codex/agents/*`（Codex CLI形式の
エージェント定義）は旧ChatGPT+Codex時代の記録として残すのみで、正本ではない（生きた優先順位は
`platform/docs/current/STATE.md` のRuntime Notes: `PROJECT.md` → `STATE.md` →
`CLAUDE.md` → `platform/basis/` → `platform/adr/` → Issue → PR → Conversation）。旧ファイル群の
儀式的フォーマット（Conclusion/Next Actionの強制順序、「Current Phase:」
フッターなど）には従わない。ChatGPT/Codexはセッション間の記憶を持たなかった
ためにこの儀式が必要だったが、Claude Codeは本ファイルと会話自体を記憶として
保持するため不要である。

## Mission

堅牢性・クリーンネス・長期保守性・再現性・引き継ぎ容易性・実行効率・継続的な
全体最適を最優先する。短期的な開発速度のために犠牲にしない。

## このリポジトリは何か

AIエージェントを中心に会社を運営する試み。GitHubが記録の一次情報源。全体像は
`platform/docs/current/PROJECT.md`、現状は`platform/docs/current/STATE.md`（必要な時に読めばよい）。

実プロダクトは `platform/app/products/`（kabukicho_survival_map, kabukicho_survival_map_mvp,
minimal_launch_brief_generator, repository_operational_summary）と
`platform/app/tools/approval_console_mvp`。注意: `kabukicho_survival_map` が本物の
フルスクラッチアプリ（HTML/CSS/JS、バックエンドなし）で、`kabukicho_survival_map_mvp`
は育たなかった旧・小規模版。両者を混同しない。それ以外の `platform/system/`, `platform/docs/`,
`platform/basis/`, `platform/adr/`, `platform/specs/`, `platform/contracts/` はガバナンスの足場で、プロダクト
コードよりはるかに大きい（約800ファイル・24k行）。この層への追加には懐疑的で
あるべきで、触るときはむしろ縮小する。

## Knowledge First

`platform/basis/` が正本（ADR-0037のガバナンス層見直しで44ファイルから整理済み。詳細は
`platform/basis/README.md`）：

- `platform/basis/CORE_PRINCIPLES.md` — 実際に効いているルールの記録。まずこれを読む。
- `platform/basis/057_boundary_validation_policy.md` — 境界検証ポリシー。
- `platform/basis/REPOSITORY_CONVENTIONS.md` — 命名規約。

設計・要件・アーキテクチャ・運用方針の変更時は該当する `platform/basis/` ファイルと
`platform/adr/*.md`（決定記録＝「なぜ今の形か」の本当の記録）を同期する。

## 実行方針とHard Rules（技術的に強制、文書だけではない）

- 作業前に計画を提示し承認を取得する。承認後はScope内で自律的に完遂してよい。
  Current Objectiveは変更しない — Scope内の改善は自律実行、Scope外は
  Parking Lotへ記録する。
- 局所最適ではなく全体最適を目的とする。作業単位ごとに、戦略・アーキテクチャ・
  実装・品質・UX・ドキュメント・運用への影響を俯瞰的に自己点検し、Project
  Goalとの整合性を継続的に監査する。改善案は自己批判と代替案比較を経てから
  採用する。
- アーキテクチャ・ガバナンス・責任境界・ワークフロー・データモデル・実行時挙動に
  影響する変更は作業を止めて確認を取り、`platform/adr/` にADRを追加・更新する。
- `main` への直接pushは禁止。常に feature branch → commit → push → PR →
  人間レビュー/マージ。ローカルガードは初回のみ
  `bash platform/system/scripts/git/install_hooks.sh` で有効化（`.git/hooks/`は
  git非追跡のためclone毎に手動要。GitHub側のbranch protectionは実はpublicリポジトリのため
  無料でも設定可能だが、現時点では未設定 — 詳細は`platform/docs/current/MAIN_PROTECTION_POLICY.md`）。
- 新しいdoc/script/workflowを追加する前に、同等のものが既に存在しないか
  （`platform/basis/`, `platform/adr/`, `platform/docs/current/`, `platform/system/`）確認し、あれば拡張・修正する。
  このリポジトリは重複が既に問題化している。
- 迎合しない。設計が過剰または一貫性を欠く場合はそう直接指摘する。
- 人間が保持する領域：戦略、承認、資本配分。Claudeが担う領域：アーキテクチャ、
  実装、リファクタリング、テスト、レビュー、PR作成。

## Interactive Agent Layer

`.claude/agents/` はinteractive Claude Code rolesの正本。現在は14 Ops、26 specialist agents、
`opsboard`の計41役割で構成する(うちVisualOpsはCreativeOps配下のサブ調整役で、opsboardには
直接報告しないため specialist 側でカウント — OpsBoard→CreativeOps→VisualOps→3専門役という
本リポジトリ初の3階層構造。PsychologyOps/UIUXDesignOps/WebDesignOpsの3件は追加時期不明のまま
`opsboard.md`未反映だったため2026-07-19に反映後、UIUXDesignOpsは既存の`ux-research`と同一責務と
判明したため同日中に統合・削除した — 「同時に使われる」は統合理由にならないが「名前が違うだけの
同一責務」は統合理由になる、という運用方針をここで確定させた)。BusinessOps、ProductOps、LegalOpsと
配下7役割は
`platform/adr/ADR-0041`で、cross-cutting役のEpistemicsOpsは`platform/adr/ADR-0043`で、同じく
cross-cutting役のTrainerOpsは`platform/adr/ADR-0044`で、somiaの美術担当CreativeOpsと配下6役割は
`platform/adr/ADR-0045`で追加、さらに哲学・心理学・リベラルアーツ・映像作家・アパレルスタイリストの
5役割が`platform/adr/ADR-0047`でCreativeOps配下に追加された(前3者はsomiaレビュー時の必須ロールで
あり任意ではない)。いずれもinteractive-only rolesであり、unattended registryには存在しない。
トレーナー役が蒸留した汎用的な教訓は
`platform/docs/current/PORTABLE_AGENT_LESSONS.md`にacip非依存の形でまとめ、他プロジェクトへの
持ち出しを想定する。

元の8 business-content rolesは自動実行側にも定義がある。`platform/adr/ADR-0039`の
dual-authority ruleに従い、共有役割のIO、contract、permissionを実質変更する場合は両方を
同期する。`.claude/agents/*.md`の存在から無人実行権限を推測してはならない。

### Agent呼び出しの階層規約(2026-07-19)

`.claude/agents/*`のどのロールも`Agent`ツールを付与されていない(全ファイルの
`tools:`行を確認済み) — つまりsubagentは他のsubagentを呼び出せない。「Reports to X」
「Manages: Y, Z」は呼び出し連鎖ではなく、実際に呼び出す主体(常にmain loop、つまり
Claude自身)が読んで従うべきメタデータに過ぎない。自動的な連鎖は技術的に存在しないため、
以下2つを毎回の運用規約として自分自身に課す:

1. **下方向の完全性**: Ops役割(またはVisualOpsのようなsub-coordinator)を「一般的な
   レビュー」目的で呼ぶ場合、そのロールのManages一覧全員を同一タスクの一部として呼ぶ
   ―自分の判断で一部だけ選ぶことをデフォルトにしない。多段階層(OpsBoard→CreativeOps→
   VisualOps→3専門役)は再帰的に適用する。タスクが明示的に狭いスコープ(「色だけ見て」)
   なら一部だけでよいが、その場合は「意図的に絞った」と明言する。EpistemicsOps/SecOps/
   TrainerOpsのようなcross-cutting役はManages一覧を持たないため対象外。OpsBoard自身は
   例外で、14 Ops全員ではなく「関連するOps」を判断して呼ぶのがOpsBoard自身の役目
   (`opsboard.md`に既述)。
2. **上方向のエスカレーション**: 専門役(specialist)を上位Opsを介さず直接呼んだ場合、
   レビューを完了とみなす前に、原則としてその上位Opsも呼ぶ(横断的な判断・調停は
   専門役単体では行われないため)。ここも意図的に専門役1つのみで完結させる場合は
   その旨を明言する。
3. somiaの philosophy-review/character-psychology/liberal-arts-review 必須ルール
   (`creativeops.md`)は、この規約をCreativeOps配下に先行適用していた前例であり、
   新しい義務を生むものではない。
4. 本当に機械的な並列実行(判断任せにしない全数呼び出し)が必要な場合は`Workflow`
   ツールを使う(ユーザーの明示的なopt-inが必要)。この規約はWorkflowの代替ではなく、
   通常の会話内で自分がAgentツールを手動で呼ぶ際の既定動作を定めるもの。

## UI Philosophy

機能美を目指す。優先順位：視線誘導 > 認知負荷低減 > 情報階層 > 一貫性 >
ミニマルデザイン > 操作効率 > アクセシビリティ。人間の認知特性を最優先する。

## Validation

- テスト: `python -m pytest -q`
- リポジトリ全体の自己検証: `python platform/system/scripts/validate_all.py`
- CIの `validate-all.yml` 相当の統合ステータス: `bash platform/system/scripts/check_repo_os_status.sh`

`platform/system/` または `platform/app/` 配下を変更してPRを開く前に実行する。

## Definition of Success

Robust / Clean / Maintainable / Reproducible / Testable / Transferable /
Scalable / Documented を満たすこと。
