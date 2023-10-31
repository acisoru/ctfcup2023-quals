# rev | 2fac

## Information
Пришли к нам тут продаваны, мол, смотрите на наш крутой и безопасный алгоритм двухфакторки. 
Говорят, им пользуются даже Арбалеты Сибири!

Some vendors came to us here, saying, "Look at our cool and secure two-factor algorithm". They say it is used even by the Arbalest of Siberia!

## Public
Give `rev-2fac.zip` to players.

## TL;DR
Reverse engineer the algorithms used in 2fac app, then take over the accounts on '2fac Demo' website, one of which will contain the flag.

## Writeup (ru)

#### Разведка

[Потыкаем приложение](https://youtu.be/JISOK8_bcpE).

Получается, нам дано приложение, которое умеет генерировать коды двухфакторной аутентификации. Ключевая особенность - оно также генерирует одноразовый 
код сброса этой самой двухфакторки. Код, естественно, может быть сгенерирован только один раз (дальше информация, нужная для генерации, теряется).

На сайте мы можем создать аккаунт и сохранить в нем заметку. Очевидно, флаг стоит искать именно в заметках.

#### Ревёрс
В приложении не используется обфускация, только минификация ProGuard и... приколы котлина, Jetpack Compose и Hilt. 
(Но признаюсь, что почти пустая `MainActivity` меня удивила.)

На что стоит обратить внимание:
1. В классе `x6.e` содержится код dependency injection. Найти его можно по использованию `R.raw` (обычно там само собой ничего не появляется).
```java
            InputStream openRawResource = context4.getResources().openRawResource(R.raw.words);
            z5.g.I(openRawResource, "context.resources.openRawResource(R.raw.words)");
```

2. В классе `x6.e` также есть логика получения `appSignature`, которая на самом деле является сертификатом разработчика приложения.
```java
o1.n nVar2 = fVar.f8422b;
                Context context3 = fVar.f8421a.f3124g;
                z5.g.J(context3);
                nVar2.getClass();
                Signature[] apkContentsSigners = context3.getPackageManager().getPackageInfo(context3.getPackageName(), 134217728).signingInfo.getApkContentsSigners();
                z5.g.I(apkContentsSigners, "context.packageManager\n \u2026ngInfo.apkContentsSigners");
                byte[] byteArray = ((Signature) w5.k.x1(apkContentsSigners)).toByteArray();
                z5.g.I(byteArray, "context.packageManager\n \u2026ers.first().toByteArray()");
                return byteArray;
```

Достать этот сертификат можно Фридой:
```js
Java.perform(() => {
  const ActivityThread = Java.use("android.app.ActivityThread");
  const PackageManager = Java.use("android.content.pm.PackageManager");

  // Get the current application context
  const context = ActivityThread.currentApplication().getApplicationContext();

  console.log(PackageManager.GET_SIGNING_CERTIFICATES.value)
  const x = context
    .getPackageManager()
    .getPackageInfo(context.getPackageName(), PackageManager.GET_SIGNING_CERTIFICATES.value)
    .signingInfo.value.getApkContentsSigners()[0].toByteArray();
  console.log(x)
});
```

3. В классе `x6.e0` реализована генерация тех самых кодов сброса. Работает примерно так: для каждого N в 0..20000 вычисляется 18-е число Фибоначчи, но с условием `F_0 = F_1 = N`. Если хеш этого числа и перемешанных юзернейма и домена совпадает с `nonce`, по вычисленному числу выбираем три слова из словаря сидов биткойна (`res/raw/words.txt`).

4. К великому счастью, ViewModel класс `TwoFacViewModel` искать не надо, он пережил минификацию. В нем находим алгоритм генерации собственно 2fac кодов. Происходит следующее: конкатенируется текущее Unix время, деленное на 30 (в десятичной записи), вот прямо буквально `.toString()` от `data class Json()` (XDDD), в котором лежат юзернейм, домен и секрет, и та "подпись". Хешируется SHA-384. Затем байты хеша хитро складываются, результат берется по модулю 2048. Выбирается одно из биткойн-слов. Затем дописываются по две цифры с начала и с конца хексов хеша.

5. Алгоритм из пункта 3 реализован через рекурсию, поэтому работает медленно (телефон на видео целую секунду считал именно его).

6. Формат QR-кодов:
```
username
domain (always 2fac-demo.com)
secret (random uuid)
nonce (sha256)
```

#### Великий похек

Признаюсь. Я забыл добавить в описание таска то, что "продаваны" хвастались неприступностью системы: даже если знать пароль, взломать аккаунт невозможно. Соответственно, наша задача - доказать обратное.

На странице логина в HTML комментарии была упомянута ручка `/__pwned_by_Slonser__`, которая выдает логины, пароли и префиксы nonce (из пункта 3 выше).

[Этот скрипт](solve/sploit.py) для каждого пользователя генерирует и применяет код сброса, затем генерирует 2fac код, чтобы войти и посмотреть заметку.
У одного из пользователей в заметке оказывается флаг.

## Writeup (en)

#### Recon

Let's take the app for a spin! Here's a [video](https://youtu.be/JISOK8_bcpE). 

We are given a two factor authenticator app and a website to test it on. The defining feature are so-called 'recovery codes', which are supposedly
generated only once (then the information required to produce one is discarded forever).

On the website, we can create an account and store a note. Obviously, this is where the flag will be located.

#### Reversing the app
The app isn't especially protected from reverse engineering. This is just bog-standard minified Koltin code with Hilt and Jetpack Compose 
(although I must admit that MainActivity perplexed me the first time I saw it).

Key things to look at when reversing the app:
1. Class `x6.e` contains DI code for words from the generated codes. You can find it by looking through resources and grepping for usages of class `R`.
```java
            InputStream openRawResource = context4.getResources().openRawResource(R.raw.words);
            z5.g.I(openRawResource, "context.resources.openRawResource(R.raw.words)");
```

2. Class `x6.e` also provides 'appSignature' (which is actually just the app developer's certificate, a lengthy blob of bytes).
```java
o1.n nVar2 = fVar.f8422b;
                Context context3 = fVar.f8421a.f3124g;
                z5.g.J(context3);
                nVar2.getClass();
                Signature[] apkContentsSigners = context3.getPackageManager().getPackageInfo(context3.getPackageName(), 134217728).signingInfo.getApkContentsSigners();
                z5.g.I(apkContentsSigners, "context.packageManager\n \u2026ngInfo.apkContentsSigners");
                byte[] byteArray = ((Signature) w5.k.x1(apkContentsSigners)).toByteArray();
                z5.g.I(byteArray, "context.packageManager\n \u2026ers.first().toByteArray()");
                return byteArray;
```

You can obtain the 'signature' using a Frida snippet:
```js
Java.perform(() => {
  const ActivityThread = Java.use("android.app.ActivityThread");
  const PackageManager = Java.use("android.content.pm.PackageManager");

  // Get the current application context
  const context = ActivityThread.currentApplication().getApplicationContext();

  console.log(PackageManager.GET_SIGNING_CERTIFICATES.value)
  const x = context
    .getPackageManager()
    .getPackageInfo(context.getPackageName(), PackageManager.GET_SIGNING_CERTIFICATES.value)
    .signingInfo.value.getApkContentsSigners()[0].toByteArray();
  console.log(x)
});
```

3. Class `x6.e0` implements the 'reset code' generation. It works something like this: for each N in 0..20000 calculate the 18th
number using a modified Fibonacci sequence algorithm, where `F_0 = F_1 = N`. Hash that with interleaved 'username' and 'domain' strings
and compare with 'nonce'. If found, use the calculated 'kinda Fiboancci' number to select three words from Bitcoin seed mnemonic wordlist (located in `res/raw/words.txt`).

4. To our great relief, `TwoFacViewModel`'s class name survived ProGruard's minify, so we don't have to search for that.
In there, we can see how 2fac codes are generated. Current unix timestamp divided by 30 (as a decimal string), quite literally a `toString()` of `data class Json(...)` containing username, domain and secret, and the app signature injected from `x6.e` are concatenated and hashed with SHA-384. Then a word is selected from our wordlist using an index calculated from the byte values of the hash. Finally, two digits are selected from both ends of a hex representation of our hash.

5. The 'kinda Fibonacci' algorithm mentioned in (3) is slow (see video) because it uses recursion.

6. QR codes are in the following format:
```
username
domain (always 2fac-demo.com)
secret (random uuid)
nonce (sha256)
```

#### Hacking the World

Great, now we have the algorithm at our fingertips. But who do we hack? I must admit, I forgot to give a crucial piece of info in the description - those 
vendors were actually very proud that even if the passwords got leaked, it would be impossible to hack someone. This was implemented in a secret page, 
`/__pwned_by_Slonser__`, which gave usernames, passwords and first 8 hex digits of nonces. It was pointed to in a HTML comment on `/login` and `/reset`:

![image](https://github.com/C4T-BuT-S4D/ctfcup-2023-quals/assets/18624304/bbdf6093-cf85-4711-ae94-4e605224c442)

The task then becomes to, for every one of 289 fake accounts, generate a reset code, get a new 2fac secret, then log in. [This script](solve/sploit.py) implements
the attack. One user's notes contain the flag.

## Flag
Dynamic

