#!/usr/bin/env python3

from mrjob.job import MRJob


def parse_line(line):
    parts = [p.strip() for p in line.rstrip("\n").split("\t")]
    if len(parts) != 6:
        return None
    _date, _time, _city, category, amount_s, _payment = parts
    try:
        amount = float(amount_s)
    except ValueError:
        return None
    return category, amount


class MRSumByCategory(MRJob):
    def mapper(self, _, line):
        parsed = parse_line(line)
        if parsed is None:
            return
        category, amount = parsed
        yield category, amount

    def reducer(self, category, amounts):
        yield category, sum(amounts)


if __name__ == "__main__":
    MRSumByCategory.run()
