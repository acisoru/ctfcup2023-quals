# ppc | Floating in Delirium

## Information

Летая на орбите над Metra Veehkim, вы находите себя в странном месте, средь чисел и арифметических операций.

Floating in orbit above Metra Veehkim, you find yourself in a strange place amongst numbers and arithmetic operations.

## Deploy

```sh
cd deploy
docker compose -p delirium up --build -d
```

## Public

Provide python file: [public/delirium.py](public/delirium.py).

## TLDR

We have to make a function emulating xor with 42 only using arithmetic operations (+, -, *, /).

## Writeup (ru)

Нам необходимо предоставить функцию `f(a)`, которая равна `g(a) = a ^ 42`, используя лишь арифметические операции. Поскольку мы можем создать константу с плавующей точкой, мы можем превратить любое число в число с плавующей точке, мы можем использовать ошибки округления:
```python
for i in range(1, 256):
    assert 2.0 ** 61 + i == 2.0 ** 61
    assert 2.0 ** 61 + (256 + i) == 2.0 ** 61 + 257
```
Это позволяет нам превратить любое число в булеву переменную. Мы называем это `convert_to_boolean(a)`. `if_n(n) = convert_to_boolean(a - n) - convert_to_boolean(a - n - 1)` вырнет `1` для `a == n` и `0` для всего остального. Таким образом `if_n(i) * v[i] for i in range(256)` это произвольная функция в `Z256`.

## Writeup (en)

We have to make a function emulating xor with 42 only using arithmetic operations (+, -, *, /). Since we can use a floating point constant, we can convert any number to a floating point number, this we will make use of floating point rounding errors:
```python
for i in range(1, 256):
    assert 2.0 ** 61 + i == 2.0 ** 61
    assert 2.0 ** 61 + (256 + i) == 2.0 ** 61 + 257
```
This allows us to effectively cast any number to a boolean. We can further make use of this by casting `a - n`, `a - n - 1` and subtracting them, allowing us to return `1` for `a` and `0` for everything else. We call this `if_n(n)`. `if_n(n) * v` will return v for `n` and `0` for everything else. Thus a sum of `if_n(i) * v[i] for i in range(256)` is an arbitrary function in `Z256`.

[Exploit](solve/solve.py)

## Domain

ella-enchanted-afb698a2b374a968.ctfcup.ru

## Cloudflare

No

## Flag

ctfcup{fdb70d58efd1fa3c38a10e0a76369a17}
