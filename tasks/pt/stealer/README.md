# Positve Tasks | stealer

## Information

> В компании произошла утечка. К счастью, нам удалось локализовать машину и забрать с нее подозрительный трафик. 
> Помоги выяснить, что украли злоумышленники.


## Public

Provide pcap file: [public/trace.pcapng](public/trace.pcapng).

## Writeup (ru)

В pcap файле, отфильтровав по протоколу http, можно заметить подозрительные GET POST запросы на 10.0.0.1

Первый GET запрос возвращает бинарь (стиллер), второй GET запрос возвращает AES ключ, третий POST запрос отправляет зашифрованные данные на сервер.Бинарь - sfx архив с dotnet стиллером и парой библиотек к нему. Стиллер немного обфусцирован.

Но после недолгого переименования все становится видно. До main вызываются различные проверки на антиотладку, окружение, виртуальные машины. 
Стиллер ворует учетки и куки из chrome и firefox, шифрует их RC4 с зашитым ключом, затем AES, ключ которого получен с сервера, затем base64 и urlencode.
Поняв алгоритм, нужно взять данные из pcap файла и расшифровать.

Пример полного решения в [CyberChef](https://gchq.github.io/CyberChef/#recipe=URL_Decode()Drop_bytes(0,7,false)From_Base64('A-Za-z0-9%2B/%3D',true,false)AES_Decrypt(%7B'option':'UTF8','string':'d90f7g07asd0g80f'%7D,%7B'option':'Hex','string':'5b%2082%20d5%200b%200d%2007%2062%2097%2036%207f%209e%2031%2041%20c3%2035%2075'%7D,'CBC','Raw','Hex',%7B'option':'Hex','string':'13%2012%2012%2012%2012%2012%2012%2012%2012%2012%2012%2012%2012%2012%2012'%7D,%7B'option':'Hex','string':''%7D)RC4(%7B'option':'UTF8','string':'timewaitsfornoone'%7D,'Hex','UTF8')&input=UmVzdWx0PUJva2ZPZyUyQiUyQkdrOEVUaVU5RFMzdnRtdGdkRzB4TkR3azI2M1oxZ012eXc1b2J0N3ZoUnljRW9EbnluSVQxVFRxbWtRUkg4dDdNV2NLczlJTHFrVWxBJTJCcTZGR2JLWmclMkI0MUJSWnFCajM5OVJlUFclMkJmbkgyOGNtWUZOMXZLTGVzeU90RXZ1WmY5dWQ3dXd5Q2oyNzdBdmJYb0JPRXJzVWhDVzAwVTV6JTJCSU40Qk9admlZaHNqMHp5VGsyYmdHbDlDZmZpc2xMb3YxMUJOUzdDRnpWJTJCS1FDc2xRWjlpNyUyQkpNeVJzaTU0RHd4R0plZ3VyUFJqOTglMkZpTGJVZCUyQjRRV0N0ZUNFNmM4Qk1qWHRnJTJGR3U5ODl3dkJ2RTljdjFqMFUlMkZPeHVuWWJHcXRucTRkajBvV0ZPUGNCM0NZZ2s3R0RJenlVQ3klMkZmR0tKR3RIVW9ERXZjNEolMkZRZDE5ejhzU0Z2UENWNkJmbEMyJTJCc2Z4Q05xUFN2T3piMmgzR05YVFl6RnY2c2FiVDlNOThhVEZDekprSWtCMUJaamFaMm1GR09XNWw4ZUZMNjl2aVZCSmpFWlJGRnJDRG9jTDFjYWdiWFQwREZra0dXb2V2JTJCR1NnYWJ0bTQxJTJGNDdnZ0V0MURrZWJPamlFRGclMkZMWXR6bjNhVlNqd3d1VzZ1VWttQlgycmcyUlVOODZSakh5bFZIYzVPZmZIVThDTEpSQnhOWFRxdzQ1RUtETWJXTXFzOTRBUTZ6ZWppSEhDJTJCJTJGTkk0TmhGODZWQ0lJN0s2T3U1dGhQT1BnY1VSeFNJV3RZRmZRVmJsenJFRjJHMm1GUFRiY0ZJa1FmdFZ2QUlqJTJGQW9nRlN5VFlaMlg)

## Writeup (en)
In pcap file, filtered by http protocol, we can notice suspicious GET POST requests to 10.0.0.1

The first GET request returns a binary (styler), the second GET request returns an AES key, the third POST request sends encrypted data to the server.
The binary is a sfx archive with dotnet styler and a couple of libraries for it. The styler is a bit obfuscated.

But after a short renaming everything becomes visible. Before main various checks for anti-debugging, environment, virtual machines are called. 
Stiller steals credentials and cookies from chrome and firefox, encrypts them with RC4 with encrypted key, then AES, which key is obtained from the server, then base64 and urlencode.
Once you understand the algorithm, you need to take the data from the pcap file and decrypt it.

An example of the full solution in [CyberChef](https://gchq.github.io/CyberChef/#recipe=URL_Decode()Drop_bytes(0,7,false)From_Base64('A-Za-z0-9%2B/%3D',true,false)AES_Decrypt(%7B'option':'UTF8','string':'d90f7g07asd0g80f'%7D,%7B'option':'Hex','string':'5b%2082%20d5%200b%200d%2007%2062%2097%2036%207f%209e%2031%2041%20c3%2035%2075'%7D,'CBC','Raw','Hex',%7B'option':'Hex','string':'13%2012%2012%2012%2012%2012%2012%2012%2012%2012%2012%2012%2012%2012%2012'%7D,%7B'option':'Hex','string':''%7D)RC4(%7B'option':'UTF8','string':'timewaitsfornoone'%7D,'Hex','UTF8')&input=UmVzdWx0PUJva2ZPZyUyQiUyQkdrOEVUaVU5RFMzdnRtdGdkRzB4TkR3azI2M1oxZ012eXc1b2J0N3ZoUnljRW9EbnluSVQxVFRxbWtRUkg4dDdNV2NLczlJTHFrVWxBJTJCcTZGR2JLWmclMkI0MUJSWnFCajM5OVJlUFclMkJmbkgyOGNtWUZOMXZLTGVzeU90RXZ1WmY5dWQ3dXd5Q2oyNzdBdmJYb0JPRXJzVWhDVzAwVTV6JTJCSU40Qk9admlZaHNqMHp5VGsyYmdHbDlDZmZpc2xMb3YxMUJOUzdDRnpWJTJCS1FDc2xRWjlpNyUyQkpNeVJzaTU0RHd4R0plZ3VyUFJqOTglMkZpTGJVZCUyQjRRV0N0ZUNFNmM4Qk1qWHRnJTJGR3U5ODl3dkJ2RTljdjFqMFUlMkZPeHVuWWJHcXRucTRkajBvV0ZPUGNCM0NZZ2s3R0RJenlVQ3klMkZmR0tKR3RIVW9ERXZjNEolMkZRZDE5ejhzU0Z2UENWNkJmbEMyJTJCc2Z4Q05xUFN2T3piMmgzR05YVFl6RnY2c2FiVDlNOThhVEZDekprSWtCMUJaamFaMm1GR09XNWw4ZUZMNjl2aVZCSmpFWlJGRnJDRG9jTDFjYWdiWFQwREZra0dXb2V2JTJCR1NnYWJ0bTQxJTJGNDdnZ0V0MURrZWJPamlFRGclMkZMWXR6bjNhVlNqd3d1VzZ1VWttQlgycmcyUlVOODZSakh5bFZIYzVPZmZIVThDTEpSQnhOWFRxdzQ1RUtETWJXTXFzOTRBUTZ6ZWppSEhDJTJCJTJGTkk0TmhGODZWQ0lJN0s2T3U1dGhQT1BnY1VSeFNJV3RZRmZRVmJsenJFRjJHMm1GUFRiY0ZJa1FmdFZ2QUlqJTJGQW9nRlN5VFlaMlg)

## Flag

ctfcup{y0ur_p455w0rd5_4r3_n07_54f3}