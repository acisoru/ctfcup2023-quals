# rev | time_capsule

## Information

Один из артефактов былой золотой эпохи Metra Veehkim - временная капсула. Однако записка в этой временной капсуле говорит, что настоящей временной капсулой является этот файл.

An artifact of Metra Veehkim once prosperous golden age - a time capsule. However a note inside indicates that the real time_capsule is this file.

## Public

Provide archive: [public/time_capsule.zip](public/time_capsule.zip).

## TLDR

Modified md5 written on a custom virtual machine.

## Writeup (ru)

Нам дан исполняемый файл, который читает из предоставляемого файла данные и для каждого символа считает с помощью виртуальной машины хеш (модифицированный md5) от него + случайной соли. Отреверсив и реализовав хеш, можно для каждого хешированного символа перебрать все возможные 256 символов и найти подходящий. Существует альтернативное решение: подменить системный вызов getrandom, чтобы он возращал необходимую соль, и перебрать с помощью самого исполняемого файла.

## Writeup (en)

We are given an executable, which reads characters from a given file, then computes a hash (modified md5), which is implemented in a virtual machine, from the character and a random salt, and then writes both the salt and the resulting hash to the output file. Having reverse engineered the hash, we can simply bruteforce all possible 256 characters from all characters in the output file and obtain the correct ones. An alternative solution exists, where by substituting the getrandom system call, such that it returns the required salt, we are able to bruteforce a character, using the binary itself.

[Exploit](solve/solve.py)

## Flag

ctfcup{d782164a05e76de75bb7ed912557af67}
