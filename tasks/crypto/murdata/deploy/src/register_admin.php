<?php

require_once "DB.php";

$db = new DB();
$db->addUser("admin", getenv("ADMIN_PASSWORD"), getenv("FLAG"));

