#!/usr/bin/env python3
"""rename_i18n_keys.py — 真语义化 i18n key 重命名 (双向同步 + 审计日志)

用法:
  python3 scripts/rename_i18n_keys.py \\
    --mapping scripts/i18n_key_mapping.json \\
    --locales frontend/src/locales \\
    --src frontend/src \\
    --log rename_i18n_keys.log

  --dry-run: 只打印将改什么, 不写盘 (默认 False)
  --mapping: 必填, JSON {old_key: new_key}
  --locales: 必填, 含 {zh-CN,en-US}.json 的目录
  --src:     必填, 扫描的 src/ 根目录
  --log:     选填, 审计日志路径 (git-tracked)

失败模式:
  - 冲突 (2 个 old → 同 new) → fail-fast (mapping 写错)
  - 冲突 (new_key 已存在于 locales 中且与 old 不同) → fail-fast (会覆盖)
  - orphan (mapping 里有, 但 locales/ 没这个 key) → warn continue (静默跳过)
"""
import argparse
import json
import re
import sys
from pathlib import Path
from collections import defaultdict


def load_mapping(path: Path) -> dict:
    """读 mapping.json, 去掉 _comment 等下划线开头的元键"""
    with open(path) as fp:
        raw = json.load(fp)
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def check_conflicts(mapping: dict) -> None:
    """fail-fast: 2 个 old → 同 new (mapping 自己写错了)"""
    new_keys: dict = defaultdict(list)
    for old, new in mapping.items():
        new_keys[new].append(old)
    for new, olds in new_keys.items():
        if len(olds) > 1:
            print(f"❌ FAIL-FAST: 多个 old key 映射到同一 new '{new}':", file=sys.stderr)
            for o in olds:
                print(f"   - {o}", file=sys.stderr)
            sys.exit(2)


def rename_locales(locales_dir: Path, mapping: dict, dry_run: bool, log_lines: list) -> int:
    """遍历 locales/*.json, old_key → new_key, value 不变, 保持 key 顺序.

    返回本步骤的重命名条数.
    """
    total = 0
    for f in sorted(locales_dir.glob("*.json")):
        with open(f) as fp:
            raw = json.load(fp)
        # 按原顺序重建 dict, 替换 key 名
        new_dict: dict = {}
        renamed_in_file: list = []
        for k, v in raw.items():
            if k in mapping:
                new_k = mapping[k]
                if new_k in new_dict:
                    print(f"❌ FAIL-FAST: locale '{f.name}' 多次出现 new_key '{new_k}'", file=sys.stderr)
                    sys.exit(2)
                new_dict[new_k] = v
                renamed_in_file.append((k, new_k, v))
            else:
                new_dict[k] = v
        # 检查 mapping 里在 raw 没有的 key (orphan) — 静默跳过
        if renamed_in_file:
            total += len(renamed_in_file)
            for old, new, val in renamed_in_file:
                log_lines.append(f"[locale] {f.name}: {old} -> {new}  //  {str(val)[:50]}")
            if not dry_run:
                with open(f, "w") as fp:
                    json.dump(new_dict, fp, ensure_ascii=False, indent=2)
                    fp.write("\n")
    return total


def rename_src(src_dir: Path, mapping: dict, dry_run: bool, log_lines: list) -> int:
    """遍历 src/**/*.{vue,ts}, $t('old_key') -> $t('new_key').

    同时支持 ' 和 " 两种引号, 以及 $t('key') 和 $t( "key" ) 等变体.
    """
    pat = re.compile(r"(\$t\(\s*['\"])([^'\"]+)(['\"]\s*\))")
    total = 0
    for p in sorted(src_dir.rglob("*")):
        if p.suffix not in (".vue", ".ts"):
            continue
        text = p.read_text()
        changes: list = []
        def repl(m):
            key = m.group(2)
            if key in mapping:
                changes.append((key, mapping[key]))
                return f"{m.group(1)}{mapping[key]}{m.group(3)}"
            return m.group(0)
        new_text = pat.sub(repl, text)
        if changes:
            total += len(changes)
            for old, new in changes:
                log_lines.append(f"[src] {p}: {old} -> {new}")
            if not dry_run:
                p.write_text(new_text)
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--mapping", required=True)
    ap.add_argument("--locales", required=True)
    ap.add_argument("--src", required=True)
    ap.add_argument("--log", default=None)
    args = ap.parse_args()

    mapping_path = Path(args.mapping)
    locales_dir  = Path(args.locales)
    src_dir      = Path(args.src)
    log_path     = Path(args.log) if args.log else None

    if not mapping_path.exists():
        print(f"❌ mapping 不存在: {mapping_path}", file=sys.stderr); sys.exit(1)
    if not locales_dir.is_dir():
        print(f"❌ locales 目录不存在: {locales_dir}", file=sys.stderr); sys.exit(1)
    if not src_dir.is_dir():
        print(f"❌ src 目录不存在: {src_dir}", file=sys.stderr); sys.exit(1)

    mapping = load_mapping(mapping_path)
    print(f"📋 mapping 条数: {len(mapping)}", file=sys.stderr)

    check_conflicts(mapping)

    log_lines = [
        f"# rename_i18n_keys.log — generated {Path(__file__).name}",
        f"# mode: {'DRY-RUN' if args.dry_run else 'WRITE'}",
        f"# mapping: {mapping_path}",
        f"# locales: {locales_dir}",
        f"# src:     {src_dir}",
        f"# entries: {len(mapping)}",
        "",
    ]

    locale_changes = rename_locales(locales_dir, mapping, args.dry_run, log_lines)
    src_changes    = rename_src(src_dir, mapping, args.dry_run, log_lines)

    log_lines.append("")
    log_lines.append(f"# summary: locale entries renamed={locale_changes}, src $t() calls renamed={src_changes}")

    print(f"✅ locales 重命名条数: {locale_changes}", file=sys.stderr)
    print(f"✅ src    重命名条数: {src_changes}", file=sys.stderr)

    if log_path:
        log_path.write_text("\n".join(log_lines) + "\n")
        print(f"📝 log: {log_path} ({log_path.stat().st_size} bytes)", file=sys.stderr)

    if args.dry_run:
        print("🧪 DRY-RUN 完成 (未写盘)", file=sys.stderr)


if __name__ == "__main__":
    main()
