import mmh3

def mix(a):
    a ^= (a >> 33)
    a *= 0xff51afd7ed558ccd
    a %= 2**64
    a ^= (a >> 33)
    a *= 0xc4ceb9fe1a85ec53
    a %= 2**64
    a ^= (a >> 33)
    return a
def unmix(a):
    a ^= (a >> 33)
    a *= pow(0xc4ceb9fe1a85ec53, -1, 2**64)
    a %= 2**64
    a ^= (a >> 33)
    a *= pow(0xff51afd7ed558ccd, -1, 2**64)
    a %= 2**64
    a ^= (a >> 33)
    return a
assert unmix(mix(133713371337)) == 133713371337
def rotr(a, b):
    return ((a >> b) | (a << (64-b))) % 2**64
h1 = 0
h2 = 0

h2 = (h2 - h1) % 2**64
h1 = (h1 - h2) % 2**64
h2 = unmix(h2)
h1 = unmix(h1)
h2 = (h2 - h1) % 2**64
h1 = (h1 - h2) % 2**64

h2 ^= 16
h1 ^= 16

h2 = ((h2 - 0x38495ab5) * pow(5, -1, 2**64) - h1) % 2**64
h2 = rotr(h2, 31)
k2t = h2
h2 = 0
h1 = ((h1 - 0x52dce729) * pow(5, -1, 2**64) - h2) % 2**64
h1 = rotr(h1, 27)
k1t = h1

c1 = 0x87c37b91114253d5
c2 = 0x4cf5ad432745937f

k2t *= pow(c1, -1, 2**64)
k2t %= 2**64
k2t = rotr(k2t, 33)
k2t *= pow(c2, -1, 2**64)
k2t %= 2**64

k1t *= pow(c2, -1, 2**64)
k1t %= 2**64
k1t = rotr(k1t, 31)
k1t *= pow(c1, -1, 2**64)
k1t %= 2**64

a = k1t.to_bytes(8,'little') + k2t.to_bytes(8, 'little')
print(a)
print(a.hex())
print([hex(x) for x in mmh3.hash64(a, 0, signed=False)])
