# Positve Tasks | Mystery_ldap

## Information

> Привет! 
> Наша команда ИБ задетектировала инцидент! 
> Злоумышленники смогли проникнуть в надежно защищенный сегмент. Эксперты нашли подозрительный ldap трафик, который вызвал у них особый интерес. Они предоставили его вам и ждут, что именно вы сможете разобраться в этом происшествии.

## Deploy


## Public

Provide pcap file: [public/tasmystery_ldap.pcap](public/mystery_ldap.pcap).


## Writeup (ru)

В pcap файле находится одна большая ldap сессия от пользователя fragger. Беглый анализ показывает, что сначала пользователь начинает вычитывать все объекты из домена, затем поочередно запрашивать и пытаться менять собственные атрибуты.

![image10][images/image10.png]
Запрос объектов из домена от пользователя fragger 

![image4][images/image4.png]
Попытки модификации значений атрибутов пользователя fragger:

Также в дампе содержатся запросы к некоторым атрибутам другого пользователя домена с уз cobalt. Значения атрибута mSMQSignCertificates содержат base64.

![image1][images/image1.png]
Base64 в атрибуте mSMQSignCertificates пользователя cobalt

![image9][images/image9.png]
Декодированный base64 из атрибута mSMQSignCertificates

![image5][images/image5.png]
Гугление приводит к утилите https://github.com/fox-it/LDAPFragger

Анализ утилиты LDAPFragger показывает, что клиентская часть коммуницирует с серверной частью через протокол ldap посредством записи и считывания данных в различные атрибуты. Серверная часть при первой установке связи следует на С2 сервер Cobalt Strike, выгружает кастомный стейджер и передает его на клиента через запись в атрибуты.

![image8][images/image8.png]
Загрузка стейджера и передача на клиента

Находим в трафике загрузку стейджера

![image3][images/image3.png]
Первый кусок стейджера в ldap

После декодирования видим, что сообщение поделено на 6 частей

![image2][images/image2.png]
Декодированное сообщение с первой частью

Сделаем еще декод внутреннего сообщения.

![image7][images/image7.png]
1 часть стейджера

Извлечем все 6 частей, сложим вместе и отправимся анализировать полученный файл. Гугление приводит к различным инструментам анализа. Попробуем достать конфиг с помощью утилиты https://github.com/Sentinel-One/CobaltStrikeParser
В конфиге находится заветный флаг

![image6][images/image6.png]
Флаг в извлеченном конфиге

## Writeup (en)

The pcap file contains one large ldap session from the fragger user. A cursory analysis shows that the user first starts reading all objects from the domain, then alternately querying and trying to change his own attributes.

![image10][images/image10.png]
Querying objects from the domain from user fragger 

![image4][images/image4.png]
Attempts to modify attribute values of the fragger user:

The dump also contains requests for some attributes of another domain user with the node cobalt. The values of the mSMQSignCertificates attribute contain base64.

![image1][images/image1.png]
Base64 in the mSMQSignCertificates attribute of user cobalt

![image9][images/image9.png]
Decoded base64 from the mSMQSignCertificates attribute

![image5][images/image5.png]
Googling leads to the utility https://github.com/fox-it/LDAPFragger

Analysis of the LDAPFragger utility shows that the client part communicates with the server part via the ldap protocol by writing and reading data to various attributes. The server part, when first establishing communication, follows the C2 server Cobalt Strike, unloads the custom stager and passes it to the client via writing to attributes.

![image8][images/image8.png]
Loading the steager and passing it to the client

Find the steager load in the traffic

![image3][images/image3.png]
The first piece of the steager in ldap

After decoding we see that the message is divided into 6 parts

![image2][images/image2.png]
Decoded message with the first part

Let's do some more decoding of the internal message.

![image7][images/image7.png]
1 part of the stager

Let's extract all 6 parts, put them together and go analyze the resulting file. Googling leads to various analysis tools. Let's try to get the config using the utility https://github.com/Sentinel-One/CobaltStrikeParser.
And config contains our flag.

![image6][images/image6.png]
Flag in the extracted config

## Flag

ctfcup{c0balt_hunt1ng_m@st3r}