"""Enumerate flattened redstone delay-chains for a given total delay."""

import argparse
from pprint import pprint
import sys
from collections import Counter, defaultdict
from functools import cache
from typing import NamedTuple


class Comp(NamedTuple):
    delay: int
    priority: int
    blocks: tuple

    @property
    def signature(self):
        return (self.priority, -self.delay)

    def __repr__(self):
        return "C" + repr(self.blocks)


# Insert custom subcomponents here, e.g. Comp(6, -1, ("-", "R2", "C")).
COMPONENTS = [
    Comp(8, -3, ("R4",)),
    Comp(6, -3, ("R3",)),
    Comp(4, -3, ("R2",)),
    Comp(2, -3, ("R1",)),
    Comp(8, -1, ("-", "R4")),
    Comp(6, -1, ("-", "R3")),
    Comp(4, -1, ("-", "R2")),
    Comp(2, -1, ("C",)),
    Comp(2, -1, ("-", "R1")),
    Comp(2, 0, ("-", "C")),
]

assert all(c.blocks for c in COMPONENTS), "components must have >= 1 block"
ORDER = tuple(sorted(COMPONENTS, key=lambda c: (c.priority, -c.delay)))
START = tuple([c for c in ORDER if c.blocks[0] == "-"])


@cache
def _body(remaining: int, order=ORDER):
    out = defaultdict(list)

    for c in order:
        if c.delay > remaining:
            continue
        if remaining == c.delay:
            out[(c.signature,)].append(c.blocks)
        else:
            for signature, rests in _body(remaining - c.delay).items():
                for rest in rests:
                    out[(c.signature, *signature)].append(c.blocks + rest)

    return dict(out)


def chains(total: int):
    return _body(total, START)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("total", type=int, help="total delay to enumerate")
    ap.add_argument("count", nargs="*", type=int, help="total element count")
    args = ap.parse_args()

    spellings = chains(args.total)

    counts = Counter(len(opt) for opts in spellings.values() for opt in opts)

    tileset = []
    for sig in sorted(spellings):
        opts = spellings[sig]
        if args.count:
            opts = [opt for opt in opts if len(opt) in args.count]
        if opts:
            tileset.append(min(opts, key=len))

    for chain in tileset:
        print(*chain)

    print(len(tileset), "chains", file=sys.stderr)
    for length in sorted(counts):
        print(f"length {length} chains: {counts[length]}", file=sys.stderr)


if __name__ == "__main__":
    main()
