#!/usr/bin/python3

import itertools
import random


def if_(x, cond):
    if cond:
        return x
    else:
        return 0


all_variants = list(
    itertools.product(
        *[
            list(d.items())
            for d in [
                {"alg": 0, "lisp": 0, "asm": 0, "forth": 0},  # 0 lang
                {"acc": 0, "cisc": 0, "risc": 0, "stack": 0},  # 1 isa
                {"neum": 0, "harv": 0},  # 2 mem
                {"hw": 0, "mc": 1},  # 3 cu
                {"tick": 0},  # 4 acurate
                {"binary": 0},  # 5 machine
                {"stream": 0, "trap": 1},  # 6 io
                {"mem": 0, "port": 0},  # isa_io
                {"cstr": 0, "pstr": 0},  # string
                {
                    "prob1": 0,
                    "prob2": 0,
                },  # euler_problem
                {
                    "pipeline": 0,
                    "cache": 0,
                    "vector": 0,
                    "superscalar": 0,
                },  # complexity
            ]
        ]
    )
)


simplify_rule = {
    # "alg": "asm",
    # "lisp": "asm",
    # "cisc": "risc",
    # "mc": "hw",
    # "trap": "stream",
    # "tick": "instr",
    # "binary": "struct",
}


def simplify(v):
    if v in simplify_rule:
        return f"{v} -> {simplify_rule[v]}"
    return v


SKIP = 100

evaluate = [
    # spi only for trap
    # lambda v: if_(SKIP, 'spi' in v and not 'trap' in v),
    # forth only for stack
    # lambda v: if_(SKIP, 'forth' in v and not 'stack' in v),
    # pipeline only for risc
    # lambda v: if_(SKIP, 'pipeline' in v and not 'risc' in v),
]

variants = []
for v in all_variants:
    opts = [e[0] for e in v]
    opts_with_simplify = [simplify(e) for e in opts]
    desc = " | ".join(opts_with_simplify)

    complexity = 0.0 + sum([e[1] for e in v])
    for ev in evaluate:
        complexity += ev(opts)

    if 1 <= complexity <= 1:
        variants.append((complexity, desc, opts))

# for (c, d, _opts) in variants:
#     print(c, d)

random.shuffle(variants)

# groups = {}
# for complexity, desc, opts in variants:
#     key = (opts[0], opts[1], opts[3], opts[6], opts[7])
#     # key = tuple(opts[:-2])
#     groups.setdefault(key, []).append((complexity, desc, opts))

# variants = []
# while sum([len(group) for group in groups.values()]) > 0:
#     wave = [group.pop() for group in groups.values() if len(group) > 0]
#     random.shuffle(wave)
#     variants.extend(wave)

for complexity, desc, opts in variants:
    print(
        desc,
        # complexity,
    )
