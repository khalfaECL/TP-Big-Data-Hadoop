#!/usr/bin/env python3

import os
import re
import sys

# Defaults match matrice.py (20x10 and 10x15). Override with env vars if needed.
A_ROWS = int(os.environ.get("A_ROWS", "20"))
A_COLS = int(os.environ.get("A_COLS", "10"))
B_COLS = int(os.environ.get("B_COLS", "15"))

_num_re = re.compile(r"[^0-9.\-]+")


def parse_number(token):
    token = _num_re.sub("", token)
    if token in ("", "-", ".", "-."):
        return None
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return None


def detect_matrix(tokens, file_path):
    if tokens and tokens[0] in ("A", "B"):
        return tokens[0], tokens[1:]
    file_lower = (file_path or "").lower()
    if "matricea" in file_lower:
        return "A", tokens
    if "matriceb" in file_lower:
        return "B", tokens
    env_name = os.environ.get("MATRIX_NAME", "")
    if env_name in ("A", "B"):
        return env_name, tokens
    return None, tokens


row_index = {"A": 0, "B": 0}

for raw_line in sys.stdin:
    line = raw_line.strip()
    if not line:
        continue

    tokens = [t for t in re.split(r"[,\s]+", line) if t]
    if not tokens:
        continue

    matrix, tokens = detect_matrix(tokens, os.environ.get("map_input_file", ""))
    if matrix is None:
        continue

    # Index format: i j value (or k j value for B)
    if len(tokens) == 3:
        i = parse_number(tokens[0])
        j = parse_number(tokens[1])
        v = parse_number(tokens[2])
        if i is None or j is None or v is None:
            continue
        i = int(i)
        j = int(j)
        if matrix == "A":
            k = j
            for out_j in range(B_COLS):
                print(f"{i},{out_j}\tA,{k},{v}")
        else:
            k = i
            for out_i in range(A_ROWS):
                print(f"{out_i},{j}\tB,{k},{v}")
        continue

    # Row format: values only, one row per line
    if len(tokens) > 3:
        r = row_index[matrix]
        row_index[matrix] += 1
        for c, token in enumerate(tokens):
            v = parse_number(token)
            if v is None:
                continue
            if matrix == "A":
                k = c
                for out_j in range(B_COLS):
                    print(f"{r},{out_j}\tA,{k},{v}")
            else:
                k = r
                j = c
                for out_i in range(A_ROWS):
                    print(f"{out_i},{j}\tB,{k},{v}")
