P = 156210697680525395807405913022225672867518230561026244167727827986872503969390713836672476231008571999805186039701198600755110769232069683662242528076520947841356681828813963095451798586327341737928960287475043247361498716148634925701665205679014796308116597863844787884835055529773239054412184291949429135511
N = P ** 2

def matmul(a: [[int]], b: [[int]]) -> [[int]]:
    assert len(a[0]) == len(a)

    c = [[0 for _ in range(len(b))] for _ in range(len(a))]

    for i in range(len(a)):
       for j in range(len(b[0])):
           for k in range(len(b)):
               c[i][j] = (c[i][j] + a[i][k] * b[k][j]) % N
    return c

def matrix_power(matrix: [[int]], power: int) -> [[int]]:
    res = [[int(i==j) for j in range(len(matrix))] for i in range(len(matrix))]

    while power:
        if power % 2:
            res = matmul(res, matrix)
        matrix = matmul(matrix, matrix)
        power //= 2
    return res

def nth_fib(n: int) -> int:
    matrix = [
            [0, 1],
            [1, 1]
            ]
    raised_matrix = matrix_power(matrix, n)
    return raised_matrix[1][0]

flag = int.from_bytes(input().strip().encode(), 'little')

print(nth_fib(flag))
# 15477909172279860560622805707406217756250478673314611655840405743858980683392022342467809548764734054323031819010395656403246118535553867565875529893902339904411654872234079089025389217047315043742323624821325917308574274385496531723065371644223007412030165992557420163545222156437007684169938359779378653221329688732057703769210888770960644372970750070465255394124057209414537291076794387746252353879216652821911990265852616544784564245679212863106429689471992159063656310222224709201046632676748173385980039034775452366076517092180852462127642556852734790654296149969382967256182904938778688315180408393824554619267