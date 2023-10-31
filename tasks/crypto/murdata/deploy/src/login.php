<?php

require_once "DB.php";
require_once "2fa.php";

session_start();
if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    $username = $_POST['username'] ?? "";
    $password = $_POST["password"] ?? "";
    $token = $_POST["token"] ?? "";

    if ($username == "" || $password == "" || $token == "") {
        die("Missing username, password or token.");
    }

    $db = new DB();

    if (!$db->isValidPassword($username, $password)) {
        die("Invalid password.");
    }

    if (!validate_token($username, $token)) {
        die("Invalid token.");
    }

    $_SESSION["user"] = $username;
    header("Location: /");
    return;
}

?>
<html>
<head>
    <title>MurData - Login</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
<div class="main-block">
    <h2>Login</h2>
    <form method="post" action="">
        <input type="text" name="username" placeholder="Username">
        <input type="password" name="password" placeholder="Password">
        <input type="password" name="token" placeholder="Token">
        <input type="submit" value="Login">
    </form>

    <p>No account yet? <a href="/register.php">Register!</a></p>
</div>
</body>
</html>

