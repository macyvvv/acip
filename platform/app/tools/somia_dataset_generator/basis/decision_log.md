# Decision Log

- D001: ゴールはLoRA用データセット生成。画像生成一般化は行わない。
- D002: 五層アーキテクチャを凍結。
- D003: 独自DSL、AST、Knowledge Base、自動自己最適化を不採用。
- D004: promptは派生成果物。正本はversioned specificationとplan。
- D005: 件数固定とcoverageを併用。採択件数を完了条件とし、bucket最低数を制約とする。
- D006: 自動reviewは補助。人手確認可能な証跡を必須とする。
- D007: Airiを参照実装とし、固定後に他キャラクターへschema適用する。
