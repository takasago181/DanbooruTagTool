# CORE_TAG_SET_SCHEMA.md

## Core Tag Setとは

Special Core Dictionary から選んだ1個以上の Special を、
「この生成で何を出したいか」を表す第一級オブジェクトとして扱う。

単なる selected_tags の別名ではない。

内部では最低限:
- Core Tag Set
- Auxiliary Tags
- LoRA
を分離する。

## v1 minimum schema

```json
{
  "core_set_id": "uuid-or-stable-id",
  "core_set_name": "user label",
  "special_tag_ids": ["SPECIAL_ID_1", "SPECIAL_ID_2"],
  "memo": "",
  "created_at": "ISO-8601"
}
```

## v1で必要

- Specialタグを核へ追加/削除
- 現在の核を常時表示
- 核を名前付きで保存
- 保存した核を呼び出す
- 補助タグだけ外して核を残せる
- Prompt生成時に核と補助を内部的に区別

## v1で不要

- Core Setの継承
- version tree
- nested set
- 複合テンプレート管理
- 補助セットとの高度な組合せ管理
- cloud sync
- collaborative presets

## 原則

Core Setは原則Special Core Dictionary由来。現在のproduction snapshot/corpusは
互換上 `Special2788` として保持される。
All Danbooruタグを勝手にCoreへ昇格させない。

将来必要ならユーザー操作で例外を追加できる余地は残してよいが、
v1では実装しない。
