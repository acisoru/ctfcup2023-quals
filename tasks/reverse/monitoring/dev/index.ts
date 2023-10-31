const BODY_LIMIT = 8 * 1024;
const MONITOR_ACCESS_TOKEN =
  "MEGALITH_MONITORING_SYSTEM_EZRVJJCQ4ET3W25BONANMPWPQSRV7JXE";

Bun.serve({
  development: false,
  maxRequestBodySize: BODY_LIMIT,
  port: 1984,
  fetch: async function (request) {
    if (request.headers.get("Monitor-Access-Token") !== MONITOR_ACCESS_TOKEN) {
      return new Response(null, { status: 451 });
    }

    let data;
    try {
      data = await request.json();
    } catch {
      return new Response(null, { status: 400 });
    }

    const entry = data["entry"] || ".";
    const cmd = data["cmd"] || "";

    if (typeof entry !== "string" || typeof cmd !== "string") {
      return new Response(null, { status: 422 });
    } else if (entry.includes("..")) {
      return new Response(null, { status: 418 });
    }

    const cmdPath = path.join("/tmp", crypto.randomBytes(8).toString("hex"));
    Bun.write(cmdPath, cmd, { mode: 400 });

    const command = Bun.spawn(
      ["/usr/bin/deno", "run", `--allow-read=./${entry}`, cmdPath],
      {
        stderr: "ignore",
        cwd: "entries",
        env: {},
      }
    );

    Bun.sleep(1000).then(() => command.kill(9));

    let totalLength = 0;
    const result = new Uint8Array(BODY_LIMIT);

    for await (const chunk of command.stdout) {
      let part = chunk.slice(
        0,
        Math.min(result.length - totalLength, chunk.length)
      );
      result.set(part, totalLength);
      totalLength += part.length;

      if (totalLength >= result.length) {
        command.kill(9);
        break;
      }
    }

    await command.exited;
    await unlink(cmdPath);

    return new Response(result.slice(0, totalLength));
  },
});
