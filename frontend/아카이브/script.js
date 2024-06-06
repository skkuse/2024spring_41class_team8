const questions = [
    {
        question: "When considering resource consumption, which coding approach is greener?",
        options: {
            A: `Performing frequent disk I/O operations without optimization.
                \ndef read_data(file_path): 
                \n    with open(file_path, 'r') as file: 
                \n        data = file.read() 
                \n    return data`,
            B: `Minimizing disk I/O by optimizing data storage and retrieval processes.
                \ndef read_data_optimized(file_path): 
                \n    cached_data = read_from_cache(file_path) 
                \n    if cached_data: 
                \n        return cached_data 
                \n    else: 
                \n        data = read_data(file_path) 
                \n        store_in_cache(file_path, data) 
                \n        return data`
        },
        answer: "B",
        reason: "Option B minimizes disk I/O operations by first checking for cached data before reading from the file, thus reducing unnecessary disk access and improving overall efficiency."
    },
    {
        question: "When considering resource consumption, which coding approach is greener?",
        options: {
            A: `Performing frequent disk I/O operations without optimization.
                \ndef read_data(file_path): 
                \n    with open(file_path, 'r') as file: 
                \n        data = file.read() 
                \n    return data`,
            B: `Minimizing disk I/O by optimizing data storage and retrieval processes.
                \ndef read_data_optimized(file_path): 
                \n    cached_data = read_from_cache(file_path) 
                \n    if cached_data: 
                \n        return cached_data 
                \n    else: 
                \n        data = read_data(file_path) 
                \n        store_in_cache(file_path, data) 
                \n        return data`
        },
        answer: "B",
        reason: "Option B minimizes disk I/O operations by first checking for cached data before reading from the file, thus reducing unnecessary disk access and improving overall efficiency."
    },
    {
        question: "Which hardware utilization method is more environmentally sustainable?",
        options: {
            A: `Executing tasks sequentially to ensure steady hardware usage.
                \ndef sequential_processing(tasks): 
                \n    for task in tasks: 
                \n        process(task)`,
            B: `Implementing parallel processing techniques to maximize hardware utilization and reduce idle time.
                \nfrom concurrent.futures import ThreadPoolExecutor 
                \ndef parallel_processing(tasks): 
                \n    with ThreadPoolExecutor() as executor: 
                \n        executor.map(process, tasks)`
        },
        answer: "B",
        reason: "Option B utilizes parallel processing techniques, allowing multiple tasks to be executed simultaneously, thus maximizing hardware utilization and reducing overall execution time."
    },
    {
        question: "When it comes to memory management, which coding strategy is greener?",
        options: {
            A: `Option A: Inefficient memory management leading to excessive memory allocations.
def allocate_memory():
    data = []
    for _ in range(1000000):
        data.append(' ' * 1024)
    return data`,
            B: `Option B: Implementing optimized memory allocation strategies to minimize memory wastage.
import numpy as np

def allocate_memory_optimized():
    data = np.empty((1000000, 1024), dtype=np.uint8)
    return data
`
        },
        answer: "B",
        reason: "Option B allocates memory using a single, optimized array, reducing memory overhead and fragmentation compared to Option A, which allocates memory inefficiently by appending to a list."
    },
    {
        question: "Which network efficiency approach is more environmentally responsible?",
        options: {
            A: `Option A: Sending redundant data over the network without compression.
import socket

def send_data(data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('server_ip', 12345))
        s.sendall(data.encode())`,
            B: `Option B: Implementing data compression and efficient transfer protocols to minimize network traffic and energy consumption.
import zlib
import socket

def send_compressed_data(data):
    compressed_data = zlib.compress(data.encode())
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('server_ip', 12345))
        s.sendall(compressed_data)`
        },
        answer: "B",
        reason: "Option B compresses data before sending it over the network, reducing the amount of data transmitted and minimizing network traffic and energy consumption."
    },
    // Add more questions as needed
];


let currentQuestionIndex = 0;
let score = 0;

function displayQuestion() {
    const currentQuestion = questions[currentQuestionIndex];
    document.getElementById('question').innerText = currentQuestion.question;
    document.getElementById('optionA').innerText = currentQuestion.options.A;
    document.getElementById('optionB').innerText = currentQuestion.options.B;
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
