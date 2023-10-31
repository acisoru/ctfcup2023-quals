async function generateTask() {
    const response = await fetch('/generate-task');
    const data = await response.json();

    document.getElementById('task').innerHTML = `
        <p>n: ${data.task.n}</p>
        <p>e: ${data.task.e}</p>
        <p>c: ${data.task.c}</p>
    `;
}

async function checkAnswer() {
    const input = document.getElementById('answer').value;

    const response = await fetch('/check-task', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ input })
    });

    const data = await response.json();

    if (data.success) {
        document.getElementById('result').innerHTML = 'Правильно!';
    } else {
        document.getElementById('result').innerHTML = 'Неправильно.';
    }

    document.getElementById('task').innerHTML = `
        <p>n: ${data.task.n}</p>
        <p>e: ${data.task.e}</p>
        <p>c: ${data.task.c}</p>
    `;
}

document.addEventListener('DOMContentLoaded', () => {
    generateTask();
});
