<?php

require_once "DB.php";
require_once "2fa.php";

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? "";
    $password = $_POST["password"] ?? "";
    $passport = $_POST["passport"] ?? "";

    if ($username == "" || $password == "" || $passport == "") {
        die("Missing username, password or passport.");
    }
    if (preg_match('/^[a-zA-Z0-9_]+$/m', $username) !== 1) {
        die("Invalid username.");
    }

    $db = new DB();
    if ($db->userExists($username)) {
        die("User already exists");
    }

    $db->addUser($username, $password, $passport);

    $token = generate_token($username);

    echo "<h1>Your token is: <b>'${token}'</b></h1><br>";
    echo "<h3>Save it somewhere safe, you will need it to login.</h3><br>";
    return;
}

?>
<html>
<head>
    <title>MurData - Register</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
<div class="main-block">
    <h2>Register</h2>
    <form method="post" action="">
        <label>
            Username:
            <input type="text" name="username" placeholder="Username">
        </label>
        <label>
            Password:
            <input type="password" name="password" placeholder="Password">
        </label>
        <label>
            Your passport id:
            <input type="text" name="passport" placeholder="1111 2222">
        </label>
        <input type="submit" value="Register">
    </form>

    <p>Already have an account? <a href="/login.php">Login</a></p>
</div>
</body>
</html>

