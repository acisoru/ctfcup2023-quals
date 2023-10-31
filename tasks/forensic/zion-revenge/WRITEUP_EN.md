# Research

We are given two files, a memory dump and a traffic dump. Running `strings` on the memory dump shows that this is a program on go, called `/home/ctf/word.exe` (don't let the `.exe` extension confuse you, this is a linux program). You may also notice lines about some `neo`, like `neo_exploit_queue_exploit_run_time_seconds_bucket` (which looks like some kind of metric, but is not googleable). There is nothing else useful in the memory dump so far, let's move on to traffic analysis.

# Analyzing traffic dump
Wireshark is your best friend when working with .pcap files, so let's use it. At the very beginning we see an unencrypted http request - wget downloads the file `termbin.com/0gdj`. In response, we can see a bash script:
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

Great, we have a binary that is running, and for which a memory dump (it can be downloaded from the same github link), and some config file. If you google `github neo_client use_tls`, the first link leads to [repository](https://github.com/C4T-BuT-S4D/neo). Seems plausible, because the domain in the config is cbsctf.live, and the repository is owned by C4T-BuT-S4D team. With a bit of research, you can realize that this is an utility for distributed exploit running for A&D competitions, and make the assumption that either one of the exploits receives a flag from another team, or contains a flag itself.

When trying to connect to `neo.cbsctf.live` we see that this domain no longer exists, so we need to dig further into the traffic and memory dump. Unfortunately, some ip addresses from the dump had already become active again by the time of CTF, and led to the left sites. This happened because everything was raised in the cloud, it was not planned.

Looking further into the traffic, we see many TLS packets to 140.82.121.3 and 185.199.110.133. According to the script, this is github, and `whois 140.82.121.3` confirms this.

At about 2774 packets we notice changes - http traffic appeared, and addresses changed. HTTP packets are collection of metrics from neo_runner, nothing interesting there. The rest is encrypted with TLS.
A little further on we see other http packets - `POST //api/register` to the address 84.252.131.189 and a little later receiving a flag via `GET //api/notes`, which receives a flag in ructf format.
This looks like some kind of exploit in A&D competition that uses sql injection to set some kind of admin flag.

This confirms the hypothesis that we have an exploit launching system running, but there is no flag for ctfcup there.

All the rest traffic is encrypted.

# Decrypting TLS

You can continue examining traffic and memory dumps (at least it is useful to use binwalk on them, and recursively search for the ctfcup substring in all unpacked files), but this will lead to nothing. There are no other options left other than decrypting tls.

## Analyzing neo_client

You can look at the sources on github and make sure that there is nothing useful or vulnerable (especially when the server is down).

Download the same `neo_client.elf` from github as in the assignment (`wget -q https://github.com/andser612345/data/raw/main/neo_client.elf`) and try to determine how it has been built.
A close reading of the `strings` output reveals the path `/opt/homebrew/Cellar/go/1.21.3`. This means that it was compiled on macos (golang supports cross-compilation out of the box) with go 1.21.3
1.21.3 is the latest version of go at the time of ctf, and you can go read its source code. The most interesting stuff is in [crypto/tls/conn.go](https://go.googlesource.com/go/+/refs/tags/go1.21.3/src/crypto/tls/conn.go):
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

That is, all decryption of incoming traffic takes place in the `halfConn` structure:
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

Right away we notice the `trafficSecret` field. Let's see how it is used.


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

Great, it's enough to get the secret key and iv for the cipher. It would be better to get [sslkeylogfile](https://datatracker.ietf.org/doc/draft-thomson-tls-keylogfile/) so wireshark can automatically decrypt [tls](https://wiki.wireshark.org/TLS#using-the-pre-master-secret), but that's more complicated, so we'll go through manual decryption.

We need to figure out two more things:
1) at which point it is set (from which point traffic should be decrypted through it)
2) what kind of messages are sent to `hc.decrypt`.

You can figure this out by closely reading the code and the tls 1.3 spec, and realize that the entire tls messages (170303...) come in, where 0x17 is the message type (tls), 0x0303 is the version (1.3), then comes the length and the message itself.

At what point to start decrypting is a bit more complicated. The easiest way is to write a test script that connects via https to the site (make sure that tls 1.3 is used!!!), and log what `trafficSecret` is used after what amount of data.
You will see (the screenshot with the proof is lost to the ages) that at first `trafficSecret` is empty, then it is set with some value, and a few packets later it takes another value that holds for a long time. If you look closely at the packet lengths and wireshark, you can see that it is empty when processing server hello, it has its first value when processing the first data, before the end of handshake, and after the end of handshake (after about 3600 bytes) it takes its final value.

So for decryption we need to:
1) Get `trafficSecret` somehow from the memory dump.
2) Find the stream in wireshark, that probably contains exploit codes, save it, and cut the handshake.
3) Write a script with go to decrypt the traffic.
4) Profit?

