# ppc | checkpoint

## Information

Вот же Арбалеты паразиты, везде ввели свой контроль! Теперь даже в соседний город нельзя съездить не находясь при этом каким-то сверхчеловеком - говорят, обычным людям нечего лишний раз по пустошам Metra ездить, как будто мы и сами не можем о себе позаботиться. Вот бы научиться как-нибудь обходить эту дрянь...

Oh, these bloody Arbalests leeches, trying to control absolutely everything! Now you aren't even allowed to visit a neighboring city without being some kind of superhuman, which they explain by saying that ordinary people have no business driving through Metra's wastes, as if we can't take care of ourselves. I wish we could come up with a way of somehow bypassing this crap...

## Deploy

Need whale deployment.

```sh
cd deploy
docker compose -p ppc-checkpoint up --build -d
```

## Public

Provide zip file: [public/checkpoint.zip](public/checkpoint.zip).

## TLDR

1. Gather many samples in order to build some sort of voice matching system (e.g. by using a distance function such as `dtw` on top of `mfcc` or `Chroma CENS`).
2. Exploit the fact that you can basically "checkpoint" after each successful flag, since the session at such a point isn't revoked in any way.

## Writeup (ru)

По данным исходникам можно понять, что для получения флага требуется корректно решить 100 "аудиокапч" подряд с ограничением в 5 секунд на каждую капчу. При этом, сами записи, из которых генерируются капчи, нам не даны, из-за чего придется либо самостоятельно их доставать, генерируя множество капч, и далее использовать для распознавания на основании схожести, либо использовать полноценное распознование голоса. Практически любое распознование голоса работает всё ещё крайне плохо, когда качество звука не идеально, как было и здесь со сгенерированными голосами.

Первым же способом как раз воспользоваться достаточно несложно - каждая аудизапись состоит из 10 букв, произнесённых [фонетическим алфавитом НАТО](https://en.wikipedia.org/wiki/NATO_phonetic_alphabet), и все буквы при этом достаточно чётко отделены тишиной, за счёт чего разделять аудиозаписи на буквы не составляет особого труда. Собрав достаточно большое количество семплов, можно построить любую систему для распознавания на основании схожести полученной записи и семплов (замечу, что полного совпадения здесь быть не может, так как капча передаётся в формате `mp3` записи, аудио в которой передаётся со сжатием с потерями), например, по характеристикам [MFCC](https://en.wikipedia.org/wiki/Mel-frequency_cepstrum) или [Chroma](https://en.wikipedia.org/wiki/Chroma_feature), и с функцией для подсчёта "схожести" между характеристиками, например, [DTW](https://en.wikipedia.org/wiki/Dynamic_time_warping).

На самом деле, в методе `generate` присутствует бага, которая позволяет упростить таск: после проверки, что капча пройдена ([deploy/checkpoint.py#L58](./deploy/checkpoint.py#L58)), старая сессия никаким образом не инвалидируется, что позволяет её переиспользовать при неверном прохождении следующей капчи. По сути, это даёт возможность восстанавливаться из "чекпоинтов".

Итоговое решение со всеми этими шагами реализовано в [solve/solve.py](./solve/solve.py), а собранные для решения семплы в файле [solve/samples.zip](./solve/samples.zip).

## Writeup (en)

By the given sources of the task, it's easy to realize that in order to get the flag 100 "audio-CAPTCHAs" in a row must be solved correctly with a time limit of 5 seconds on each CAPTCHA. The original audiorecordings used to generated the CAPTCHAs, however, aren't given to us, which means that we would either need to retrieve them ourselves by generating lots of CAPTCHAs in the task, and then use said recordings to solve the CAPTCHAs based on similarity of the audio, or use actual speech recognition. Pretty much any speech recognition still works incredibly bad when the quality of the audio isn't perfect, which was the case with the generated voices.

It's not particularly difficult to implement the first solution method - each audio recording consists of 10 letters pronounced using the [NATO phonetic alphabet](https://en.wikipedia.org/wiki/NATO_phonetic_alphabet), and, additionally, the pronounciation of each letter is separated from the previous' by a segment of silence of pretty long duration, which allows us to separate each recording into its parts relatively easily. Having collected enough samples, any audio-matching system can be built for recognition of the letters of the recordings based on the similarity of said recordings and the collected samples. Note that there will never be full equality of the recordings, since each recording is passed in the `mp3` format with lossy compression. For matching features such as [MFCC](https://en.wikipedia.org/wiki/Mel-frequency_cepstrum) and [Chroma](https://en.wikipedia.org/wiki/Chroma_feature) can be used, alongside a "distance" calculation function, for example, [DTW](https://en.wikipedia.org/wiki/Dynamic_time_warping).

Actually, however, there was also a way to simplify the solution, since a bug in the `generate` method is present: after validating, that the last CAPTCHA has been completed ([deploy/checkpoint.py#L58](./deploy/checkpoint.py#L58)), the old session is not invalidated, which allows us to reuse it after failing to complete the next CAPTCHA. This bug, pretty much, allows us to restore from "checkpoints".

The final solution with all of these steps is implemented in [solve/solve.py](./solve/solve.py), and the collected samples used for the solution are available in [solve/samples.zip](./solve/samples.zip).

## Domain

No

## Cloudflare

Yes

## Flag

Should be auto-generated by Whale.
