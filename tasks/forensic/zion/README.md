# for | zion

## Information

> Мы заметили странную активность на нашем сервере. Ходят слухи, что арбалеты сибири запускают на нем эксплойты, но они случайно оставили там свои секретные данные. Мы сняли дамп памяти процесса word.exe и записали траффик. Разберитесь с этим, мы рассчитываем на вас.

## Public

Provide zip file: [zion.zip](./zion.zip).

## TLDR

Use strings to find plaintext flag in core dump.

## Writeup (ru)

Нам сказано о каком-то вирусе, содержащем интересную информацию, и даны его [core dump](https://ru.wikipedia.org/wiki/Дамп_памяти) и запись траффика с сервера в формате pcap.

Это задание более простое из двух, тут флаг лежит просто в памяти вируса, и соответственно попал в core dump. Достаточно найти его там. Несколько возможных решений:

1) `strings core.1315 | grep ctfcup`
2) Открыть файл в вашем любимом текстовом редакторе, подождает пока он переварит файл на 2 гигабайта и сделать ctrl+f по ctfcup.
3) Любой другой способ найти строку в файле.

Для более подробного описания происходящего в задании рекомендуется посмотреть райтап на `zion-revenge`.

## Writeup (en)

We are told about a certain virus containing interesting information, and we are given its [core dump](https://en.wikipedia.org/wiki/Core_dump) and a pcap-format server traffic record.

This task is the easier of the two, as the flag is simply in the virus's memory and therefore ended up in the core dump. It is enough to find it there. Here are several possible solutions:

1) `strings core.1315 | grep ctfcup`
2) Open the file in your favorite text editor, wait for it to process a 2-gigabyte file, and perform a Ctrl+F search for ctfcup.
3) Any other method to find a string in a file.

For better understanding of this task and what was going on I recommend to read `zion-revenge` writeup.

## Flag

Изначально это задание предполагалось сложным, но по ошибке флаг оказался лежать просто строкой в дампе памяти. Поэтому флаг отсылает нас к TLS, что служит небольшой подсказкой к `zion-revenge`
`ctfcup{yOu_WerE_the_0ne_f0r_tls_nEo}`
