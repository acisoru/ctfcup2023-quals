# Исследование

Нам даны два файла - дамп памяти и траффика. Запуск `strings` на дамп памяти показывает, что это явно программа на go, называется `/home/ctf/word.exe` (не дайте расширению `.exe` запутать вас, это программа под linux). Так же можно заметить строки про какое-то `neo`, например `neo_exploit_queue_exploit_run_time_seconds_bucket` (что выглядит как какая-то метрика, но не гуглится). Больше ничего полезного в дампе памяти пока нет, перейдем к анализу траффика.

# Анализ траффика
Wireshark - лучший друг при работе с .pcap файлами, воспользуемся им. В самом начале мы видим незашифрованный http запрос - wget скачивает файл `termbin.com/0gdj`. В ответ прилетает bash скрипт:
```bash
#!/bin/sh

wget -q https://github.com/andser612345/data/raw/main/neo_client.elf -O word.exe

cat >word.yml <<-EOT
host: "neo.cbsctf.live:443"
metrics_host: "neo.cbsctf.live:8428/api/v1/import/prometheus"
exploit_dir: "data"
grpc_auth_key: "zeonrevenge"
use_tls: true
EOT

chmod +x word.exe
./word.exe -c word.yml run
```

Отлично, у нас есть бинарь, который запущен, и для которого дамп памяти (его можно скачать по этой же ссылке с github), и какой-то конфиг файл. Если загуглить `github neo_client use_tls`, то первая ссылка будет вести на [репозиторий](https://github.com/C4T-BuT-S4D/neo). Выглядит правдоподобно, потому что домен в конфиге cbsctf.live, и репозиторий команды C4T-BuT-S4D. Немного поизучав, можно понять, что это утилита для распределенного запуска эксплойтов на A&D соревнованиях, и сделать предположение, что либо один из эксплойтов получает флаг от другой команды, либо сам содержит в себе флаг.

При попытке подключиться к `neo.cbsctf.live` видим, что такого домена уже нет, значит надо дальше копать траффик и дамп памяти. К сожалению, некоторые ip адреса из дампа к моменту проведения CTF уже опять стали активными, и вели на левые сайты. Так получилось, потому что поднималось все в облаке, это не было запланированно.

Если посмотреть дальше на траффик, видим много tls пакетов до адресов 140.82.121.3 и 185.199.110.133. Судя по скрипту это github, и `whois 140.82.121.3` это подтверждает.

Примерно на 2774 пакете замечаем изменения - появился http траффик, и адреса изменились. http пакеты - сбор метрики с neo_runner, там ничего интересного. Остальное зашифровано tls.
Еще чуть дальше видим другие http пакеты - `POST //api/register` на адрес 84.252.131.189 и чуть позже получение флага через `GET //api/notes`, на что прилетает флаг в ructf формате. Это подтверждает гипотезу, что у нас запущена система запусков эксплойтов, но флага на наш CTF тут нет.

Весь остальной траффик зашифрован.

# Расшифровка TLS

Можно еще поизучать дампы траффика и памяти (как минимум полезно использовать на них binwalk, и рекурсивно во всех распакованных файлах поискать подстроку ctfcup), но тут это ни к чему не приведет. Остается расшифровывать TLS.

## Анализ neo_client

Можно поизучать исходники на github и убедиться, что ничего полезного или уязвимого (тем более когда сервер выключен) там нету.

Скачаем себе такой же `neo_client.elf` с гитхаба, как в задании (`wget -q https://github.com/andser612345/data/raw/main/neo_client.elf`) и попробуем определить как он был скомпилирован.
Пристальным чтением вывода `strings` можно заметить пути `/opt/homebrew/Cellar/go/1.21.3`. Это значит, что он был скомпилирован на macos (golang поддерживает кросс-компиляцию из коробки) на версии go 1.21.3
1.21.3 - последняя на момент ctf версия go, и можно пойти читать ее исходный код. Самое интересное находится в [crypto/tls/conn.go](https://go.googlesource.com/go/+/refs/tags/go1.21.3/src/crypto/tls/conn.go):
```go
type Conn struct {
    ...
	// input/output
	in, out   halfConn
	...
}

func (c *Conn) readRecordOrCCS(expectChangeCipherSpec bool) error {
    ...
    data, typ, err := c.in.decrypt(record)
    ...
}
```

То есть вся расшифровка входящего траффика происходит в структуре `halfConn`:
```go
type halfConn struct {
	sync.Mutex
	err     error  // first permanent error
	version uint16 // protocol version
	cipher  any    // cipher algorithm
	mac     hash.Hash
	seq     [8]byte // 64-bit sequence number
	scratchBuf [13]byte // to avoid allocs; interface method args escape
	nextCipher any       // next encryption state
	nextMac    hash.Hash // next MAC algorithm
	level         QUICEncryptionLevel // current QUIC encryption level
	trafficSecret []byte              // current TLS 1.3 traffic secret
}
```

Сразу видим поле `trafficSecret`. Идем смотреть как оно используется.

```go
func (hc *halfConn) setTrafficSecret(suite *cipherSuiteTLS13, level QUICEncryptionLevel, secret []byte) {
	hc.trafficSecret = secret
	hc.level = level
	key, iv := suite.trafficKey(secret)
	hc.cipher = suite.aead(key, iv)
	for i := range hc.seq {
		hc.seq[i] = 0
	}
}
```

Отлично, его достаточно чтобы узнать ключ и iv для шифра. Хотелось бы получить [sslkeylogfile](https://datatracker.ietf.org/doc/draft-thomson-tls-keylogfile/) чтобы wireshark смог автоматически расшифровать [tls](https://wiki.wireshark.org/TLS#using-the-pre-master-secret), но это сложнее, поэтому пойдем через ручную расшифровку.

Надо выяснить две вещи:
1) в какой момент он устанавливается (с какого момента траффик надо расшифровывать через него)
2) какие именно сообщения приходят в `hc.decrypt`

Это можно выяснить пристальным чтением кода и tls 1.3 спецификации, и понять, что приходят целиком tls сообщения (170303...), где 0x17 - тип сообщения (tls), 0x0303 - версия (1.3), потом идет длина и само сообщение.

С какого момента начинать расшифровывать - чуть сложнее. Проще всего - написать тестовый скрипт, который подключается по https к сайту (проверить, что используется tls 1.3!!!), и залоггировать, какой `trafficSecret` используется после какого количество данных.
Можно будет увидеть (скриншот с доказательством утерян в веках), что сначала `trafficSecret` пустой, потом он принимает какое-то значение, и через несколько пакетов принимает другое значение, которое держится уже долго. Если пристально посмотреть на длины пакетов и на wireshark, можно понять, что пустой он при обработке server hello, первое значение он имеет при обработке первых данных, до окончания handshake, и после окончания handshake (спустя примерно 3600 байт) принимает свое финальное значение.

Значит для расшифровки нам надо:
1) Достать `trafficSecret` каким-то образом из дампа памяти.
2) Найти в wireshark нужный нам стрим, сохранить его, и обрезать handshake.
3) Написать скрипт на go для расшифровки траффика.
4) Profit?

