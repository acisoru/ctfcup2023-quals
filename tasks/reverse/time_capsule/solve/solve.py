import struct

ROTATE_BY = [
        7, 9, 13, 10, 15, 8, 5, 8, 9, 22, 20, 15, 5, 21, 6, 14, 11, 5, 9, 9,
        18, 19, 22, 18, 7, 22, 18, 21, 20, 16, 18, 20, 11, 16, 14, 15, 18, 22,
        17, 9, 14, 6, 15, 18, 12, 8, 7, 20, 14, 8, 14, 6, 8, 10, 16, 18, 5, 15,
        10, 6, 22, 5, 14, 21
        ]

CONSTANTS = [
        2320580733, 1787337053, 4251985396, 2807377974, 1218319809, 4123899979,
        3237985526, 624917886, 3913274677, 3603784776, 19008228, 3624325155,
        3897454249, 587281880, 3262834740, 4113116148, 1181817537, 2836038666,
        4246454000, 1752699109, 2352479259, 4294799046, 2288500396, 1821834964,
        4257183660, 2778497332, 1254726629, 4134360714, 3212882625, 662504932,
        3928788511, 3582962050, 57023195, 3644581578, 3881328466, 549599862,
        3287428321, 4102010066, 1145222674, 2864477163, 4240589907, 1717923846,
        2384193475, 4294294311, 2256240761, 1856190139, 4262048386, 2749399002,
        1291035144, 4144497534, 3187528003, 700040073, 3943994535, 3561858610,
        95033694, 3664552458, 3864898592, 511874784, 3311764340, 4090582603,
        1108538085, 2892691235, 4234393575, 1683013989
        ]

def pad(msg):
    msg = bytearray(msg)
    msg_len_in_bits = (8 * len(msg)) & 0xffffffffffffffff
    msg.append(0x80)

    while len(msg) % 64 != 56:
        msg.append(0)

    msg += msg_len_in_bits.to_bytes(8, byteorder='little') # little endian convention
    
    return msg


INIT_BUFFER = [0x47a8925b, 0xc3efcbbd, 0x8f2ce0f5, 0xb451eaa5]

def leftRotate(x, amount):
    x &= 0xFFFFFFFF
    return (x << amount | x >> (32-amount)) & 0xFFFFFFFF



def myhash(msg):
    msg = pad(msg)
    # print(msg)

    buffer = INIT_BUFFER[:]
    
    for offset in range(0, len(msg), 64):
        A, B, C, D = buffer
        block = msg[offset : offset+64]
        for i in range(64):
        # for i in range(17):
            if i < 16:
                F = (C & B) | (~C & D)
                index = i

            elif i >= 16 and i < 32:
                F = (D & B) | (~D & C)
                index = (5 * i + 7) % 16

            elif i >= 32 and i < 48:
                F = B ^ C ^ D
                index = (3 * i + 5) % 16
            
            elif i >= 48 and i < 64:
                F = B ^ (C | ~D)
                index = (7 * i) % 16

            to_rotate = A + F + CONSTANTS[i] + int.from_bytes(block[4 * index : 4 * index + 4], byteorder='little')

            newB = (B + leftRotate(to_rotate, ROTATE_BY[i])) & 0xFFFFFFFF
                
            A, B, C, D = D, newB, B, C

        for i, val in enumerate([A, B, C, D]):
            buffer[i] += val
            buffer[i] &= 0xFFFFFFFF

    
    return struct.pack("<4I", *buffer)



if __name__ == '__main__':
    with open("flag.txt.enc", 'rb') as f:
        data = f.read()

    assert len(data) % 32 == 0

    flag = bytearray()

    for i in range(0, len(data), 32):
        salt = data[i:i + 16]
        target = data[i + 16:i + 32]
        for c in range(256):
            if myhash(salt + bytes([c])) == target:
                flag.append(c)
                break
    print(flag)
