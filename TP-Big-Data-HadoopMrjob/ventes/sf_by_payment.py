#!/usr/bin/env python3

from mrjob.job import MRJob


def parse_line(line):
    parts = [p.strip() for p in line.rstrip("\n").split("\t")]
    if len(parts) != 6:
        return None
    _date, _time, city, _category, amount_s, payment = parts
    try:
        amount = float(amount_s)
    except ValueError:
        return None
    return city, payment, amount


class MRSanFranciscoByPayment(MRJob):
    def mapper(self, _, line):
        parsed = parse_line(line)
        if parsed is None:
            return
        city, payment, amount = parsed
        if city == "San Francisco":
            yield payment, amount

    def reducer(self, payment, amounts):
        yield payment, sum(amounts)


if __name__ == "__main__":
    MRSanFranciscoByPayment.run()
