# ppc | slons

## Information

> Арбалеты Сибири создали лотерею, где зарабатывают огомные деньги. Можно ли ее взломать ?
> 
> `http://slons-afb69872b377a978.ctfcup-2023.ru`

## Deploy

```sh
cd deploy
docker compose -p ella_enchanted up --build -d
```

## Public

No

## TLDR

Just bruteforce)

## Writeup (ru)

В таске нам дан сайт с одной статической html страницей. Если открыть ее код, то мы увидим, что есть две API ручки - `/generate-task` и `/check-task`.

`/generate-task` возвращает `json` из трех чисел `n`, `e` и `c`. По этим числам и названию сайта `RSA Challange` видим, что это алгоритм шифрования [RSA](https://en.wikipedia.org/wiki/RSA_(cryptosystem)), и нам надо расшифровать зашифрованное сообщение.

Однако не зная публичный ключ, это сделать сложно.

После внимательного изучения сайта видим, что там есть [cookie](https://en.wikipedia.org/wiki/HTTP_cookie) с именем `session` и каким-то [base64](https://en.wikipedia.org/wiki/Base64) в значении.

Расшифровав этот base64 любым удобным вам способом, видим, что там `json`, в котором есть поля `n`, `e`, и `c`, которые мы уже видели, и поле `key`, содержащий почему-то приватный ключ в формате PEM.

Загружаем приватный ключ, и пытаемся расшифровать сообщение. Внезапно видим, что c > n, что ломает большинство библиотек питона.

Дальше есть два пути. Либо взять библиотеку node-rsa, которая умеет такое расшифровывать (как в [solve.js](./solve/solve.js)), либо расшифровывать руками. RSA обладает ограничением - может шифровать сообщения размером не больше `n`. Чтобы его обойти, обычно разбивают сообщение на блоки длины меньше `n`, и шифруют блоки независимо, при этом делая их настолько большими, насколько возможно. Максимальный размер блока, который гарантированно меньше `n`, равен `n // 8` байт. Значит, именно на блоки такого размера нам надо разбить и отдельно расшифровать каждый блок. Реализацию такого алгоритма можно найти в [solve.py](./solve/solve.py). Подробнее про такое разбиение на блоки можно прочитать в [RFC](https://datatracker.ietf.org/doc/html/rfc3447).

Расшифровываем, видим строчку `I placed (тут какое-то число) slons or no`. Догадываемся, что раз поле в html для числового ввода (хотя и принимает в том числе текст), то надо ввести только это самое число. Отправляем его, радуемся... И не получаем флаг.

Смотрим на сам запрос браузера в developer tools -> network, и видим, что `/check-task` вернул json с ключом `answered`.

Догадываемся, что надо ответить много раз. Пишем скрипт, запускаем, идем пить кофе, возвращаемся, он решил уже 10 тысяч раз, но флага нет. Грустим, думаем дальше. От безысходности начинаем логгировать абсолютно все ответы в файл, перезапускаем скрипт и снова идем пить кофе.

Возвращаемся и видим, что в логах после правильного ответа под номером [1337](https://en.wikipedia.org/wiki/Leet) нам прилетел флаг. Очевидно, потому что это "хакерское" число. Сдерживаемся, чтобы не убить автора, и сдаем флаг.

Так же можно было заметить, что в этом таске числа не очень большие: порядка тысячи. И можно не расшифровывать сообщения приватным ключом, а первый раз факторизовать `n` - 512 бит факторизовать долго, но возможно, хоть и [дорого](https://crypto.stackexchange.com/questions/55728/factoring-a-512-bit-number), заметить этот факт, и расшифровывать сообщения [перебором по сообщению](https://crypto.stackexchange.com/questions/58147/attack-rsa-knowing-the-public-key-and-brute-forcing-all-possible-message)

## Writeup (en)

In the task we are given a site with one static html page. If we open its code, we see that there are two API routes, `/generate-task` and `/check-task`.

`/generate-task` returns a `json` of three numbers `n`, `e` and `c`. By these numbers and the site name `RSA Challange` we see that this is the [RSA](https://en.wikipedia.org/wiki/RSA_(cryptosystem)) algorithm, and we need to decrypt the encrypted message.

However, without knowing the public key, this is difficult to do.

After a careful study of the site we see that there is a [cookie](https://en.wikipedia.org/wiki/HTTP_cookie) with the name `session` and some [base64](https://en.wikipedia.org/wiki/Base64) in the value.

After decoding this base64 we can see that there is `json`, which contains fields `n`, `e`, and `c`, which we have already seen, ans also for some reason the field `key`, containing for some reason a private key in PEM format.

We can load the private key and try to decrypt the message. Suddenly we see that c > n, which breaks most python libraries.

Then there are two ways. Either take the node-rsa library, which can decrypt such messages (as in [solve.js](./solve/solve.js), or decrypt them by hand. RSA has a limitation - it can encrypt messages of size no larger than `n`. To get around this, it is common to break the message into blocks of length less than `n`, and encrypt the blocks independently, while making them as large as possible. The maximum block size that is guaranteed to be smaller than `n` is `n // 8` bytes. So it is into blocks of this size that we need to split, and decrypt each block separately. The implementation of such an algorithm can be found in [solve.py](./solve/solve.py). You can read more about such block splitting in [RFC](https://datatracker.ietf.org/doc/html/rfc3447).

Decode it, see the line `I placed (some number here) slons or no`, guess that since the field in html is counter (although it accepts text as well), we need to enter only this very number, send it.... And we didn't get the flag.

If we look at the browser request itself in developer tools -> network, we can see that `/check-task` has returned a json with the `answered` key.

Probably we have to answer multiple times. Write a script, run it, go for a coffee, come back, and see that it has solved it 10 thousand times, but there is no flag. Out of desperation we start logging absolutely all server responces, restart the script and go for coffee again.

When we come back and [grep](https://en.wikipedia.org/wiki/Grep) the logs wi can see the flag after the answer number [1337](https://en.wikipedia.org/wiki/Leet). Obviously because it's a "ahcking" number. We hold back not to kill the author and submit the flag.

Also you could notice that in this task the numbers are not very large, about a thousand. And it is possible not to decrypt messages with private key, but to factorize `n` for the first time - 512 bits factorize long, but it is possible, though [expensive](https://crypto.stackexchange.com/questions/55728/factoring-a-512-bit-number), notice this fact, and decrypt messages [brute force by message](https://crypto.stackexchange.com/questions/58147/attack-rsa-knowing-the-public-key-and-brute-forcing-all-possible-message).


## Domain

slons-afb69872b377a978.ctfcup-2023.ru

## Cloudflare

No

## Flag

ctfcup{a51c8cc4d131a6cbe54bfce654fa9c81}
