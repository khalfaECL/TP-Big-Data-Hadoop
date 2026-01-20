#!/usr/bin/env python3

import sys


def emit(key, a_vals, b_vals):
    total = 0.0
    for k, a in a_vals.items():
        b = b_vals.get(k)
        if b is not None:
            total += a * b
    if abs(total - int(total)) < 1e-9:
        total = int(total)
    print(f"{key}\t{total}")


current_key = None
a_vals = {}
b_vals = {}

for raw_line in sys.stdin:
    line = raw_line.strip()
    if not line:
        continue
    try:
        key, value = line.split("\t", 1)
    except ValueError:
        continue

    if current_key is None:
        current_key = key

    if key != current_key:
        emit(current_key, a_vals, b_vals)
        a_vals = {}
        b_vals = {}
        current_key = key

    parts = value.split(",")
    if len(parts) < 3:
        continue
    matrix = parts[0]
    try:
        k = int(parts[1])
        v = float(parts[2])
    except ValueError:
        continue

    if matrix == "A":
        a_vals[k] = a_vals.get(k, 0.0) + v
    elif matrix == "B":
        b_vals[k] = b_vals.get(k, 0.0) + v

if current_key is not None:
    emit(current_key, a_vals, b_vals)
