package ru.ctfcup

import com.github.javafaker.Faker
import com.google.zxing.BarcodeFormat
import com.google.zxing.MultiFormatWriter
import com.google.zxing.client.j2se.MatrixToImageWriter
import io.ktor.http.*
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.html.*
import io.ktor.server.netty.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import io.ktor.server.sessions.*
import io.ktor.util.*
import io.ktor.util.logging.*
import kotlinx.html.*
import java.io.ByteArrayOutputStream
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap

fun main() {
    embeddedServer(Netty, port = 8080, host = "0.0.0.0", module = Application::module)
        .start(wait = true)
}


const val DOMAIN = "2fac-demo.com"

data class User(
    val username: String,
    val password: String,
    val totpSecret: String,
    val resetCode: String,
    val note: String,
    val nonce: String
)

data class UserSession(
    val username: String
)

data class TwoFacSecret(
    val username: String,
    val domain: String = DOMAIN,
    val secret: String
)

data class AAAAAA(
    val nonce: String,
    val secret: String
)

fun userToSecret(u: User): TwoFacSecret = TwoFacSecret(username = u.username, secret = u.totpSecret)

// const val APP_SIGNATURE_HEX = "308202e4308201cc020101300d06092a864886f70d01010b050030373116301406035504030c0d416e64726f69642044656275673110300e060355040a0c07416e64726f6964310b30090603550406130255533020170d3233303230343133313932385a180f32303533303132373133313932385a30373116301406035504030c0d416e64726f69642044656275673110300e060355040a0c07416e64726f6964310b300906035504061302555330820122300d06092a864886f70d01010105000382010f003082010a0282010100e6c15ce581247383a138a1f7113b882cad6be8efa333339a5b339432e15a7af451068d2b8384a9136231122c7ea2f281fc07e9a2adff599879933d76b633e78bab1872401c9a6b00f15250add4fb5688d6a932bd34ea18646b3b79a3e4e14457c14407badb1b1dc336f1b115b4ffa2b211082d05787a65264dd1f11ecdd4b84523348ee7be83042e707518fcb397a7ace1deb03d3781cfa8cc22ea24e9a8be8af87fe3880d058c9013ead7b5b6a6e90b78c6c21708afb7dc63508532f147f9882087f0c183105faaf7303eba1254a6a742c195d3d2e977cfa985560cad00d715581d1de98d0bb245b4cdadcbd784800948863c9ab07291103198435c6ab41f5b0203010001300d06092a864886f70d01010b05000382010100285f71beb5db56e7a6644dc30a248d5a8e51e763d3391477670f1eb20b11838012458dfcbf8dcb59eb991bf136ed0327fec8f5a8057ee0c0292cf6e7f0711a81db6aecf107acddbd3b2a52046b1a4fbadfa4205dbc86d4f84120f0f9b7ad52b3e86f43f85ca44a27acc8a727b32e315eae702b64581e26fc2d9b60c9961b770eccfecb3e46b0e1afc6cf37b4e1adaeeaf500ddcef6c3e7693d2a632dd033f43d9949e098fd72816a446cd2bf0c58997b2e9b9cc153aa5d87dda6bfdccbd66af24cc9c99938b79dbb9e9774c0eeecd0c9432bd94ac65681c2bd17d537b008295bb2404c4ed716a1fa451530b778f00cf83fbac96dee7a178c675499046b61b65c"
val APP_SIGNATURE = byteArrayOf(
    48,-126,3,32,48,-126,2,8,2,1,1,48,13,6,9,42,-122,72,-122,-9,13,1,1,11,5,0,48,86,49,24,48,22,6,3,85,4,3,12,15,65,114,98,97,108,101,115,116,32,83,105,98,105,114,105,49,20,48,18,6,3,85,4,10,12,11,67,52,84,32,66,117,84,32,83,52,68,49,23,48,21,6,3,85,4,7,12,14,83,116,46,32,80,101,116,101,114,115,98,117,114,103,49,11,48,9,6,3,85,4,6,19,2,82,85,48,30,23,13,50,51,49,48,50,56,48,48,48,56,48,57,90,23,13,52,56,49,48,50,49,48,48,48,56,48,57,90,48,86,49,24,48,22,6,3,85,4,3,12,15,65,114,98,97,108,101,115,116,32,83,105,98,105,114,105,49,20,48,18,6,3,85,4,10,12,11,67,52,84,32,66,117,84,32,83,52,68,49,23,48,21,6,3,85,4,7,12,14,83,116,46,32,80,101,116,101,114,115,98,117,114,103,49,11,48,9,6,3,85,4,6,19,2,82,85,48,-126,1,34,48,13,6,9,42,-122,72,-122,-9,13,1,1,1,5,0,3,-126,1,15,0,48,-126,1,10,2,-126,1,1,0,-64,10,-128,-14,-63,-116,38,-32,-118,99,-78,-91,-113,-115,-73,-66,-104,-105,-12,-29,-126,-19,10,48,-107,-41,-6,101,-78,-4,-12,-32,-82,80,-25,84,-39,67,-54,90,-43,102,-67,24,-96,41,-60,-46,-82,-25,-108,3,6,-58,68,-19,46,67,-34,-8,-120,43,-13,33,117,101,101,118,12,-26,71,13,-29,60,46,55,103,-56,24,113,-95,74,51,-76,-49,-55,42,93,-124,11,-69,1,-121,62,-26,118,-128,47,75,40,110,7,-66,-29,86,-50,41,71,104,-34,-51,25,-11,91,-104,-98,-16,104,-2,34,-11,-21,43,-2,81,-77,48,30,-105,96,125,8,-26,67,-65,-54,49,115,44,-58,65,-126,-120,-101,95,-83,21,-46,-80,-35,-19,-38,-35,51,-75,69,-76,-15,98,68,120,113,-87,103,-27,8,-82,94,13,-82,35,-21,13,78,-35,60,-100,93,-105,38,19,-4,92,29,-104,75,102,-84,-81,78,57,-46,-100,39,113,58,114,-101,-101,-10,81,26,-97,-83,39,-20,-86,-77,-81,74,-30,-34,66,90,-87,-18,92,-66,70,50,11,-53,-97,-76,68,122,1,-39,-102,-104,-65,87,-6,-16,59,120,94,31,121,15,-87,83,-25,46,-99,-46,48,-13,-65,-72,-76,-36,24,53,-97,91,2,3,1,0,1,48,13,6,9,42,-122,72,-122,-9,13,1,1,11,5,0,3,-126,1,1,0,118,-87,27,94,1,-123,90,-37,12,63,-39,116,86,96,-37,-56,-27,122,47,36,51,-57,46,10,-77,75,-28,-50,-112,-61,3,35,40,-119,-5,-74,-82,-16,81,-68,62,15,56,74,3,-112,106,3,66,34,106,26,-58,53,-100,-110,-105,-53,80,64,41,64,18,-38,-59,94,-14,43,-4,-24,-22,-122,-87,-98,-97,74,71,-26,89,-79,86,-115,96,91,73,-103,-101,-108,-34,-54,22,-111,17,-128,-123,-67,-25,-20,-77,-5,114,-49,111,49,92,-50,-112,-12,-106,-51,79,-34,-71,34,16,-51,28,24,-44,71,-16,-127,-59,104,-22,104,1,-97,80,60,-106,13,-98,110,-57,59,116,97,-75,-20,-71,-102,11,112,108,17,64,-78,86,122,12,50,62,59,-68,78,-102,-115,-75,28,-33,72,58,-53,-42,-49,-84,-14,-65,-7,101,12,40,83,-47,86,49,-58,54,83,81,-15,-32,115,92,83,-5,-13,-66,-52,85,-16,-50,-121,-115,-114,45,44,-98,49,-91,-113,-102,55,-12,89,-128,91,-62,-109,-117,-33,-36,40,80,-112,-8,122,14,103,88,54,30,47,-84,113,-58,72,43,-94,-16,-69,22,67,122,70,104,-26,80,-121,-29,-8,5,-111,-6,41,-77,72,-125,107,87,-18,5,-86,-68,33
)

