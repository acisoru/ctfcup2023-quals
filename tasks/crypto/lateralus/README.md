# crp | lateralus

## Information

С нами вошел в контакт один из ученых "Арбалетов Сибири", он утверждает, что не согласен с методами корпорации, желает помочь и направляет вам секретный проэкт. Однако открыв его, единственное, что вы обнаруживаете - какието бессмысленные заметки про числа Фибоначчи и этот файл.

You were contacted by one of the scientists of "Arbalest of Siberia", he says he does not agree with the methods of the corporation, wants to help and forwards you some secret project. However having opened it, all you find is some incomprehensible ramblings about Fibonacci numbers and this file.

## Public

Provide python script file: [public/lateralus.py](public/lateralus.py).

## TLDR

Given nth Fibonacci number modulo `p ^ 2` (where `p` is prime) find `n`.

## Writeup (ru)

Имея н-нное число Фибоначчи под модулю `p ^ 2` (где `p` - простое) найти `n`.

Имея формулу н-нного числа Фибоначчи через золотое сечение, поскольку, `(phi ^ n + psi ^ n) ^ 2 == phi ^ 2n + psi ^ 2n + 2`, получаем и решаем систему уравнений для `phi ^ n` и `psi ^ n`, потом находим дискретный логарифм по модулю `p`, используя принцип криптосистемы Пэйе.

## Writeup (en)

Given nth Fibonacci number modulo `p ^ 2` (where `p` is prime) find `n`.

Using the Fibonacci number through golden rasio formula, since `(phi ^ n + psi ^ n) ^ 2 == phi ^ 2n + psi ^ 2n + 2`, we can get a system of equations for `phi ^ n` and `psi ^ n`, solve it, then find the discrete logarithm modulo `p` using the Paillier cryptosystem trick.

[Exploit](solve/solve.py)

## Flag

ctfcup{0v3rthInk1nG_ov3r4nal1ziNg}
