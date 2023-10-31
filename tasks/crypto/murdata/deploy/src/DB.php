<?php

class DB
{
    private $redis;
    private $dataDir;
    public function __construct()
    {
        $this->redis = new Redis([
            'host' => getenv("REDIS_HOST") ?: "localhost",
            'port' => 6379,
            'connectTimeout' => 2.5,
            'backoff' => [
                'algorithm' => Redis::BACKOFF_ALGORITHM_DECORRELATED_JITTER,
                'base' => 500,
                'cap' => 750,
            ],
        ]);
        $this->dataDir = getenv("DATA_DIR") ?: "/tmp/";
    }

    public function userExists($username) {
        return $this->redis->hExists("users", $username);
    }

    private function hashPassword($password) {
        return hash('murmur3f', $password);
    }

    private function compareHashes($hash1, $hash2) {
        error_log("Comparing hashes: " . $hash1 . " " . $hash2);
        error_log("Comparing hashes: " . hexdec($hash1) . " " . hexdec($hash2));
        return hexdec($hash1) === hexdec($hash2);
    }

    public function addUser($username, $password, $passport) {
        $this->redis->hSet("users", $username, $this->hashPassword($password));
        file_put_contents($this->normalizePath($this->dataDir . $username . ".txt"), $passport);
    }

    public function getPassport($username) {
        return file_get_contents($this->normalizePath($this->dataDir . $username . ".txt"));
    }

    public function isValidPassword($username, $password) {
        return $this->compareHashes($this->redis->hGet("users", $username), $this->hashPassword($password));
    }

    private function normalizePath(string $path)
    {
        return array_reduce(explode('/', $path), function($a, $b) {
            if ($a === null) {
                $a = "/";
            }
            if ($b === "" || $b === ".") {
                return $a;
            }
            if ($b === "..") {
                return dirname($a);
            }

            return preg_replace("/\/+/", "/", "$a/$b");
        });
    }

}