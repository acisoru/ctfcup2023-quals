const NodeRSA = require('node-rsa');
const axios = require('axios');

function restoreMessage(jsonData) {
    const privateKeyData = jsonData.key;
    const encryptedMessage = jsonData.task.c;

    const key = new NodeRSA(privateKeyData, 'pkcs8-private');

    const encryptedBuffer = Buffer.from(encryptedMessage, 'base64');
    const decryptedMessage = key.decrypt(encryptedBuffer, 'utf8');

    return decryptedMessage.split(" ")[2];
}

async function main() {
    const url = process.argv[2];
    if (!url) {
        console.log("Usage: node solve.js https://example.com");
        return;
    }

    const session = axios.create();

    try {
        let lastResponse = await session.get(`${url}/generate-task`);
        for (let i = 0; i < 1337; i++) {
            const ans = restoreMessage(JSON.parse(Buffer.from(lastResponse.headers['set-cookie'][0].split(';')[0].split('=')[1], 'base64').toString()));
            const r = await session.post(`${url}/check-task`, {input: ans}, {
                headers: {
                    'Cookie': lastResponse.headers['set-cookie'],
                    'Content-Type': 'application/json'
                },
                proxy: { host: '127.0.0.1', port: 8080 }
            });

            const s = r.data;
            if (s.flag) {
                console.log(s.flag);
                return;
            }
            lastResponse = r;
        }
    } catch (error) {
        console.error(error);
    }
}

main();
