#!/usr/bin/env python3

from mrjob.job import MRJob
from mrjob.step import MRStep


def parse_line(line):
    parts = [p.strip() for p in line.rstrip("\n").split("\t")]
    if len(parts) != 6:
        return None
    _date, _time, city, category, amount_s, payment = parts
    try:
        amount = float(amount_s)
    except ValueError:
        return None
    return city, category, payment, amount


class MRWomensCashTopCity(MRJob):
    def steps(self):
        return [
            MRStep(mapper=self.mapper_filter, reducer=self.reducer_sum),
            MRStep(mapper=self.mapper_prepare_max, reducer=self.reducer_max),
        ]

    def mapper_filter(self, _, line):
        parsed = parse_line(line)
        if parsed is None:
            return
        city, category, payment, amount = parsed
        if category == "Women's Clothing" and payment == "Cash":
            yield city, amount

    def reducer_sum(self, city, amounts):
        yield city, sum(amounts)

    def mapper_prepare_max(self, city, total):
        yield None, (total, city)

    def reducer_max(self, _, values):
        max_city = None
        max_total = None
        for total, city in values:
            if max_total is None or total > max_total:
                max_total = total
                max_city = city
        if max_city is not None:
            yield max_city, max_total


if __name__ == "__main__":
    MRWomensCashTopCity.run()
