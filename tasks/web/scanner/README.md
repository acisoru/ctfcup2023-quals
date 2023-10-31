# web | scanner

## Information

> Арбалеты Сибири сделали передовой продукт для сканирования того, чем стал интернет. Если ничего не предпринять они
> монополизируют и этот рынок. Мы должны их остановить. 
>
> `Arbalety Sibiri' just released an advanced product for scanning what the internet has become. If we don't react they will monopolize this market as well. We have to stop them now.

## Deploy

Need whale deployment.

Image: `cr.yandex/crp56e8fvolm1rqugnkf/web-scanner:latest`
Port: `5000`

Compose(local) deploy:

```sh
cd deploy
docker compose -p web-scanner up --build -d
```

## Public

Provide zip file: [public/web-scanner.zip](public/web-scanner.zip).

## TLDR

SSRF with CRLF Injection -> Redis write -> Celery RCE.

## Writeup (ru)

Перед нами веб-сервис, который позволяет отправить HTTP-запрос на заданный URL и сохранить ответ.
Мы полностью контролируем URL, можем указывать заголовки и HTTP-версию для запроса.

Сервис использует [celery](https://docs.celeryq.dev/en/stable/) для того, чтобы асинхронно выполнять задачи отправке
HTTP-запросов.

Для решения также важны следующие факты:

1. Сервис использует библиотеку [aiohttp](https://docs.aiohttp.org/en/stable/index.html) для отправки HTTP-запросов.
2. Redis, Celery и сервер находятся в одном контейнере.
3. Celery использует redis как бэкенд для очередей и результатов.
4. В приложении описан класс исключения `InvalidHostException`, который содержит shell-injection. Но в самом
   приложении аргументы для конструктора этого исключения всегда экранируются.

Решение основано на [CVE-2021-23727](https://github.com/advisories/GHSA-q4xr-rc97-m4xx).

При десериализации ошибки Celery создаст объект исключения с параметрами, сохраненными в бэкенде (в нашем случае Redis).

Это означает, что если мы сможем положить в Redis сериализацию `InvalidHostException` с shell-инъекцией в параметре как
результат задачи, то при получении результата этой задачи Celery создаст исключение напрямую и мы получим RCE.

Для записи в Redis мы можем использовать SSRF. Протокол HTTP - текстовый, а значит что если мы
запросим http://localhost:6379, то Redis будет пытаться исполнять сырой HTTP-запрос как команды.

Однако внутри Redis'а
есть [защита](https://github.com/redis/redis/blob/2cf50ddbad1b8169ed31c913d6e6c860e4736f80/src/networking.c#L3637),
которая игнорирует команды в запросе после получения `Host:`.

Если мы сможем вставить команду до заголовка Host, она будет исполнена Redis.

Здесь нам
поможет [ошибка в библиотеке aiohttp](https://github.com/aio-libs/aiohttp/blob/317bf95d4cbac42b178972d7a00599399a2d55c7/aiohttp/client_reqrep.py#L318C9-L318C23)
. Если передать в функцию список строк, то их значения не будут провалидированы
и [значения будут поставленны как есть](https://github.com/aio-libs/aiohttp/blob/317bf95d4cbac42b178972d7a00599399a2d55c7/aiohttp/client_reqrep.py#L627C24-L627C50)
.

Если в значениях списка будет "\r\n", то мы получим CRLF инъекцию и сможем записать текст до заголовка Host и выполнить
любую команду в Redis.

Решение:

1. Подготовить JSON-представление исключения с RCE.
1. Отправить запрос на Scan, указать version как массив c `\r\n` в одном из значений, после `\r\n` должно
   идти `SET celery-task-meta-<uid> <json>`.
1. Подождать пока запрос будет обработан Celery.
1. Сходить на результат `uid`, что приведет к десериализации и RCE.

[Эксплойт](solve/sploit.py)

## Writeup (en)

We have a web service that allows us to send an HTTP request to a given URL and save the response.
We have full control over the URL, and can specify headers and HTTP version for the request.

Service uses [celery](https://docs.celeryq.dev/en/stable/) in order to asynchronously perform the task of sending the
HTTP requests.

The following facts are also important for the solution:

1. The service uses the [aiohttp](https://docs.aiohttp.org/en/stable/index.html) library to send HTTP requests.
2. Redis, Celery and the server are running in the same container.
3. Celery uses redis as a backend for queues and results.
4. There is an `InvalidHostException` exception class that contains a shell-injection. But in the
   application, arguments to the constructor of this exception are always sanitized.

The solution idea is based on [CVE-2021-23727](https://github.com/advisories/GHSA-q4xr-rc97-m4xx).

When deserializing an error, Celery will create an exception object with parameters stored in the backend (in our case
Redis).

This means that if we can put a serialized `InvalidHostException` to Redis with shell injection in the parameter as
the result of a task, then when we will get the result of that task Celery will create an exception directly, and we
will get an RCE.

To write to Redis, we can use SSRF. The HTTP protocol is text-based, which means that if we will fire
request to the http://localhost:6379, Redis will try to execute the raw HTTP request as commands.

However, inside Redis.
there's
a [protection](https://github.com/redis/redis/blob/2cf50ddbad1b8169ed31c913d6e6c860e4736f80/src/networking.c#L3637)
which ignores commands in the request after `Host:` is received.

But if we can insert a command before the Host header, it will be executed by Redis.

A [bug in aiohttp library](https://github.com/aio-libs/aiohttp/blob/317bf95d4cbac42b178972d7a00599399a2d55c7/aiohttp/client_reqrep.py#L318C9-L318C23)
will help us. If we pass a list of strings to the function, their values will not be validated
and [values will be sent as they are](https://github.com/aio-libs/aiohttp/blob/317bf95d4cbac42b178972d7a00599399a2d55c7/aiohttp/client_reqrep.py#L627C24-L627C50)
.

If the values of the list have "\r\n", we will get CRLF injection, and we will be able to write text before the Host
header and execute any command in Redis.

Solution:

1. Prepare a JSON representation of the exception with RCE.
2. Send a request to Scan, specify version as an array with `\r\n` in one of the values, after the `\r\n` there should
   be a `SET celery-task-meta-<uid> <json>`.
3. Wait for the request to be processed by Celery.
4. Go to the `uid` result, which will result in deserialization and RCE.

[Exploit](solve/sploit.py)

## Domain

Should be auto-generated by Whale.

## Cloudflare

No

## Flag

Should be auto-generated by Whale.
