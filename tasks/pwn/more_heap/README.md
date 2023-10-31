# pwn | more_heap

## Information

> Мой агент передал бумажку с каким-то цифрами и больше не выходил на связь. Надеюсь его не схватили Арбалеты, но что делать с бумажкой я так и не понял. Разберись, а о награде договоримся.
>
> My agent handed over a piece of paper with some numbers and never contacted me again. I hope the Arbalety didn’t grab him, but I still don’t understand what to do with the piece of paper. Figure it out, and we'll agree on a reward.
> 
> nc 0 13001

## Deploy

```sh
cd deploy/
docker compose -p more-heap up --build -d
```

## Public

Provide zip file [public/more_heap.zip](./public/more_heap.zip)

## TLDR

- arbitrary write using 2free
- get heap, libc, stack leak
- rewrite `strchrnul` in .got to `puts`, rewrite `_IO_2_1_stdout_` to call `read(0, &stack, 0x100)` on calling `puts`, call `free` with invalid argument to call `strchrnul`
- write rop to read flag

## Writeup (ru)

Сервис с заметками, в котором можно создать заметку, прочитать ее и удалить. Заметка всегда размера 0x10 байт, также при создании заметки проверяется, что чанк выделился не на стеке и не в бинаре. Если это так, то в чанк считывается 16 байт, иначе чанк освобождается. 

1. При удалении заметки не зануляется указатель на нее, поэтому можно сначала удалить заметку, затем прочитать ее и ликнуть адрес кучи.
2. Для лика либсы можно освободить фейковый чанк большого размера (например, 0x460). Можно попытаться с помощью 2free выделить чанк так, чтобы перезаписать размер существующего чанка:
    ```
    +0000 0x55e773b97290  00 00 00 00 00 00 00 00  21 00 00 00 00 00 00 00  │........│!.......│
    +0010 0x55e773b972a0  61 61 00 00 00 00 00 00  00 00 00 00 00 00 00 00  │aa......│........│ <- 1st
    +0020 0x55e773b972b0  00 00 00 00 00 00 00 00  61 04 00 00 00 00 00 00  │........│a.......│ <- 2nd
    +0030 0x55e773b972c0  61 61 00 00 00 00 00 00  00 00 00 00 00 00 00 00  │aa......│........│ <- 3rd
    +0040 0x55e773b972d0  00 00 00 00 00 00 00 00  21 00 00 00 00 00 00 00  │........│!.......│
    ```
    Проблема в том, что когда мы будем выделять фейковый чанк (который находится на `0x55e773b972b0`), первые 8 байт будут равны 0. tcache попробует расшифровать этот адрес, и получится следующее:
    ```
    tcachebins
    0x20 [  0]: 0x55e773b97
    ```
    Из-за этого, если мы попробуем еще раз проэксплуатировать 2free, получится ошибка в тот момент, когда у нас не осталось чанков в tcache и мы попытаемся взять чанк из fastbin
    ```
    tcachebins
    0x20 [  0]: 0x55e773b97
    fastbins
    0x20: 0x55e773b972b0 —▸ 0x55e773b972d0 ◂— 0x55e773b972b0
    ```
    Чтобы избавиться от этой ошибки, можно сначала выделить чанк по адресу `heap+0x90`, где находится указатель на чанк из tcache, который вернется при следующем `malloc(0x10)`. Если записать туда 0, то 2free можно будет использовать еще раз.

    Также при следующем 2free можно будет записать по адресу `heap+0x88` 0x21, чтобы получился валидный хедер. Тогда этот чанк можно будет освобождать, и мы получим arbitrary write
    ```py
    def write(what, where):
        add(1, b'aa') ; delete(1)       # set tcache size to 1
        delete(0) ; add(0, p64(where))  # 0 is chunk at `heap+0x90`
        add(1, what)
        delete(0) ; add(0, p64(0))      # fix tcache
    ```
3. Теперь можно перезаписать размер какого-либо чанка на 0x460, освободить его и ликнуть либсу
4. Создать чанк по адресу `libc.sym['environ']-0x10` и записать 0x10 ненулевых байт. При выводе заметки выводится все до первого 0-байта, поэтому так мы ликнем адрес стека.
5. `free` проверяет, что переданный ему указатель является валидным указателем на чанк. Если это не так, вызовется `malloc_printerr` и получится следующая цепочка вызовов:
   ```
   malloc_printerr (const char *str)
     __libc_message (do_abort, "%s\n", str)
       __strchrnul
   ```
   `__strchrnul` находится в .got либсы. Мы можем его заранее переписать на что-то другое, например, на `puts`. 
