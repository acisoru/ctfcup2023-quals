<?php

session_start();
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = [];
    $content_type = $_SERVER["CONTENT_TYPE"];
    $is_json = $content_type == "application/json";
    if ($is_json) {
        $jsonData = file_get_contents('php://input');
        $data = json_decode($jsonData, true);
        if ($data === null) {
            http_response_code(400);
            die("Invalid JSON data.");
        }
    }
    if ($content_type == "application/x-www-form-urlencoded") {
        $data = $_POST;
    }

    $username = $data['name'] ?? "";
    $password = $data["password"] ?? "";
    if ($username === "" || $password === "") {
        http_response_code(412);
        die("Missing name or password.");
    }

    $db = new SQLite3('/sql.db');
    $val = $db->querySingle("SELECT * FROM users WHERE name = '$username' AND password = '$password'");
    if ($val == null) {
        http_response_code(401);
        die("Invalid credentials.");
    }

    $_SESSION["IsAdmin"] = true;
    if ($is_json) {
        header('Content-Type: application/json');
        echo json_encode(["user" => $username]);
    } else {
        header("Location: /admin");
    }
}