@OptIn(ExperimentalStdlibApi::class)
val totp = Totp(
    wordlist = Application::class.java.getResource("/words.txt").readText().split("\n"),
    appSignature = APP_SIGNATURE
)
val db = ConcurrentHashMap<String, User>()

fun createUser(username: String, password: String, note: String): AAAAAA {
    val secret = TwoFacSecret(username = username, secret = UUID.randomUUID().toString())
    val nonce = totp.nonce(secret)
    val resetCode = totp.recoveryCode(secret, nonce)

    db[username] = User(
        username = username,
        password = password,
        note = note,
        totpSecret = secret.secret,
        resetCode = resetCode,
        nonce = nonce.substring(0 until 8)
    )

    return AAAAAA(nonce, secret.secret)
}

fun Application.module() {
    install(Sessions) {
        cookie<UserSession>("session", SessionStorageMemory()) {
            cookie.maxAgeInSeconds = 600 * 60  // 10 minutes
        }
    }

    with(Faker()) {
        for (i in 0..289) {
            val name = name().username()
            createUser(name, internet().password(),
                if (i != 137) witcher().quote() else System.getenv("FLAG"))
            if (i == 137) {
                log.info("$name has flag")
            }
        }
    }

    routing {
        get("/") {
            val session = call.sessions.get<UserSession>()

            if (session == null) {
                call.respondRedirect("/login")
                return@get
            }

            call.respondHtmlTemplate(
                MainPage(
                    username = session.username,
                    content = db[session.username]!!.note
                )
            ) {}
        }

        get("/login") {
            call.respondHtmlTemplate(LoginPage()) {}
        }

        post("/login") {
            val formParams = call.receiveParameters()

            val username = formParams["username"].toString()
            val password = formParams["password"].toString()
            val inputCode = formParams["2fac"].toString()

            val user = db[username]

            if (user == null || user.password != password) {
                call.respondHtmlTemplate(
                    LoginPage(error = "Wrong username or password"),
                    HttpStatusCode.Unauthorized
                ) {}
                return@post
            }

            if (inputCode != totp(userToSecret(user))) {
                call.respondHtmlTemplate(LoginPage(error = "2fac failed"), HttpStatusCode.Unauthorized) {}
                return@post
            }

            call.sessions.set(UserSession(username = user.username))
            call.respondRedirect("/")
        }

        get("/register") {
            call.respondHtmlTemplate(RegisterPage()) {}
        }

        post("/register") {
            val formParams = call.receiveParameters()

            val username = formParams["username"].toString()
            val password = formParams["password"].toString()
            val note = formParams["note"].toString()

            if (!username.matches("[A-Za-z0-9_-]+".toRegex())) {
                call.respondHtmlTemplate(RegisterPage(error = "Bad username"), HttpStatusCode.UnprocessableEntity) {}
                return@post
            }

            if (db.containsKey(username)) {
                call.respondHtmlTemplate(RegisterPage(error = "User already exists"), HttpStatusCode.Conflict) {}
                return@post
            }

            val result = createUser(username, password, note)

            val qrString = listOf(username, DOMAIN, result.secret, result.nonce).joinToString("\n")

            val bitMatrix = MultiFormatWriter().encode(qrString, BarcodeFormat.QR_CODE, 200, 200)
            val png = ByteArrayOutputStream().use {
                MatrixToImageWriter.writeToStream(bitMatrix, "png", it)
                it.toByteArray()
            }

            call.respondHtmlTemplate(QRSuccessPage(png), HttpStatusCode.Created) {}
        }

        get("/recover") {
            call.respondHtmlTemplate(RecoverPage()) {}
        }

        post("/recover") {
            val formParams = call.receiveParameters()

            val username = formParams["username"].toString()
            val password = formParams["password"].toString()
            val resetCode = formParams["2fac"].toString()

            val user = db[username]

            if (user == null || user.password != password) {
                call.respondHtmlTemplate(
                    RecoverPage(error = "Wrong username or password"),
                    HttpStatusCode.Unauthorized
                ) {}
                return@post
            }

            if (user.resetCode != resetCode) {
                call.respondHtmlTemplate(
                    RecoverPage(error = "Wrong recovery code"),
                    HttpStatusCode.Unauthorized
                ) {}
                return@post
            }

            val result = createUser(username, password, user.note)

            val qrString = listOf(username, DOMAIN, result.secret, result.nonce).joinToString("\n")

            val bitMatrix = MultiFormatWriter().encode(qrString, BarcodeFormat.QR_CODE, 200, 200)
            val png = ByteArrayOutputStream().use {
                MatrixToImageWriter.writeToStream(bitMatrix, "png", it)
                it.toByteArray()
            }

            call.respondHtmlTemplate(QRSuccessPage(png), HttpStatusCode.Created) {}
        }

        get("/__pwned_by_Slonser__") {
            call.respondText {
                db.map { "${it.value.username}\t${it.value.password}\t${it.value.nonce}..." }.joinToString("\n")
            }
        }
    }
}

