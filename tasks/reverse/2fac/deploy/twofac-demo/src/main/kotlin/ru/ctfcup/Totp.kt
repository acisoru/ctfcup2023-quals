package ru.ctfcup

import java.security.MessageDigest
import java.security.SecureRandom
import kotlin.math.absoluteValue

const val TOTP_INTERVAL_SECONDS = 30L
const val TOTP_RECOVERY_WORK = 18L
val TOTP_RECOVERY_RANGE = 0..20000


class Totp(
    private val wordlist: List<String>,
    private val appSignature: ByteArray
) {
    operator fun invoke(params: TwoFacSecret): String {
        val seed = (System.currentTimeMillis() / 1000L) / TOTP_INTERVAL_SECONDS

        val paramsForStr = Json(
            username = params.username,
            domain = params.domain,
            secret = params.secret
        )

        val digest = MessageDigest.getInstance("SHA-384")
            .digest("$seed-lol+$paramsForStr".toByteArray() + appSignature)

        val word = wordlist[digest.fold(0xDEAD1337BEEFL) { a, b ->
            a * 2 + digest[(b.toUInt().mod(digest.size.toUInt())).toInt()]
        }.toInt().rem(wordlist.size).absoluteValue]

        val digits = digest.toHex().filter { it.isDigit() }.let { it.take(2) + it.takeLast(2) }

        return "$word-$digits"
    }

    fun recoveryCode(secret: TwoFacSecret, nonce: String): String {
        // nonce = sha256(fib(nonce_n, 16))
        // 0..20000 fib_16
        val salt = interleaveStrings(secret.username, secret.domain)

        var nonceN = TOTP_RECOVERY_RANGE.first {
            nonce == MessageDigest.getInstance("SHA-256")
                .digest("$salt-${fib(it.toLong(), TOTP_RECOVERY_WORK)}".toByteArray()).toHex()
        }.let { fib(it.toLong(), TOTP_RECOVERY_WORK) }.absoluteValue

        return List(3) {
            (nonceN % wordlist.size).also { nonceN /= wordlist.size }
        }.joinToString("-") { wordlist[it.toInt()] }
    }

    fun nonce(secret: TwoFacSecret): String {
        val salt = interleaveStrings(secret.username, secret.domain)
        val n = SecureRandom().nextLong(TOTP_RECOVERY_RANGE.last.toLong() / 2) + TOTP_RECOVERY_RANGE.last.toLong() / 2
        return MessageDigest.getInstance("SHA-256")
            .digest("$salt-${fib(n, TOTP_RECOVERY_WORK)}".toByteArray()).toHex()
    }

    companion object {
        fun fib(start: Long, n: Long): Long {
            if (n <= 1) return start

            var a = start
            var b = start

            for (i in 2..n) {
                val sum = a + b
                a = b
                b = sum
            }

            return b
        }
//        tailrec fun fib(start: Long, n: Long): Long {
//            if (n <= 1L) return start
//            return fib(start, n - 1) + fib(start, n - 2)
//        }

        fun interleaveStrings(vararg strings: String): String {
            val maxLength = strings.maxOfOrNull { it.length } ?: 0
            val result = StringBuilder()

            for (i in 0 until maxLength) {
                for (str in strings) {
                    if (i < str.length) {
                        result.append(str[i])
                    }
                }
            }

            return result.toString()
        }
    }
}

@OptIn(ExperimentalUnsignedTypes::class)
fun ByteArray.toHex(): String =
    asUByteArray().joinToString("") { it.toString(radix = 16).padStart(2, '0') }

data class Json(
    val username: String,
    val domain: String,
    val secret: String
)
