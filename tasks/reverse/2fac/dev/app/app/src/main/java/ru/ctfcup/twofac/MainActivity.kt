@file:OptIn(ExperimentalMaterial3Api::class, ExperimentalMaterial3Api::class)

package ru.ctfcup.twofac

import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.viewmodel.compose.viewModel
import com.google.zxing.BarcodeFormat
import com.journeyapps.barcodescanner.DecoratedBarcodeView
import com.journeyapps.barcodescanner.DefaultDecoderFactory
import dagger.hilt.android.AndroidEntryPoint
import ru.ctfcup.twofac.ui.theme._2facTheme

data class TwoFactorData(val username: String, val website: String, val code: String)

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            _2facTheme {
                TwoFactorAuthUI()
            }
        }
    }
}

@Composable
fun TwoFactorAuthUI(
    viewModel: TwoFacViewModel = viewModel()
) {
    var showDialog by remember { mutableStateOf(false) }

    val twoFactorDataList by viewModel.twoFactorDataList
    val timeLeft by viewModel.timeLeft
    val recoveryToken by viewModel.recoveryToken.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("2fac") },
                colors = TopAppBarDefaults.smallTopAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                ),
                actions = {
//                    SmallFloatingActionButton(onClick = {
//                        Toast.makeText(context, viewModel._genRecovery(), Toast.LENGTH_SHORT).show()
//                    }) {
//                        Icon( imageVector = Icons.Default.Build, contentDescription = null )
//                    }
                    CountdownPie(timeLeft = timeLeft, maxTime = TOTP_INTERVAL_SECONDS, Modifier.padding(end = 16.dp))
                }
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { showDialog = true },
                modifier = Modifier.padding(16.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Add,
                    contentDescription = null
                )
            }
        }
    ) { pv ->
        LazyColumn(Modifier.padding(pv)) {
            items(twoFactorDataList) { TwoFactorCard(it) }
        }
        Spacer(Modifier.height(48.dp))
    }

    if (showDialog) {
        ModalBottomSheet(
            onDismissRequest = { showDialog = false },
        ) {
            AndroidView(
                modifier = Modifier
                    .height(300.dp)
                    .padding(bottom = 16.dp),
                factory = { context ->
                DecoratedBarcodeView(context).apply {
                    barcodeView.decoderFactory = DefaultDecoderFactory(listOf(BarcodeFormat.QR_CODE))
                    resume()
                    decodeSingle {
                        val parts = it.text.split("\n")
                        viewModel.addSecret(
                            TwoFacSecret(
                                username = parts[0],
                                domain = parts[1],
                                secret = parts[2]
                            ), nonce = parts[3])


                        showDialog = false
                    }
                }
            })
        }
    }

    if (recoveryToken.isNotEmpty()) {
        AlertDialog(
            onDismissRequest = {
                viewModel.dismissToken()
            },
            title = { Text("Your recovery token") },
            text = {
                Column {
                    Text(
                        buildAnnotatedString {
                            append("This token can be used to reattach 2fac to your account. ")
                            withStyle(style = SpanStyle(fontWeight = FontWeight.Bold)) {
                                append("Please write it down now, as it is only shown once.")
                            }
                        }
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = recoveryToken,
                        color = MaterialTheme.colorScheme.primary,
                        fontSize = 24.sp,
                        fontFamily = FontFamily.Monospace,
                        modifier = Modifier
                            .fillMaxWidth()
                    )
                } },
            confirmButton = {
                Button(
                    onClick = {
                        viewModel.dismissToken()
                    }
                ) {
                    Text("Got it")
                }
            }
        )
    }
}


@Composable
fun CountdownPie(
    timeLeft: Long,
    maxTime: Long,
    modifier: Modifier = Modifier,
) {
    val color = MaterialTheme.colorScheme.primary

    Canvas(
        modifier = modifier
            .size(48.dp)
            .border(8.dp, MaterialTheme.colorScheme.inversePrimary, CircleShape)
    ) {
        val sweepAngle = 360f * (timeLeft.toFloat() / maxTime.toFloat())
        val center = Offset(size.width / 2, size.height / 2)
        val radius = size.width / 2

        drawArc(
            color = color,
            startAngle = -90f,
            sweepAngle = sweepAngle,
            useCenter = true,
            topLeft = center - Offset(radius, radius),
            size = Size(radius * 2, radius * 2)
        )
    }
}

@Composable
fun TwoFactorCard(data: TwoFactorData) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp),
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                buildAnnotatedString {
                    append(data.username)
                    withStyle(style = SpanStyle(fontStyle = FontStyle.Italic)) { append(" at ") }
                    withStyle(style = SpanStyle(fontWeight = FontWeight.Bold)) { append(data.website) }
                }
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = data.code,
                color = MaterialTheme.colorScheme.primary,
                fontSize = 24.sp,
                fontFamily = FontFamily.Monospace,
                modifier = Modifier
                    .fillMaxWidth()
            )
        }
    }
}