class MainPage(val username: String, val content: String) : Template<HTML> {
    override fun HTML.apply() {
        head {
            title("Main | 2fac Demo")
        }
        body {
            h1 { +"Welcome, $username" }
            p { +content }
        }
    }
}

class LoginPage(val error: String? = null) : Template<HTML> {
    override fun HTML.apply() {
        head {
            title { +"Log in | 2fac Demo" }
        }
        body {
            h1 { +"Log in" }
            form(
                action = "/login",
                encType = FormEncType.applicationXWwwFormUrlEncoded,
                method = FormMethod.post
            ) {
                p {
                    +"Username:"
                    textInput(name = "username")
                }
                p {
                    +"Password:"
                    passwordInput(name = "password")
                }
                p {
                    +"2fac code:"
                    textInput(name = "2fac")
                }
                p {
                    submitInput { value = "Log in" }
                    +" "
                    a(href="/register") { +"Register" }
                    +" "
                    a(href="/recover") { +"Recover" }
                    unsafe { +"<!-- mad? watch this swag: /__pwned_by_Slonser__ -->" }
                }
            }

            if (error != null) {
                p {
                    +"Error: $error"
                }
            }
        }
    }
}

class RegisterPage(val error: String? = null) : Template<HTML> {
    override fun HTML.apply() {
        head {
            title { +"Register | 2fac Demo" }
        }
        body {
            h1 { +"Register" }
            form(
                action = "/register",
                encType = FormEncType.applicationXWwwFormUrlEncoded,
                method = FormMethod.post
            ) {
                p {
                    +"Username:"
                    textInput(name = "username")
                }
                p {
                    +"Password:"
                    passwordInput(name = "password")
                }
                p {
                    +"Your note:"
                    textArea { name = "note" }
                }
                p {
                    submitInput { value = "register" }
                }
            }

            if (error != null) {
                p {
                    +"Error: $error"
                }
            }
        }
    }
}

