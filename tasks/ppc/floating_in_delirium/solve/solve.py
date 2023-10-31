#!/usr/bin/env python3

from typing import List

def convert_to_bool(a: str) -> str:
    # return f"((2.0 ** 61 + (256 + {a})) / 2.0 ** 9 - 4503599627370496)"
    return f"((2305843009213693952.0 + (256 + {a})) / 512 - 4503599627370496)"

def one_if_n(n: int, a: str) -> str:
    return "(" + convert_to_bool(f"{a} - {n} + 1") + " - " + convert_to_bool(f"{a} - {n}") + ")"

def map_values(a: str, values: List[str]):
    return "({})".format('+'.join(one_if_n(i, a) + f" * {v}" for i, v in enumerate(values)))

# def xor(a: str, b: str):
#     return map_values(a, [map_values(b, [i ^ j for j in range(256)]) for i in range(256)])

def main():
    print(map_values("a", [i ^ 42 for i in range(256)]))

if __name__ == "__main__":
    main()
