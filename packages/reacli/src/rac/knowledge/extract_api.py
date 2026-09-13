#!/usr/bin/env python3
"""extract_api.py — ReaScript v777 官方文档 → api_index.json (纯标准库)

用法: python3 extract_api.py <reascript_api_html> <输出目录>

HTML 结构 (官方生成文档):
  <a name="FuncName"><hr></a><br>
  <div class="c_func">...C...</div>
  <div class="e_func">...EEL2...</div>
  <div class="l_func">...<code><i>boolean</i> retval = reaper.Func(<i>Type</i> arg)</code>...</div>
  <div class="p_func">...Python...</div>
  描述文本 (到下一个 <a name= 或文件尾)
"""
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

FUNC_RE = re.compile(r'<a name="([A-Za-z0-9_]+)"><hr></a><br>')
LUA_RE = re.compile(r'<div class="l_func">.*?<code>(.*?)</code>', re.S)
TAG_RE = re.compile(r"<[^>]+>")


def clean(s: str) -> str:
    s = TAG_RE.sub("", s)
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def parse_lua_sig(sig: str):
    """两种形态:
    'boolean retval, string buf = reaper.GetTrackName(MediaTrack track)'
    → returns=['boolean retval','string buf']
    'MediaTrack reaper.GetTrack(ReaProject proj, integer trackidx)' (无 =, 单返回)
    → returns=['MediaTrack']
    无返回值: 'reaper.Main_OnCommand(integer command, integer flag)' → returns=[]
    """
    sig = clean(sig)
    if "=" in sig:
        ret_part, call_part = sig.split("=", 1)
        returns = [r.strip() for r in ret_part.split(",") if r.strip()]
    else:
        call_part = sig
        m0 = re.match(r"^(.*?)\s*(reaper\.\w+\()", sig)
        if m0 and m0.group(1).strip():
            returns = [m0.group(1).strip()]
        else:
            returns = []
    m = re.search(r"reaper\.\w+\((.*)\)", call_part)
    params = []
    if m and m.group(1).strip():
        for p in re.split(r",\s*(?![^()]*\))", m.group(1)):
            p = p.strip()
            pm = re.match(r"(.+?)\s+(\w+)$", p)
            if pm:
                params.append({"type": pm.group(1).strip(), "name": pm.group(2)})
            else:
                params.append({"type": "", "name": p})
    return sig, returns, params


def main():
    src = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    text = src.read_text(encoding="utf-8", errors="replace")

    anchors = list(FUNC_RE.finditer(text))
    functions = {}
    with_lua = 0
    for i, a in enumerate(anchors):
        name = a.group(1)
        end = anchors[i + 1].start() if i + 1 < len(anchors) else len(text)
        block = text[a.start():end]
        lua_m = LUA_RE.search(block)
        lua_sig, returns, params = ("", [], [])
        if lua_m:
            lua_sig, returns, params = parse_lua_sig(lua_m.group(1))
            with_lua += 1
        # 描述 = p_func div 结束后到块尾
        p_end = block.find('class="p_func"')
        desc = ""
        if p_end != -1:
            div_close = block.find("</div>", p_end)
            if div_close != -1:
                desc = clean(block[div_close + 6:])
        functions[name] = {
            "lua_signature": lua_sig,
            "returns": returns,
            "params": params,
            "description": desc[:2000],
            "description_truncated": len(desc) > 2000,
            "has_lua": bool(lua_sig),
        }

    index = {
        "meta": {
            "source": f"{src.name} (REAPER v7.77 官方生成文档)",
            "generated": str(date.today()),
            "function_count": len(functions),
            "with_lua_sig": with_lua,
        },
        "functions": functions,
    }
    (out_dir / "api_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")

    report = {"function_count": len(functions), "with_lua_sig": with_lua,
              "samples": {k: functions.get(k, {}).get("lua_signature", "MISSING")
                          for k in ["GetTrack", "SetMediaTrackInfo_Value",
                                    "InsertEnvelopePoint", "AddProjectMarker",
                                    "Main_OnCommand"]}}
    (out_dir / "extract_api_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