## Достаем trafficSecret из дампа памяти

Проще всего открыть дамп памяти в [delve](https://github.com/go-delve/delve): `dlv core neo_client.elf core.1319`. Или можно [использовать](https://www.jetbrains.com/help/go/exploring-go-core-dumps.html) goland.

Открываем дамп в delve, и понимаем почему использовался странный билд `neo` вместо стандартного - у нас есть отладочная информация, что сильно упрощает жизнь, хотя в оригинальном neo она убирается при сборке.

Поскольку это программа на go, использующая сетевое взаимодействие, в ней много делается через горутины. Посмотрим все горутины через `grs`, и пойдем смотреть, какая где остановилась. Замечаем, что 16-я горутина остановилась в интересной функции - `google.golang.org/grpc/internal/transport.(*Stream).waitOnHeader`. Там однозначно есть какая-то информация о tls connect. Идем изучать:
```
gr 16
bt
frame 2
... (изучаем локальные переменные)
p s.ct.conn.Conn.in.trafficSecret
```

Ура, `trafficSecret` получен. Осталось правильно вытащить траффик.

## Достаем нужный стрим из wireshark

По http пакетам с метриками можно заметить, что адрес сервера, к которому подключается `neo_client`, `158.160.113.123`. Поставим фильтр `ip.addr == 158.160.113.123`, и видим с первых же пакетов tls стрим. Открыв его видим, что он подключается к `neo.cbsctf.live`. Выглядит как то, что нужно.
Некоторые участники могли так же найти другой tls стрим до `farm.cbsctf.live`. Это стрим отправки флагов эксплойта на [ферму](https://github.com/C4T-BuT-S4D/S4DFarm). Его можно аналогично декодировать, но в этом задании не нужно.

Делаем analyze -> follow -> tcp stream, выбираем нужное нам направление, а не entire conversation, show data as: raw и сохраняем в файл `dump.bin` для дальнейшей обработки.

Так же обратим внимание на server hello (пакет под номером 2725). Этот пакет нам не нужно декодировать нашим ключом, т.к. он идет до окончания handshake, и он содержит 3612 байт данных, что можно посмотреть в TCP -> Tcp Segment Len.

## Обрабатываем файл в удобный вид

Я не настоящий go разработчик, поэтому мне проще сначала максимально подготовить код питоном, а потом с помощью chatgpt написать код для его обработки на go.

Проверяем, что длина `handshake` действительно 3612:
```python
data = open('./dump.bin', 'rb').read()
print(data[3612:3620].hex()) # 170303003891b391
```

Начинается с 170303, значит скорее всего все правильно.
Подготовим данные для максимально простой работы из go с ними - разобьем данные по отдельным сообщениям.
TLS сообщения имеют вид `[header (17)][version (0303 для tls 1.3)][length (2 байта)][data]`
```python
messages = []
i = 3612 # skip handshake
while i < len(data):
    assert data[i:i+3] == b'\x17\x03\x03'
    length = data[i + 4] + 256 * data[i + 3]
    messages.append(data[i:i+5+length])
    i += 5 + length

with open('dump.hex', 'w') as fout:
    for m in messages:
        print(m.hex(), file=fout)
```

Приступаем к написанию программы на go.

## Пишем скрипт на go

Проще всего будет внести изменения в стандартную библиотеку go, чтобы сделать структуру `halfConn` публичной. Поэтому поднимаем docker/виртуальную машину, чтобы не сломать себе систему.

```go
type HalfConn struct {
	inner halfConn
}

func NewHalfConn() HalfConn {
	x := HalfConn{}
	x.inner.version = VersionTLS13
	x.inner.level = QUICEncryptionLevelApplication

	return x
}

func (hc *HalfConn) SetTrafficSecret(secret []byte) {
	suite := &cipherSuiteTLS13{TLS_AES_128_GCM_SHA256, 16, aeadAESGCMTLS13, crypto.SHA256}
	hc.inner.setTrafficSecret(suite, QUICEncryptionLevelApplication, secret)
}

func (hc *HalfConn) Decrypt(data []byte) ([]byte, recordType, error) {
	return hc.inner.decrypt(data)
}
```

Значения `cipherSuite` взяты из wireshark server hello -> tls -> tls1.3 record layer -> handshake protocol -> cipher suite
Значение `QUICEncryptionLevelApplication` подобрано перебором.

Отлично, пишем сам скрипт.
```go
package main

import (
	"bufio"
	"crypto/tls"
	"encoding/hex"
	"fmt"
	"os"
)

func must[T any](data T, err error) T {
	if err != nil {
		panic(err)
	}
	return data
}

func main() {
	data := must(os.Open("./dump.hex"))
	scanner := bufio.NewScanner(data)
	hc := tls.NewHalfConn()
	// значение из dlv
	hc.SetTrafficSecret([]byte{189, 142, 31, 146, 119, 66, 170, 178, 200, 207, 109, 9, 195, 36, 188, 83, 50, 31, 238, 176, 2, 51, 91, 54, 245, 40, 123, 213, 10, 9, 22, 185})
	allData := make([]byte, 0)
	for scanner.Scan() {
		line := scanner.Text()
		data := must(hex.DecodeString(line))
		decoded, rt, err := hc.Decrypt(data)
		if err != nil {
			break
		}
		fmt.Println(rt)
		allData = append(allData, decoded...)
	}
	os.WriteFile("output", allData, 0644)
}
```

## Получениe флага
Запускаем `strings output | grep ctfcup` и.. расстраиваемся, никакого флага.

Если вспомнить dlv, то можно понять, что используется grpc. И можно предположить, что траффик как-то сжат или закодирован.
Попробуем вытащить его втупую.
```bash
binwalk -Me output
grep -nri ctfcup output
# ./B47:20:TEAM_TOKEN = "ctfcup{N0_sTringS_N0w?}"
```

Ура, флаг получен.
Решение не идеальное, потому что и расшифровка на самом деле падает с ошибкой (поэтому нужен именно `break`).

Для идеального решения надо добыть полноценный pre-shared-key, чтобы автоматически расшифровывать полный траффик и извлекать абсолютно все данные, но это будет в следующей серии.

Отдельное спасибо [@pomo-mondreganto](https://github.com/pomo-mondreganto) за шикарные утилиты, поставьте ему звездочку на гитхабе.
