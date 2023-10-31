# pwn | some_storage

## Information

> Мы перехватили трафик из штаба "Арбалетов", и все, что удалось выявить — только этот адрес. Проверь, может, найдешь там что-то интересное.
>
> We intercepted traffic from the headquarters of "Arbalety", and all we were able to identify was this address. Check it out, maybe you'll find something interesting there.
> 
> nc 0 13002

## Deploy

```sh
cd deploy/
docker compose -p some_storage up --build -d
```

## Public

Provide zip file [public/some_storage.zip](./public/some_storage.zip)

## TLDR

Overflow in `User.name[]`, corrupt `TaskStorage` to rewrite `User.vtable` to shellcode

## Writeup (ru)

При смене имени мы можем прочитать 0x20 байт вместо 20. Это позволет нам переписать указатель `User->tasks.free_list`, который идет после `User->name`. Но при этом к концу нашего ввода всегда добавляется `\0`, поэтому, не зная никаких адресов, получится переписать только младший байт.

Таски хранятся в виде односвязного списка, с указателями на адрес следующей структуры и адрес, по которому пишется текст данного таска (список хранится на куче, текст тасков хранится в памяти, выделенной через mmap):
```cpp
struct list {
    list *next;
    char *cur;
};
```

Если мы перепишем `free_list`, при следующем создании таска в качестве указателя `->cur` нам вернется что-то другое, и возможно мы сможем перезаписать что-то еще.
Если мы попробуем перезаписать по адресу `free_list` другого юзера, получится следующее:
```
+0140 0x556f07740ba0  a8 cc 3b 07 6f 55 00 00  75 73 65 72 00 00 00 00  │..;.oU..│user....│ <- 1й юзер
+0150 0x556f07740bb0  35 35 35 35 35 35 35 35  35 35 35 35 35 35 35 35  │55555555│55555555│
+0160 0x556f07740bc0  35 35 35 35 35 35 35 35  00 0c 74 07 6f 55 00 00  │55555555│..t.oU..│ <- Переписанный `free_list`
+0170 0x556f07740bd0  10 0d 74 07 6f 55 00 00  00 90 fa 5d f7 7f 00 00  │..t.oU..│...]....│ <- `used_list` и `mem`
+0180 0x556f07740be0  a8 cc 3b 07 6f 55 00 00  75 73 65 72 00 00 00 00  │..;.oU..│user....│ <- 2й юзер
+0190 0x556f07740bf0  36 36 36 36 36 36 36 36  36 36 36 36 36 36 36 36  │66666666│66666666│
+01a0 0x556f07740c00  00 00 00 00 00 00 00 00  90 0e 74 07 6f 55 00 00  │........│..t.oU..│ <- `free_list`
+01b0 0x556f07740c10  00 00 00 00 00 00 00 00  00 80 fa 5d f7 7f 00 00  │........│...]....│ <- `used_list` и `mem`
...
+0420 0x556f07740e80  00 00 00 00 00 00 00 00  21 00 00 00 00 00 00 00  │........│!.......│
+0430 0x556f07740e90  70 0e 74 07 6f 55 00 00  00 81 fa 5d f7 7f 00 00  │p.t.oU..│...]....│ <- `next` и `cur`
+0440 0x556f07740ea0  00 00 00 00 00 00 00 00  21 00 00 00 00 00 00 00  │........│!.......│
```
1. Мы переписали `free_list` 1го юзера
2. Создаем новый таск для 1го юзера
   1. В качестве `->cur` возвращается `free_list` 2го юзера, мы что-то туда пишем (в данном примере пишем по адресу 0x556f07740e90)
   2. Дальше в `->next` положится текущий указатель `used_list` 1го юзера (т.к. таск добавляется в начало `used_list`). То есть по адресу 0x556f07740c00 теперь будет лежать 0x0000556f07740d10
3. Теперь можно ликнуть адрес кучи, вывев имена всех пользователей

Теперь можно переписать `free_list` другого юзера на vtable, создать этому юзеру таск и переписать vtable на адрес кучи, по которому лежит адрес из mmap, и выполнить шеллкод

[Exploit](./solve/sploit.py)

## Writeup (en)

There's overflow in `User.name[]`, so we can rewrite `User->task.free_list`. But we have no leaks, and our input ends with null byte, so we can only put `\0` in `free_list`.

Tasks are stored in a list with a pointer to next `list` structure and a pointer to address from mmap, where we write task text.
```cpp
struct list {
    list *next;
    char *cur;
};
```

If we rewrite `free_list`, we will get as `->cur` something else and probably we would be able to rewrite something else.
If we try to rewrite `free_list` and create new task, we will get the following:
```
+0140 0x556f07740ba0  a8 cc 3b 07 6f 55 00 00  75 73 65 72 00 00 00 00  │..;.oU..│user....│ <- 1st user
+0150 0x556f07740bb0  35 35 35 35 35 35 35 35  35 35 35 35 35 35 35 35  │55555555│55555555│
+0160 0x556f07740bc0  35 35 35 35 35 35 35 35  00 0c 74 07 6f 55 00 00  │55555555│..t.oU..│ <- rewritten `free_list`
+0170 0x556f07740bd0  10 0d 74 07 6f 55 00 00  00 90 fa 5d f7 7f 00 00  │..t.oU..│...]....│ <- `used_list` and `mem`
+0180 0x556f07740be0  a8 cc 3b 07 6f 55 00 00  75 73 65 72 00 00 00 00  │..;.oU..│user....│ <- 2nd user
+0190 0x556f07740bf0  36 36 36 36 36 36 36 36  36 36 36 36 36 36 36 36  │66666666│66666666│
+01a0 0x556f07740c00  00 00 00 00 00 00 00 00  90 0e 74 07 6f 55 00 00  │........│..t.oU..│ <- `free_list`
+01b0 0x556f07740c10  00 00 00 00 00 00 00 00  00 80 fa 5d f7 7f 00 00  │........│...]....│ <- `used_list` and `mem`
...
+0420 0x556f07740e80  00 00 00 00 00 00 00 00  21 00 00 00 00 00 00 00  │........│!.......│
+0430 0x556f07740e90  70 0e 74 07 6f 55 00 00  00 81 fa 5d f7 7f 00 00  │p.t.oU..│...]....│ <- `next` and `cur`
+0440 0x556f07740ea0  00 00 00 00 00 00 00 00  21 00 00 00 00 00 00 00  │........│!.......│
```
1. Rewrite `free_list` of 1st user
2. Create new task for 1st user
   1. Get `free_list` as a `->cur` pointer, write something (here we write to 0x556f07740e90)
   2. Next, because of tasks are added to the beginning of `used_list`, we put current `used_list` value to `->next` of new task. So at 0x556f07740c00 now will be 0x0000556f07740d10.
3. Now we can leak heap address by listing all users

Finally we need to rewrite some `free_list` to vtable, create task for this user and rewrite vtable to execute shellcode from mmaped task

[Exploit](./solve/sploit.py)