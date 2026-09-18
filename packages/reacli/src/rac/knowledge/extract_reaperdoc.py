#!/usr/bin/env python3
"""extract_reaperdoc.py — ReaperDoc TS 数据 → 知识库产物 (纯标准库)

用法: python3 extract_reaperdoc.py <ReaperDoc目录> <输出目录>

产出:
  raw/reaperdoc_docdata.json      — DOC_DATA 原始结构 (对账基准)
  raw/reaperdoc_rppstructure.json — RPP_STRUCTURE 注释树
  rpp_schema.json                 — KEY → 字段语义 (label-level; operation-grade
                                    元数据逐步补充)
  annotated_tree.md               — 注释树 markdown (few-shot 用)
  extract_report.json             — 对账报告 (数量/TODO/NOT CLEAR 统计)

只依赖 Python 标准库。TS 解析为手写字面量 tokenizer (非通用 TS parser,
仅覆盖 ReaperDoc 数据文件语法: 对象/数组/字符串/数字/布尔/注释/尾逗号)。
"""
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# TS 字面量 tokenizer + parser
# ---------------------------------------------------------------------------

class TSLiteralParser:
    def __init__(self, text: str):
        self.s = text
        self.i = 0
        self.n = len(text)

    def error(self, msg):
        line = self.s.count("\n", 0, self.i) + 1
        raise SyntaxError(f"TS literal parse error at line {line}: {msg}")

    def skip_ws(self):
        while self.i < self.n:
            c = self.s[self.i]
            if c in " \t\r\n":
                self.i += 1
            elif self.s.startswith("//", self.i):
                self.i = self.s.find("\n", self.i)
                if self.i == -1:
                    self.i = self.n
            elif self.s.startswith("/*", self.i):
                end = self.s.find("*/", self.i)
                if end == -1:
                    self.error("unterminated block comment")
                self.i = end + 2
            else:
                break

    def peek(self):
        return self.s[self.i] if self.i < self.n else ""

    def expect(self, ch):
        self.skip_ws()
        if self.peek() != ch:
            self.error(f"expected {ch!r}, got {self.peek()!r}")
        self.i += 1

    def parse_string(self):
        quote = self.s[self.i]
        assert quote in "'\"`"
        self.i += 1
        buf = []
        while self.i < self.n:
            c = self.s[self.i]
            if c == "\\":
                nxt = self.s[self.i + 1]
                buf.append({"n": "\n", "t": "\t", "r": "\r", "\\": "\\",
                            "'": "'", '"': '"', "`": "`", "0": "\0"}.get(nxt, nxt))
                self.i += 2
            elif c == quote:
                self.i += 1
                return "".join(buf)
            else:
                buf.append(c)
                self.i += 1
        self.error("unterminated string")

    def parse_number(self):
        m = re.match(r"-?\d+(\.\d+)?([eE][+-]?\d+)?", self.s[self.i:])
        if not m:
            self.error("bad number")
        self.i += m.end()
        txt = m.group(0)
        return float(txt) if ("." in txt or "e" in txt.lower()) else int(txt)

    def parse_ident(self):
        m = re.match(r"[A-Za-z_$][A-Za-z0-9_$]*", self.s[self.i:])
        if not m:
            self.error(f"unexpected char {self.peek()!r}")
        self.i += m.end()
        return m.group(0)

    def parse_value(self):
        self.skip_ws()
        c = self.peek()
        if c == "{":
            return self.parse_object()
        if c == "[":
            return self.parse_array()
        if c in "'\"`":
            return self.parse_string()
        if c == "-" or c.isdigit():
            return self.parse_number()
        ident = self.parse_ident()
        if ident == "true":
            return True
        if ident == "false":
            return False
        if ident in ("null", "undefined"):
            return None
        self.error(f"unexpected identifier {ident!r}")

    def parse_object(self):
        obj = {}
        self.expect("{")
        first = True
        while True:
            self.skip_ws()
            if self.peek() == "}":
                self.i += 1
                return obj
            if not first:  # 强制逗号分隔, 非法字面量不吃
                self.expect(",")
                self.skip_ws()
                if self.peek() == "}":  # 尾逗号
                    self.i += 1
                    return obj
            first = False
            if self.peek() in "'\"":
                key = self.parse_string()
            else:
                key = self.parse_ident()
            self.expect(":")
            obj[key] = self.parse_value()

    def parse_array(self):
        arr = []
        self.expect("[")
        first = True
        while True:
            self.skip_ws()
            if self.peek() == "]":
                self.i += 1
                return arr
            if not first:
                self.expect(",")
                self.skip_ws()
                if self.peek() == "]":
                    self.i += 1
                    return arr
            first = False
            arr.append(self.parse_value())


def extract_const(text: str, const_name: str):
    """定位 `const_name` 声明并解析其字面量。

    锚定行首声明 (`export const X: T =` / `const X =`)，防止注释/字符串中
    出现的同名文本被误定位。"""
    m = re.search(
        r"^\s*(?:export\s+)?const\s+" + re.escape(const_name) + r"[^=]*=\s*",
        text, flags=re.M)
    if not m:
        raise ValueError(f"const {const_name} declaration not found")
    p = TSLiteralParser(text[m.end():])
    return p.parse_value()


# ---------------------------------------------------------------------------
# schema 构建
# ---------------------------------------------------------------------------

FIELD_LABEL_RE = re.compile(r"field\s+(\d+)(?:\s*-\s*(\d+))?", re.I)


