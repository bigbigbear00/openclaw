#!/usr/bin/env python3
"""/new 后自检（只读）：用于快速发现 roster/bindings/session 串线。

不做任何配置修改，只输出检查结果与建议。
"""

import json
from pathlib import Path

OPENCLAW_JSON = Path("/Users/apple/.openclaw/openclaw.json")
AGENTS_DIR = Path("/Users/apple/.openclaw/agents")

EXPECTED_AGENTS = [
    "main",
    "ctf-director",
    "vn-realestate",
    "news-analyst",
    "nba-expert",
    "library-keeper",
    "designer",
    "writer-editor",
]

EXPECTED_BINDINGS = {
    "nba-expert": "-4995447684",
    "vn-realestate": "-5151557628",
    "news-analyst": "-5261774282",
    "library-keeper": "-5137214022",
    "ctf-director": "-5231717830",
    "designer": "-5175626021",
    "writer-editor": "-5260834117",
}


def load_config():
    return json.loads(OPENCLAW_JSON.read_text(encoding="utf-8"))


def check_agents_list(cfg):
    ids = [a.get("id") for a in cfg.get("agents", {}).get("list", [])]
    missing = [a for a in EXPECTED_AGENTS if a not in ids]
    extra = [a for a in ids if a and a not in EXPECTED_AGENTS]
    return {"present": ids, "missing": missing, "extra": extra}


def check_bindings(cfg):
    bindings = cfg.get("bindings", [])
    seen = {}
    for b in bindings:
        aid = b.get("agentId")
        peer = (b.get("match") or {}).get("peer") or {}
        gid = str(peer.get("id")) if peer.get("kind") == "group" else None
        if aid and gid:
            seen.setdefault(aid, set()).add(gid)

    problems = []
    for aid, gid in EXPECTED_BINDINGS.items():
        got = sorted(seen.get(aid, []))
        if gid not in got:
            problems.append({"agentId": aid, "expected": gid, "got": got})
    return {"seen": {k: sorted(list(v)) for k, v in seen.items()}, "problems": problems}


def check_main_group_sessions():
    p = AGENTS_DIR / "main" / "sessions" / "sessions.json"
    if not p.exists():
        return {"exists": False, "groupSessions": []}
    d = json.loads(p.read_text(encoding="utf-8"))
    groups = []
    for k, v in d.items():
        if isinstance(v, dict) and v.get("channel") == "telegram" and v.get("chatType") == "group":
            groups.append({"key": k, "groupId": str(v.get("groupId")), "subject": v.get("subject")})
    return {"exists": True, "groupSessions": groups}


def main():
    cfg = load_config()
    out = {
        "agents_list": check_agents_list(cfg),
        "bindings": check_bindings(cfg),
        "main_group_sessions": check_main_group_sessions(),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