## Getting trafficSecret from memoryDump

The easiest way is to open the memory dump with [delve](https://github.com/go-delve/delve): `dlv core neo_client.elf core.1319`. Or you can [use](https://www.jetbrains.com/help/go/exploring-go-core-dumps.html) goland.

We open the dump in delve, and understand why non-official `neo` build was used instead of the standard one - we have debugging information, which makes life much easier, although in the original neo (from `C4T-BuT-S4D/neo` releases) it is removed when building.

Since this is a go program that uses networking, it does a lot of things with goroutines. Let's look at all the goroutines through `grs`, and go to see which one stopped where. We notice that the 16th goroutine stopped in an interesting function - `google.golang.org/grpc/internal/transport.(*Stream).waitOnHeader`. There is definitely some information about tls connect there. Let's go study it:

```
gr 16
bt
frame 2
... (looking for useful variables and struct members)
p s.ct.conn.Conn.in.trafficSecret
```

Yay, `trafficSecret' has been obtained. The only thing left to do is to get the traffic out correctly.

## Getting stream from wireshark

By http packets with metrics we can see that the address of the server to which `neo_client` connects is `158.160.113.123`. Let's put the filter `ip.addr == 158.160.113.123`, and we see from the first packets tls stream. Opening it up we see that it connects to `neo.cbsctf.live`. This looks like the most interesting stream.
Some participants may have also found another tls stream to `farm.cbsctf.live`. This is a stream of sending exploit flags to [farm](https://github.com/C4T-BuT-S4D/S4DFarm). It can be decrypted with similar methods, but is not needed in this task.

Analyze -> follow -> tcp stream, then choose corrent direction instead of "entire conversation", show data as: raw and save as `dump.bin` for further editing.

Let's also pay attention to server hello (packet number 2725). This packet does not need to be decoded with our key, because it comes before the end of handshake, and it contains 3612 bytes of data, which can be seen in TCP -> Tcp Segment Len.

## Prepare file to make it easier to read from go

I'm not a real go developer, so it's easier for me to prepare the dump with python as much as possible first, and then use chatgpt to write the code to process it in go.

Checking that handshake length is 3612:
```python
data = open('./dump.bin', 'rb').read()
print(data[3612:3620].hex()) # 170303003891b391
```

It starts with 170303, so most likely everything is correct.
Let's prepare the data for the simplest possible work from go with them - break the data into separate messages.
TLS messages have the form `[header (17)][version (0303 for tls 1.3)][length (2 bytes)][data]`.
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

Now it's time to decrypt our data with go

## Wrinting script with go

The easiest thing to do would be to modify the standard go library to make the `halfConn` structure public. So we bring up docker/virtual machine so we don't break out main OS.

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

The `cipherSuite` values are taken from wireshark server hello -> tls -> tls1.3 record layer -> handshake protocol -> cipher suite
The value of `QUICEncryptionLevelApplication` is chosen by brute force.

Nice, let's write main function.
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
	// trafficSecret from dlv
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

## Getting the flag флага
Run `strings output | grep ctfcup` and... get frustrated, no flag.

If we remember backtrace from dlv, we can realize that grpc is used. And we can assume that the traffic is somehow compressed or encoded.
Let's try to pull it out stupidly.
```bash
binwalk -Me output
grep -nri ctfcup output
# ./B47:20:TEAM_TOKEN = "ctfcup{N0_sTringS_N0w?}"
```

Hooray, the flag is received.
The solution is not perfect, because the decryption actually crashes with an error (that's why we need `break`).

For a perfect solution we need to get a full-fledged pre-shared-key to automatically decrypt full traffic and extract absolutely all data, but that will be in the next series.

Special thanks for [@pomo-mondreganto](https://github.com/pomo-mondreganto) for his amazing tools, go and star him on github.