def build_schema(doc_data: list, source_commit: str, generated: str) -> dict:
    keys = {}
    sections = []
    collisions = []
    for sec in doc_data:
        sections.append({"id": sec["id"], "title": sec.get("title", ""),
                         "subtitle": sec.get("subtitle", ""),
                         "entry_count": len(sec["entries"])})
        for entry in sec["entries"]:
            name = entry["name"]
            fields = []
            for f in entry.get("fields", []):
                label = f.get("label", "")
                m = FIELD_LABEL_RE.search(label)
                idx = int(m.group(1)) if m else None
                idx_end = int(m.group(2)) if (m and m.group(2)) else None
                sub = f.get("subFields") or []
                fields.append({
                    "index": idx,
                    "index_end": idx_end,
                    "label": label,
                    "type": f.get("type"),
                    "description": f.get("description", ""),
                    "enum_candidates": sub if sub else None,
                })
            # RPP KEY 是上下文敏感的: 同名 KEY 在不同 section 语义不同
            # (如 track:VOLPAN vs item:VOLPAN) — 键必须带上下文前缀
            qname = f"{sec['id']}:{name}"
            if name in {k.split(":", 1)[1] for k in keys}:
                collisions.append(name)
            keys[qname] = {
                "name": name,
                "section": sec["id"],
                "is_chunk": bool(entry.get("isChunk")) or name.startswith("<"),
                "fields": fields,
                "tags": entry.get("tags", []),
                # human-source = 源自人工验证的 ReaperDoc, 但本框架未逐条实机复核;
                # 实机复核后升级为 live (见 gap_registry.md C 节)
                "verified": "human-source",
                "source": "ReaperDoc",
            }
    return {
        "meta": {
            "source": f"ReaperDoc constants.ts @ {source_commit}",
            "generated": generated,
            "generator": "rac/knowledge/extract_reaperdoc.py",
            "verified_default": "human-source",
            "verified_levels": "human-source(源人工验证) < live(本框架实机复核) < human(本框架人工复核)",
            "section_count": len(sections),
            "key_count": len(keys),
            "key_format": "<section>:<KEY> — RPP KEY 上下文敏感, 同名不同义 "
                          "(如 track:VOLPAN 与 item:VOLPAN 字段语义不同), 查询必须带 section",
            "colliding_names": sorted(set(collisions)),
            "note": "enum_candidates 为 subFields 原文 ('0 = off'/'+2 = ...'), "
                    "语义需按上下文解读; operation-grade 元数据(defaults/range/"
                    "write_contract)逐步人工/实机补充",
        },
        "sections": sections,
        "keys": keys,
    }


# ---------------------------------------------------------------------------
# annotated_tree.md 构建
# ---------------------------------------------------------------------------

def render_tree(node: dict, lines: list, depth: int = 0):
    indent = "  " * depth
    key = node.get("key", "?")
    values = node.get("values")
    comment = node.get("comment")
    is_chunk = "children" in node and node["children"] is not None
    line = indent + key
    if values:
        line += " " + values
    if comment:
        line += "  # " + comment
    lines.append(line)
    for ch in node.get("children") or []:
        render_tree(ch, lines, depth + 1)
    if is_chunk and depth >= 0 and key.startswith("<"):
        lines.append(indent + ">")


def build_annotated_md(rpp_structure: dict, source_commit: str, generated: str) -> str:
    lines = []
    lines.append("# RPP 注释树（annotated_tree）")
    lines.append("")
    lines.append(f"> 来源: ReaperDoc rppStructure.ts @ {source_commit} | 生成: {generated}")
    lines.append("> ReaperDoc 注释树样例（上游人工维护的 RPP 结构示例，逐行注释）。")
    lines.append("> 读 RPP 时对照本文件理解结构；字段语义以 rpp_schema.json 为准。")
    lines.append("")
    lines.append("```")
    render_tree(rpp_structure, lines)
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    doc_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    import subprocess, datetime
    try:
        source_commit = subprocess.run(
            ["git", "-C", str(doc_dir), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        source_commit = "unknown"
    generated = datetime.date.today().isoformat()

    constants = (doc_dir / "constants.ts").read_text(encoding="utf-8")
    structure = (doc_dir / "rppStructure.ts").read_text(encoding="utf-8")

    doc_data = extract_const(constants, "DOC_DATA")
    rpp_structure = extract_const(structure, "RPP_STRUCTURE")

    (raw_dir / "reaperdoc_docdata.json").write_text(
        json.dumps(doc_data, ensure_ascii=False, indent=2), encoding="utf-8")
    (raw_dir / "reaperdoc_rppstructure.json").write_text(
        json.dumps(rpp_structure, ensure_ascii=False, indent=2), encoding="utf-8")

    schema = build_schema(doc_data, source_commit, generated)
    (out_dir / "rpp_schema.json").write_text(
        json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")

    md = build_annotated_md(rpp_structure, source_commit, generated)
    (out_dir / "annotated_tree.md").write_text(md, encoding="utf-8")

    # 对账报告
    todo_keys = [k for k, v in schema["keys"].items() if "TODO" in v["tags"]]
    notclear = [k for k, v in schema["keys"].items()
                if any("NOT CLEAR" in (f["description"] or "")
                       for f in v["fields"])]
    report = {
        "source_commit": source_commit,
        "generated": generated,
        "section_count": len(schema["sections"]),
        "sections": {s["id"]: s["entry_count"] for s in schema["sections"]},
        "key_count": schema["meta"]["key_count"],
        "todo_keys": todo_keys,
        "not_clear_keys": notclear,
    }
    (out_dir / "extract_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"commit": source_commit, "sections": report["sections"],
                      "keys": report["key_count"],
                      "todo": len(todo_keys), "not_clear": len(notclear)},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
