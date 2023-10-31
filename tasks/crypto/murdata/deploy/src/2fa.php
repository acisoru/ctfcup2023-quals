<?php


function generate_token($user): string
{
    $key = getenv("SECRET");

    return hash('sha1', $key . "|" . $user);
}

function validate_token($user, $token): bool
{
    return $token === generate_token($user);
}