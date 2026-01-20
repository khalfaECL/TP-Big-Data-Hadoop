#!/usr/bin/env python3

import heapq

from mrjob.job import MRJob
from mrjob.step import MRStep


def parse_line(line):
    parts = [p.strip() for p in line.rstrip("\n").split("\t")]
    if len(parts) != 6:
        return None
    _date, _time, city, _category, amount_s, _payment = parts
    try:
        amount = float(amount_s)
    except ValueError:
        return None
    return city, amount


class MRTopCitiesBySales(MRJob):
    def configure_args(self):
        super().configure_args()
        self.add_passthru_arg(
            "--top-n",
            type=int,
            default=5,
            help="Number of top cities to output (default: 5)",
        )

    def steps(self):
        return [
            MRStep(mapper=self.mapper_city, reducer=self.reducer_sum),
            MRStep(mapper=self.mapper_prepare_top, reducer=self.reducer_top),
        ]

    def mapper_city(self, _, line):
        parsed = parse_line(line)
        if parsed is None:
            return
        city, amount = parsed
        yield city, amount

    def reducer_sum(self, city, amounts):
        yield city, sum(amounts)

    def mapper_prepare_top(self, city, total):
        yield None, (total, city)

    def reducer_top(self, _, values):
        top_n = self.options.top_n
        heap = []
        for total, city in values:
            item = (total, city)
            if len(heap) < top_n:
                heapq.heappush(heap, item)
            else:
                if item[0] > heap[0][0]:
                    heapq.heapreplace(heap, item)
        for total, city in sorted(heap, reverse=True):
            yield city, total


if __name__ == "__main__":
    MRTopCitiesBySales.run()