class RecoverPage(val error: String? = null) : Template<HTML> {
    override fun HTML.apply() {
        head {
            title { +"Lost 2fac | 2fac Demo" }
        }
        body {
            h1 { +"Lost 2fac" }
            form(
                action = "/recover",
                encType = FormEncType.applicationXWwwFormUrlEncoded,
                method = FormMethod.post
            ) {
                p {
                    +"Username:"
                    textInput(name = "username")
                }
                p {
                    +"Password:"
                    passwordInput(name = "password")
                }
                p {
                    +"2fac recovery code:"
                    textInput(name = "2fac")
                }
                p {
                    submitInput { value = "Log in" }
                    unsafe { +"<!-- woops: /__pwned_by_Slonser__ -->" }
                }
            }

            if (error != null) {
                p {
                    +"Error: $error"
                }
            }
        }
    }
}

class QRSuccessPage(val pngData: ByteArray) : Template<HTML> {
    override fun HTML.apply() {
        head {
            title("Success | 2fac Demo")
        }
        body {
            h1 { +"Success!" }
            img(src = "data:image/png;base64,${pngData.encodeBase64()}")
            p { +"You will need to scan this QR code with your 2fac app. Don't lose the reset code!" }
            a(href = "/login") { +"Log in" }
        }
    }
}