<?php

session_start();
if ($_SESSION["IsAdmin"] !== true) {
    http_response_code(401);
    die("Only admins can add new admins.");
}

$username = $_POST['name'] ?? "";
$password = $_POST["password"] ?? "";

$db = new SQLite3('/sql.db');

$q = "INSERT INTO users VALUES ('$username', '$password')";
$db->exec($q);

echo "Added user $username";

