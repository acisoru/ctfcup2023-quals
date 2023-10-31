# crypto | murdata

## Information

> Нам удалось найти один из старых сервисов "Арбалетов" для сбора персональных данных. <ДАННЫЕ_УДАЛЕНЫ> но может быть что-то уцелело?
> We were able to find one of the old "Arbalets" services for collecting personal data. <DATA_REMOVED> but maybe you fill find something?
> `murdata-138852fe54171c5c.ctfcup-2023.ru`

## Deploy

```sh
cd deploy
docker compose -p murnotes up --build -d
```

## Public

Provide zip file: [public/task.zip](public/task.zip).

## TLDR

Hash-Length Extension + MurMur3(128 bit) preimage.

## Writeup (ru)

### Авторское решение.

В задании используется murmur3 хэш для хэширования паролей. Хэш при этом сравнивается с помощью приведения строки к числу.

Важный факт, который используется при решении задания - int(murmur3('')) = 0. Т.е. пустая строка хэшируется в 0.

Пароли пользователей хранятся в Redis. При этом Redis вернет пустую строку, если мы запросим пароль для несуществующего пользователя.

`hexdec('') = 0`, как и `hexdec(murmur3('')) = 0`. Таким образом, мы можем зайти за несуществующего пользователя, если используем в качестве пароля пустую строку.

Приложение не даст использовать пустую строку как пароль, поэтому нужно будет найти другую строку, murmur3 которой будет равен 0.

Далее мы можем обойти проверку двухфакторной аутентификации, используя атаку Hash-Length-Extension. 

Итоговые шаги эксплойта:

1. C помощью HLE подписываем к своему username строку `/../admin`.
2. Пользователя с таким username не будет в Redis, а значит его пароль будет 0.
3. Передаем в качестве пароля такую строку, что ее хэш будет равен 0.
4. Получаем флаг (с помощью Path-Traversal в логине).

### Альтернативное решение.

Можно заметить, что пароль пользователя `admin` на самом деле пустой, т.к. переменная окружения объявлена после ее использования.

Второе замечание — переменная окружения `SECRET` не определена в контейнере. Таким образом нам достаточно найти такую непустую строку, что ее хэш будет равен 0.

### Writeup (en)

### Author solution.

App uses murmur3 hash to hash passwords. The hash is compared by converting a hash hex string to a number.

An important fact to note is that int(murmur3(''')) = 0. That is, an empty string is hashed to 0.

User passwords are stored in Redis. Redis will return an empty string if we request a password for a non-existent user.

`hexdec('') = 0`, just like `hexdec(murmur3(''))) = 0`. Thus, we can log in as a non-existent user if we use an empty string as the password.

The application will not let us use the empty string as a password, so we will have to find another string with murmur3 equal to 0.

Next, we can bypass the two-factor authentication check using the Hash-Length-Extension attack.

The overall steps of the exploit are:

1. Use HLE to sign & add the `/../admin` string to your username.
2. User with this username won't be present in Redis, so the redis returns an empty string.
3. Pass a string as password such that its murmur3 hash is 0.
4. Get the flag (using Path-Traversal in the username).

### Alternative solution.

You may notice that the `admin` password is actually empty, since the environment variable is declared after it is used.

The second observation is that the `SECRET` environment variable is not defined in the container. Thus, we only need to find such a non-empty string that its hash will be equal to 0.


## Domain

murdata-138852fe54171c5c.ctfcup-2023.ru


## Cloudflare

Yes

## Flag

ctfcup{3fe2d4499e6d327c9d7f1e9f9f9a02aa998311c7}