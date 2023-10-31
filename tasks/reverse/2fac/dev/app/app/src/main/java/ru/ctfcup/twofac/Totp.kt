package ru.ctfcup.twofac

import android.content.Context
import android.content.pm.PackageManager
import android.util.Log
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import java.security.MessageDigest
import javax.inject.Inject
import javax.inject.Qualifier
import javax.inject.Singleton
import kotlin.math.absoluteValue

const val TOTP_INTERVAL_SECONDS = 30L
const val TOTP_RECOVERY_WORK = 18L
val TOTP_RECOVERY_RANGE = 0..20000

@Module
@InstallIn(SingletonComponent::class)
class TotpModule {
    @WordList
    @Singleton
    @Provides
    fun provideWordlist(@ApplicationContext context: Context): List<String> =
        context.resources.openRawResource(R.raw.words)
            .bufferedReader()
            .use { it.readText() }
            .split("\n")

    @AppSignature
    @Singleton
    @Provides
    fun provideAppSignatureHex(@ApplicationContext context: Context): ByteArray =
        context.packageManager
            .getPackageInfo(context.packageName, PackageManager.GET_SIGNING_CERTIFICATES)
            .signingInfo.apkContentsSigners.first().toByteArray()
}

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class WordList

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class AppSignature

class Totp @Inject constructor(
    @WordList private val wordlist: List<String>,
    @AppSignature private val appSignature: ByteArray
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
//        Log.d("RecoveryCode", "appsig " + appSignature.toHex())

        val salt = interleaveStrings(secret.username, secret.domain)

        var nonceN = TOTP_RECOVERY_RANGE.first {
             nonce == MessageDigest.getInstance("SHA-256")
                .digest("$salt-${horribleFib(it.toLong(), TOTP_RECOVERY_WORK)}".toByteArray()).toHex()
        }.let { horribleFib(it.toLong(), TOTP_RECOVERY_WORK) }.absoluteValue

        return List(3) {
            (nonceN % wordlist.size).also { nonceN /= wordlist.size }
        }.joinToString("-") { wordlist[it.toInt()] }
    }

    companion object {
        fun horribleFib(start: Long, n: Long): Long {
            if (n <= 1L) return start
            return horribleFib(start, n - 1) + horribleFib(start, n - 2)
        }

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
