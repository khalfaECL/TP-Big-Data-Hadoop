#!/usr/bin/env python3

from mrjob.job import MRJob


def parse_line(line):
    parts = [p.strip() for p in line.rstrip("\n").split("\t")]
    if len(parts) != 6:
        return None
    _date, _time, _city, category, amount_s, _payment = parts
    try:
        float(amount_s)
    except ValueError:
        return None
    return category


class MRCountByCategory(MRJob):
    def mapper(self, _, line):
        category = parse_line(line)
        if category is None:
            return
        yield category, 1

    def reducer(self, category, counts):
        yield category, sum(counts)


if __name__ == "__main__":
    MRCountByCategory.run()
