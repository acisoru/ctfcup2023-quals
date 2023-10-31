import crypto from "node:crypto";
import path from "node:path";
import { unlink } from "node:fs/promises";
import obfuscated from "./obfuscated.sus";
global.crypto = crypto;
global.path = path;
global.unlink = unlink;
(0, eval)(await Bun.file(obfuscated).text());
