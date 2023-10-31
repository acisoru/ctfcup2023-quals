package ru.ctfcup.twofac

import android.os.CountDownTimer
import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class TwoFacViewModel @Inject constructor(
    private val secretDao: TwoFacSecretDao,
    private val totp: Totp
): ViewModel() {
    private val _twoFactorDataList = mutableStateOf(emptyList<TwoFactorData>())
    val twoFactorDataList: State<List<TwoFactorData>> = _twoFactorDataList

    private val _recoveryToken = MutableStateFlow("")
    val recoveryToken: StateFlow<String> = _recoveryToken

    fun dismissToken() {
        _recoveryToken.value = ""
    }

    val refreshInterval = TOTP_INTERVAL_SECONDS * 1000L

    private val _timeLeft = mutableStateOf(0L)
    val timeLeft: State<Long> = _timeLeft

    init {
        // Initialize the data in the ViewModel
        viewModelScope.launch { refreshCodes() }

        // wacky stuff
        var initOffset = System.currentTimeMillis() % refreshInterval
        object : CountDownTimer(refreshInterval, 1000) {
            override fun onTick(millisUntilFinished: Long) {
                val timeLeft = millisUntilFinished / 1000 - initOffset / 1000
                if (timeLeft == -1L) {
                    onFinish()
                }
                _timeLeft.value = timeLeft + 1
            }

            override fun onFinish() {
                // Refresh the codes when the timer completes
                viewModelScope.launch { refreshCodes() }
                initOffset = 0
                start()
            }
        }.start()
    }

    fun addSecret(secret: TwoFacSecret, nonce: String) = viewModelScope.launch {
        secretDao.insertTwoFactorSecret(secret)
        refreshCodes()
        _recoveryToken.value = totp.recoveryCode(secret, nonce)
    }

    fun _genRecovery(): String = totp.recoveryCode(
        secret = TwoFacSecret(
            username = "abobus",
            domain = "sus.com",
            secret = "lol"
        ),
        nonce = "71e766ad0f0d1dce8640e96de7ba5403ff049ec592c4ffee647bcf6f31a74705"
    )

    private suspend fun refreshCodes() {
        _twoFactorDataList.value = secretDao.getAllTwoFactorSecrets().map {
            TwoFactorData(
                username = it.username,
                website = it.domain,
                code = totp(it)
            )
        }
    }
}
