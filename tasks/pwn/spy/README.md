# pwn | spy

## Information

> Один из наших шпионов попал в руки Арбалетов! Мы успели получить от него координаты одного из серверов Megalith, но дальше связь оборвалась. Узнайте оставшуюся часть сообщения.

## Deploy

```sh
cd deploy
docker compose -p spy up --build -d
```

## Public

Provide zip file: [public/spy.zip](public/spy.zip).

## TLDR

Arbitrary write to GOT and _fini_array sections.

## Writeup (ru)

Нам дана программа с 3 вариантами на выбор:
1) Написать любые 8 байт куда угодно.
2) Прочитать флаг в буфер.
3) Вывести содержимое буфера на экран.

Мы можем выбрать только один вариант для каждого запуска программы.

Как видно из Dockerfile, программа не имеет защиты таблицы GOT, поэтому мы можем записать адрес функции `main` в `puts@got`, чтобы зациклить нашу программу. После этого мы хотим настроить цепочку для чтения флага и его вывода. Поэтому мы перезаписываем первую запись в `_fini_array` на `spy_open` и `strchrnul@got` на `spy_print`. Наконец, мы перезаписываем `puts@got` на `printf@plt`, чтобы выйти из цикла и выполнить цепочку `spy_open -> spy_print`.

## Writeup (en)

We are given program with 3 options:
1) Write any 8 bytes anywhere.
2) Read flag to buffer.
3) Write buffer contents to stdout.

We can only choose one option per program invocation.

As can be seen in Dockerfile the program doesn't have GOT table protection so we can write `main` function address to `puts@got` to loop our program.
After that we want to setup chain to read flag and output it. So we overwrite first entry in `_fini_array` to `spy_open` and `strchrnul@got` to `spy_print`. Finally we overwrite `puts@got` to `printf@plt` to exit the loop and execute chain `spy_open -> spy_print`.

[Exploit](solve/sploit.py)

