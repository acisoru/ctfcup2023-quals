# rev | magick lock

## Information

В одной из лабороторий "Арбалетов Сибири" вы находите магическую дверь, она просит у вас некую hex строчку. Говорят, достаточно развитые технологии неотличимы от магии, верно?

You find a magick door in one "Arbalest of Siberia" laboratories, which asks for some hex string. They say: any technology sufficiently advenced is indistinguishable from magick, right?

## Public

Provide executable: [public/lock](public/lock).

## TLDR

Polynomial remainders modulo flag that should equal simple polynomials of degree 1, written in c++.

## Writeup (ru)

Нам дан исполняемый файл, который проверяет корректность флага следующий образом: превращает хекс строчку в байты и байты в полином очевидным образом (при этом коэффициент 31 степени должен быть равен 1), берет остаток от деления на этот полином 16-ти известных полиномов и проверяет, что получился полином степени 1 с соответствующим корнем. Отреверсив, мы можем взять известные полиномы вычесть `x - root` и посчитать наибольшие общий делитель получившихся полиномов. (`poly = (x - root) mod(flag_poly) <=> poly = (x - root) + some_poly * flag_poly`)

## Writeup (en)

We are given an executable which checks for flag correctness in the following way: it trivially converts hex string to bytes to polynomial, then computes the remainder of 16 known polynomials modulo this polynomial and checks that the result is a polynomial of degree 1 with a matching root. Having reverse engineered the binary, we can simply take the known polynomials, subtract `x - root` and compute their greatest common diviser. (`poly = (x - root) mod(flag_poly) <=> poly = (x - root) + some_poly * flag_poly`)

[Exploit](solve/solve.py)

## Flag

ctfcup{a8cb45262f5e8db8cd3f4260dce899154097f7e31ed440b4600470baef799d01}
