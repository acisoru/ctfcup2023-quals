<?php

require_once "DB.php";

session_start();

$user = $_SESSION["user"] ?? "";
if ($user === "") {
    header("Location: /login.php");
    return;
}



echo <<<HTML
<html lang="en">
<head>
    <title>MurData - Passport</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
<div class="main-block">
HTML;


$db = new DB();
$passport = $db->getPassport($user);

echo "<h3>Welcome ${user}!<br></h3>";
echo "<h4>Your passport id: ${passport}<br></h4>";
?>

</div>
</body>
</html>