6. `puts` вызовет `stdout->vtable[7]`. Предполагается, что так вызовется функция `_IO_file_xsputn`. Но мы можем переписать `stdout->vtable` так, чтобы вместо `_IO_file_xsputn` вызвался [`_IO_obstack_overflow`](https://elixir.bootlin.com/glibc/glibc-2.35/source/libio/obprintf.c#L39). Эта функция воспримет `stdout` как структуру `_IO_obstack_file`, и если [`stdout->obstack->next_free + 1 > stdout->obstack->chunk_limit`](https://elixir.bootlin.com/glibc/glibc-2.35/source/malloc/obstack.h#L317), вызовется [`_obstack_newchunk`](https://elixir.bootlin.com/glibc/glibc-2.35/source/malloc/obstack.c#L245). `_obstack_newchunk` проверит, что [`stdout->obstack->use_extra_arg != 0`](https://elixir.bootlin.com/glibc/glibc-2.35/source/malloc/obstack.c#L121), и если это так, вызовет `stdout->obstack->chunkfun(stdout->obstack->extra_arg, stdout->obstack->chunk_size)`. При этом в rdx будет лежать `stdout->obstack->alignment_mask`, то есть, переписав `stdout->vtable` и переписав `stdout+0xe0` (по этому оффсету должен лежать указатель на `struct obstack*`) на фейковую структуру, мы сможем вызвать `read` и записать rop на стек.

[Exploit](./solve/sploit.py)

## Writeup (en)

1. We can add, show and delete note. Note size is always 0x10 bytes. Also after calling `malloc` we check that chunk hasn't been allocated on stack or on binary. If that's true, we read 0x10 bytes, otherwise we call `free`.
2. To get libc leak we can free big fake chunk (for example of size 0x460). We can try exploit 2free to create chunk which will overwrite header of another chunk:
    ```
    +0000 0x55e773b97290  00 00 00 00 00 00 00 00  21 00 00 00 00 00 00 00  │........│!.......│
    +0010 0x55e773b972a0  61 61 00 00 00 00 00 00  00 00 00 00 00 00 00 00  │aa......│........│ <- 1st
    +0020 0x55e773b972b0  00 00 00 00 00 00 00 00  61 04 00 00 00 00 00 00  │........│a.......│ <- 2nd
    +0030 0x55e773b972c0  61 61 00 00 00 00 00 00  00 00 00 00 00 00 00 00  │aa......│........│ <- 3rd
    +0040 0x55e773b972d0  00 00 00 00 00 00 00 00  21 00 00 00 00 00 00 00  │........│!.......│
    ```
    But when we will do `malloc` for fake chunk (in this example we want to allocate it at `0x55e773b972b0`), first 8 bytes will be 0. So when tcache will try to decode it as address of next chunk, it will get the following:
    ```
    tcachebins
    0x20 [  0]: 0x55e773b97
    ```
    Because of this if we try to do 2free again, we will get an error at the moment when tcache is empty and we try to get chunk from fastbin
    ```
    tcachebins
    0x20 [  0]: 0x55e773b97
    fastbins
    0x20: 0x55e773b972b0 —▸ 0x55e773b972d0 ◂— 0x55e773b972b0
    ```
    So at first we need to allocate chunk at `heap+0x90`, where tcache keeps pointer to last freed chunk of size 0x20. If we clear tcache and put here `0`, we will be able to exploit 2free again.

    Also we should put 0x21 to `heap+0x88` to get valid chunk header. After that we can call `free` on this chunk, so we can do arbitrary write.
    ```py
    def write(what, where):
        add(1, b'aa') ; delete(1)       # set tcache size to 1
        delete(0) ; add(0, p64(where))  # 0 is chunk at `heap+0x90`
        add(1, what)
        delete(0) ; add(0, p64(0))      # fix tcache
    ```
3. Now we can free fake chunk of size 0x460 and get libc leak.
4. To get stack leak we should create chunk at `libc.sym['environ']-0x10` and write some 0x10 bytes. On printing note program write to stdout everything until it gets null byte, so we will get stack leak.
5. `free` checks that passed argument is a valid pointer. It it's false, it will call `malloc_printerr` and we will get the following call chain:
    ```
   malloc_printerr (const char *str)
     __libc_message (do_abort, "%s\n", str)
       __strchrnul
    ```
    `__strchrnul` is a pointer from libc .got . We can rewrite it to something else, for example, to `puts`.
6. `puts` will call `stdout->vtable[7]`. Usually this calls `_IO_file_xsputn`. But we can overwrite `stdout->vtable` to call [`_IO_obstack_overflow`](https://elixir.bootlin.com/glibc/glibc-2.35/source/libio/obprintf.c#L39) instead of `_IO_file_xsputn`. This function will interpret `stdout` as `struct _IO_obstack_file` and call [`_obstack_newchunk`](https://elixir.bootlin.com/glibc/glibc-2.35/source/malloc/obstack.c#L245) if `stdout->obstack->next_free + 1 > stdout->obstack->chunk_limit`. `_obstack_newchunk` will call `stdout->obstack->chunkfun(stdout->obstack->extra_arg, stdout->obstack->chunk_size)` if `stdout->obstack->use_extra_arg != 0`. Also we will have `stdout->obstack->alignment_mask` in rdx, so if we rewrite `stdout->vtable` and rewrite `stdout+0xe0` (this is an offset of `struct obstack*` pointer) to fake struct, we will be able to call read and write rop on stack.

[Exploit](./solve/sploit.py)