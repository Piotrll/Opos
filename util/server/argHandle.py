from typing import List, Dict, Any
import sys

"""
Small utility to decode a list of arguments into a dict of values.

Behavior:
- Accepts tokens like "key=value", "--key=value", "-k=value" -> {"key": value}
- Accepts tokens where a key and its value are separate: "-diag 3", "--opt true"
- Flags like "--flag" or "-f" (no following value) -> {"flag": True}
- Positional tokens (no dash, no '=') are collected under the "_" key as a list
- Repeated keys become lists of values
- Simple value coercion for int/float/true/false
"""

def _coerce_value(v: str):
    lv = v.lower()
    if lv == "true":
        return True
    if lv == "false":
        return False
    try:
        return int(v)
    except Exception:
        pass
    try:
        return float(v)
    except Exception:
        pass
    return v

def decode_args(args: List[str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    pos: List[str] = []

    def add(k: str, v):
        if k in out:
            if isinstance(out[k], list):
                out[k].append(v)
            else:
                out[k] = [out[k], v]
        else:
            out[k] = v

    i = 0
    while i < len(args):
        token = args[i]
        if "=" in token:
            k, v = token.split("=", 1)
            k = k.lstrip("-")
            add(k, _coerce_value(v))
        elif token.startswith("-"):
            k = token.lstrip("-")
            # If next token exists and is not another key, treat it as value
            if i + 1 < len(args) and not args[i + 1].startswith("-") and "=" not in args[i + 1]:
                i += 1
                add(k, _coerce_value(args[i]))
            else:
                add(k, True)
        else:
            pos.append(token)
        i += 1

    if pos:
        out["_"] = pos

    return out

if __name__ == "__main__":
    print(decode_args(sys.argv[1:]))