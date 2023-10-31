# for | Gamer

## Information
*Часть вторая.* В самом деле, не могла же древняя игрулька так затуманить разум элитного агента! 
Он нам что-то недоговаривает... В зрительную кору по `arbassh` не зайдешь, а нужно узнать, что на самом деле у него там мелькает.
Вербуют ли его?

*Part Two.* I seriously doubt that some old stupid game could cloud an elite agent's mind!  He must not be telling us the whole truth... It's not like we could `arbassh` into his visual cortex, but we need to know exactly what he's seeing there. Is he being secretly recruited?


## Public
Provide for-misc-gamer.7z to players.

for-misc-gamer.7z: `e0129d4b8eb37cc24c3c234ea25b21ff53094264ec72b5977067c5da76e6e463`

## TL; DR
Recover MPEG TS data from firefox.exe processes in the dump.

## Writeup (ru)

В дампе памяти можно увидеть процессы `firefox.exe`. Есть несколько способов понять, что именно было открыто в браузере, а именно стрим на твиче.

Много команд смогли сделать достоверный скриншот рабочего стола. Флаг можно было увидеть в левом верхнем углу трансляции. Решение, задуманное автором, заключалось в нахождении кусков MPEG-TS в дампах `firefox.exe`.

## Writeup (en)

In the RAM dump, we can notice `firefox.exe` processes. There are a number of ways to identify what's being viewed through in the browser, namely, a Twitch livestream.

Many teams were able to obtain a full screenshot and see the flag, which was located in the top left corner of the video. The intended solution, however, was to simply run binwalk on firefox.exe dumps. It is able to recover MPEG-TS pieces of the livestream.

## Flag
`ctfcup{th4nks_f0r_th3_f4t_10_g1f7_Sub5_p1k4CHu_mY_C0}`
