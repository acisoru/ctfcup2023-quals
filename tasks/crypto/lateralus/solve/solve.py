from typing import Tuple

def cipolla(n: int, p: int) -> int:
    """
    Cipolla's algorithm for solving x ** 2 % p == n
    https://en.wikipedia.org/wiki/Cipolla%27s_algorithm
    """

    for a in range(p):
        if pow(a ** 2 - n, (p - 1) // 2, p) == p - 1:
            break
    else:
        raise ValueError("Non quadratic residue not found.")

    def cipolla_multiply(x, y):
        return (
                (x[0] * y[0] + x[1] * y[1] * (a ** 2 - n)) % p,
                (x[0] * y[1] + x[1] * y[0]) % p
                )

    x = (1, 0)
    base = (a, 1) # x = x0 + x1 * sqrt(a ** 2 - n)
    exp = (p + 1) // 2
    while exp:
        if exp % 2:
            x = cipolla_multiply(x, base)
        base = cipolla_multiply(base, base)
        exp //= 2

    assert x[1] == 0

    return x[0]

def hensel_lifting(f: int, r: int, p: int, k: int, m: int=1) -> int:
    def apply(f, x, p):
        return sum(c * pow(x, i, p) for i, c in enumerate(f)) % p

    assert m <= k
    if m <= 0:
        return r % p ** (k + m)

    fd = [c * i for i, c in enumerate(f)][1:] + [0]
    assert(apply(f, r, p ** k) == 0)
    assert(apply(fd, r, p ** k) != 0)

    return (r - apply(f, r, p ** (k + m)) *  pow(apply(fd, r, p ** m), -1, p ** m)) % p ** (k + m)


def sqrtmod(n: int, p: int, power: int=1) -> Tuple[int,]:
    """

    Square root modulo prime number using Cipolla's algorithm or know formulas.
    https://en.wikipedia.org/wiki/Quadratic_residue#Prime_or_prime_power_modulus.
    """

    if pow(n, (p - 1) // 2, p) != 1:
        return ()

    if p % 4 == 3:
        x = pow(n, (p + 1) // 4, p)
    else:
        x = cipolla(n, p)

    assert x ** 2 % p == n % p

    roots = [x, -x % p]

    power_of_2 = 0
    while 2 ** (power_of_2 + 1) < power:
        roots = [hensel_lifting(
            f=[-n, 0, 1], # f(x) = 1 * x ** 2 + 0 * x ** 1 + (-n) * x ** 0 (mod p)
            r=root,
            p=p,
            k=2**power_of_2,
            m=2**power_of_2,
            ) for root in roots]
        power_of_2 += 1
    roots = [hensel_lifting(
        f=[-n, 0, 1], # f(x) = 1 * x ** 2 + 0 * x ** 1 + (-n) * x ** 0 (mod p)
        r=root,
        p=p,
        k=2**power_of_2,
        m=power - 2**power_of_2,
        ) for root in roots]


    return tuple(roots)

def main():
    P = 156210697680525395807405913022225672867518230561026244167727827986872503969390713836672476231008571999805186039701198600755110769232069683662242528076520947841356681828813963095451798586327341737928960287475043247361498716148634925701665205679014796308116597863844787884835055529773239054412184291949429135511
    N = P ** 2

    output = 15477909172279860560622805707406217756250478673314611655840405743858980683392022342467809548764734054323031819010395656403246118535553867565875529893902339904411654872234079089025389217047315043742323624821325917308574274385496531723065371644223007412030165992557420163545222156437007684169938359779378653221329688732057703769210888770960644372970750070465255394124057209414537291076794387746252353879216652821911990265852616544784564245679212863106429689471992159063656310222224709201046632676748173385980039034775452366076517092180852462127642556852734790654296149969382967256182904938778688315180408393824554619267

    r5 = sqrtmod(5, P, power=2)[0] # sqrt(5) (mod N)

    i2 = pow(2, -1, N) # 1/2 (mod N)

    phi = (1 + r5) * i2 % N # phi = (1 + sqrt(5)) / 2
    psi = (1 - r5) * i2 % N # psi = (1 - sqrt(5)) / 2

    # (phi ** n - psi ** n) / sqrt(5) == output (mod N)
    # phi ** n - psi ** n == output * sqrt(5) (mod N)
    # c = output * sqrt(5) (mod N)
    c = output * r5 % N

    # phi ** n == c + psi ** n (mod N)
    # phi * psi == (1 + sqrt(5)) / 2 * (1 - sqrt(5)) / 2 == (1 - 5) / 4 == -1 (mod N)
    # d = phi * psi mod N in {-1, 1}
    # c ** 2 == (phi ** n - psi ** n) ** 2 == phi ** 2n + psi ** 2n - 2 * (phi * psi) ** n (mod N)
    # phi ** n == psi ** n + c (mod N)
    # (psi ** n + c) ** 2 + psi ** 2n - 2 * d - c ** 2 == 0 (mod N)
    # 2 * psi ** 2n + 2 * c * psi ** n - 2 * d == 0 (mod N)
    # psi ** 2n + c * psi ** n - d == 0 (mod N)

    for d in [-1, 1]:
        D = (c ** 2 + 4 * d) % N
        D_sqrt_root = sqrtmod(D, P, power=2)[0]
        assert D_sqrt_root ** 2 % N == D

        for psin in [(-c + k * D_sqrt_root) * i2 % N for k in [-1, 1]]:
            # phi ** n (mod N)
            # https://en.wikipedia.org/wiki/Paillier_cryptosystem
            # using some facts outlined in the underlying paper (phi as a function means euler's function)
            # say
            # b == (P + 1) ** a == 1 + a * P + C(a, 2) * P ** 2 + ... == 1 + a * P (mod N == P ** 2)
            # a == (b - 1) / P (mod N)
            # 
            # any number x can be made of form (P + 1) ** a by raising it to the power (P - 1)
            # and the underlying power would not change modulo phi(N) // (P - 1) == P
            # ((x ** (p - 1) mod N) - 1) / p == log(x, P - 1) (mod P)

            psi_log = (pow(psi, P - 1, N) - 1) // P
            psin_log = (pow(psin, P - 1, N) - 1) // P
            n = psin_log * pow(psi_log, -1, P) % P
            print(n.to_bytes((n.bit_length() + 7) // 8, 'little'))

if __name__ == "__main__":
    main()
