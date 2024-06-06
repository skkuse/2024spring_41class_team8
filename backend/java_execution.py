import os
import re
import subprocess
import time
import psutil
import threading

def extract_class_name(java_code: str) -> str:
    match = re.search(r'\bpublic\s+class\s+(\w+)', java_code)
    if match:
        return match.group(1)
    else:
        raise ValueError("No public class found in Java code")

def monitor_memory_usage(proc, interval=0.1):
    mem_usage = []
    try:
        while proc.is_running():
            mem_info = proc.memory_info()
            mem_usage.append(mem_info.rss)  # RSS (Resident Set Size) 메모리 사용량
            time.sleep(interval)
    except psutil.NoSuchProcess:
        pass
    return mem_usage

def compile_and_run_java_code(java_code: str):
    # Java 코드에서 클래스 이름 추출
    class_name = extract_class_name(java_code)
    
    # Java 코드 저장
    java_file_path = f"{class_name}.java"
    with open(java_file_path, "w") as f:
        f.write(java_code)

    # Java 코드 컴파일
    compile_process = subprocess.run(["javac", java_file_path], capture_output=True, text=True)
    if compile_process.returncode != 0:
        os.remove(java_file_path)
        return {"error": compile_process.stderr, "class_name": class_name, "java_file_path": java_file_path}

    # Java 코드 실행 및 실행 시간 측정
    start_time = time.time()
    run_process = subprocess.Popen(["java", class_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # 메모리 사용량 모니터링
    proc = psutil.Process(run_process.pid)
    mem_thread = threading.Thread(target=monitor_memory_usage, args=(proc,))
    mem_thread.start()

    stdout, stderr = run_process.communicate()
    end_time = time.time()
    mem_thread.join()

    if run_process.returncode != 0:
        os.remove(java_file_path)
        os.remove(f"{class_name}.class")
        return {"error": stderr.decode(), "class_name": class_name, "java_file_path": java_file_path}

    execution_time = end_time - start_time
    memory_usage = max(monitor_memory_usage(proc)) if monitor_memory_usage(proc) else 0

    return {
        "execution_time": execution_time,
        "memory_usage": memory_usage,
        "stdout": stdout.decode(),
        "stderr": stderr.decode(),
        "class_name": class_name,
        "java_file_path": java_file_path
    }