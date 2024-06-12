const questions = [
    {
        question: "Which coding practice is more environmentally friendly?",
        options: {
            A: `Option A:
<pre><code>def brute_force_search(array, target):
    for i in range(len(array)):
        if array[i] == target:
            return i
</code></pre>`,
            B: `Option B:
<pre><code>def brute_force_search(array, target):
    lenofArray = len(array)
    for i in range(lenofArray):
        if array[i] == target:
            return i
</code></pre>`
        },
        answer: "B",
        reason: "Option B is better because it avoids multiple calls to len(array) by storing the length in a variable, making the loop more efficient."
    },
    {
        question: "When considering resource consumption, which coding approach is greener?",
        options: {
            A: `Option A:
<pre><code>def read_data(file_path): 
    with open(file_path, 'r') as file: 
        data = file.read() 
    return data
</code></pre>`,
            B: `Option B:
<pre><code>def read_data_optimized(file_path): 
    cached_data = read_from_cache(file_path) 
    if cached_data: 
        return cached_data 
    else: 
        data = read_data(file_path) 
        store_in_cache(file_path, data) 
        return data
</code></pre>`
        },
        answer: "B",
        reason: "Option B minimizes disk I/O operations by first checking for cached data before reading from the file, thus reducing unnecessary disk access and improving overall efficiency."
    },
    {
        question: "Which hardware utilization method is more environmentally sustainable?",
        options: {
            A: `Option A:
<pre><code>def sequential_processing(tasks): 
    for task in tasks: 
        process(task)
</code></pre>`,
            B: `Option B:
<pre><code>from concurrent.futures import ThreadPoolExecutor 
def parallel_processing(tasks): 
    with ThreadPoolExecutor() as executor: 
        executor.map(process, tasks)
</code></pre>`
        },
        answer: "B",
        reason: "Option B utilizes parallel processing techniques, allowing multiple tasks to be executed simultaneously, thus maximizing hardware utilization and reducing overall execution time."
    },
    {
        question: "When it comes to memory management, which coding strategy is greener?",
        options: {
            A: `Option A:
<pre><code>def allocate_memory():
    data = []
    for _ in range(1000000):
        data.append(' ' * 1024)
    return data
</code></pre>`,
            B: `Option B:
<pre><code>import numpy as np

def allocate_memory_optimized():
    data = np.empty((1000000, 1024), dtype=np.uint8)
    return data
</code></pre>`
        },
        answer: "B",
        reason: "Option B allocates memory using a single, optimized array, reducing memory overhead and fragmentation compared to Option A, which allocates memory inefficiently by appending to a list."
    },
    {
        question: "Which network efficiency approach is more environmentally responsible?",
        options: {
            A: `Option A:
<pre class="small-text"><code>import socket

def send_data(data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('server_ip', 12345))
        s.sendall(data.encode())
</code></pre>`,
            B: `Option B:
<pre class="small-text"><code>import zlib
import socket

def send_compressed_data(data):
    compressed_data = zlib.compress(data.encode())
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('server_ip', 12345))
        s.sendall(compressed_data)
</code></pre>`
        },
        answer: "B",
        reason: "Option B compresses data before sending it over the network, reducing the amount of data transmitted and minimizing network traffic and energy consumption."
    },

];

let currentQuestionIndex = 0;
let score = 0;

function displayQuestion() {
    const currentQuestion = questions[currentQuestionIndex];
    document.getElementById('question').innerHTML = currentQuestion.question;
    document.getElementById('optionA').innerHTML = currentQuestion.options.A;
    document.getElementById('optionB').innerHTML = currentQuestion.options.B;
    clearSelectionStyles();
    hideReasonAndNextButton();
    updateProgressBar();
}

function clearSelectionStyles() {
    document.getElementById('optionA').classList.remove('correct', 'wrong');
    document.getElementById('optionB').classList.remove('correct', 'wrong');
}

function hideReasonAndNextButton() {
    document.getElementById('reason').style.display = 'none';
    document.getElementById('next-button').style.display = 'none';
}

function selectOption(option) {
    const currentQuestion = questions[currentQuestionIndex];
    const selectedButton = document.getElementById(`option${option}`);
    const correctButton = document.getElementById(`option${currentQuestion.answer}`);

    if (option === currentQuestion.answer) {
        selectedButton.classList.add('correct');
        score++;
    } else {
        selectedButton.classList.add('wrong');
        correctButton.classList.add('correct');
    }

    showReasonAndNextButton(currentQuestion.reason);
    disableOptions();
}

function showReasonAndNextButton(reason) {
    document.getElementById('reason').innerText = `Reason: ${reason}`;
    document.getElementById('reason').style.display = 'block';
    document.getElementById('next-button').style.display = 'block';
}

function disableOptions() {
    document.getElementById('optionA').disabled = true;
    document.getElementById('optionB').disabled = true;
}

function nextQuestion() {
    currentQuestionIndex++;
    if (currentQuestionIndex < questions.length) {
        displayQuestion();
    } else {
        showResult();
    }

    enableOptions();
}

function enableOptions() {
    document.getElementById('optionA').disabled = false;
    document.getElementById('optionB').disabled = false;
}

function showResult() {
    document.getElementById('question-container').style.display = 'none';
    document.getElementById('result-container').style.display = 'block';
    document.getElementById('score').innerText = `${score} / ${questions.length}`;
}

function updateProgressBar() {
    const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
    document.getElementById('progress-bar').style.width = `${progress}%`;
}

window.onload = displayQuestion;
