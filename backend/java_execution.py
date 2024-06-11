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

def add_execution_time_and_memory_measurement(java_code: str) -> str:
    # 실행 시간과 메모리 측정 코드를 추가합니다.
    lines = java_code.split('\n')
    main_method_start = None
    brace_count = 0

    for i, line in enumerate(lines):
        if 'public static void main' in line:
            main_method_start = i
            brace_count = 1
            break
    
    if main_method_start is None:
        raise ValueError("No main method found in Java code")

    # main 메서드 시작 지점에 시간 및 메모리 측정 코드 추가
    lines.insert(main_method_start + 1, '        long startTime = System.nanoTime();')
    lines.insert(main_method_start + 2, '        Runtime runtime = Runtime.getRuntime();')
    lines.insert(main_method_start + 3, '        runtime.gc();')
    lines.insert(main_method_start + 4, '        long beforeUsedMem = Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory();')
    
    # main 메서드 끝 지점에 시간 및 메모리 측정 코드 추가
    for i in range(main_method_start + 1, len(lines)):
        brace_count += lines[i].count('{')
        brace_count -= lines[i].count('}')
        
        if brace_count == 0:
            lines.insert(i, '        long endTime = System.nanoTime();')
            lines.insert(i + 1, '        long afterUsedMem = Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory();')
            lines.insert(i + 2, '        double executionTimeInSeconds = (endTime - startTime) / 1_000_000_000.0;')
            lines.insert(i + 3, '        long memoryUsed = afterUsedMem - beforeUsedMem;')
            lines.insert(i + 4, '        System.out.println("Execution time: " + executionTimeInSeconds + " seconds");')
            lines.insert(i + 5, '        System.out.println("Memory used: " + (memoryUsed / (1024 * 1024)) + " MB");')
            break

    return '\n'.join(lines)

def compile_and_run_java_code(java_code: str):
    # Java 코드에서 클래스 이름 추출
    class_name = extract_class_name(java_code)
    
    # 실행 시간 및 메모리 측정 코드 추가
    modified_java_code = add_execution_time_and_memory_measurement(java_code)
    
    # 수정된 Java 코드 저장
    java_file_path = f"{class_name}.java"
    with open(java_file_path, "w") as f:
        f.write(modified_java_code)

    # Java 코드 컴파일
    compile_process = subprocess.run(["javac", java_file_path], capture_output=True, text=True)
    if compile_process.returncode != 0:
        os.remove(java_file_path)
        return {
            "error": f"Compile Error: {compile_process.stderr.strip()}"
        }

    # Java 코드 실행 및 실행 시간 측정
    run_process = subprocess.Popen(["java", class_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    stdout, stderr = run_process.communicate()

    if run_process.returncode != 0:
        os.remove(java_file_path)
        os.remove(f"{class_name}.class")
        return {
            "error": f"Execution Error: {stderr.decode().strip()}"
        }

    execution_time = None
    memory_used = None
    for line in stdout.decode().split('\n'):
        if "Execution time:" in line:
            execution_time = float(line.split(":")[1].strip().split()[0])
        if "Memory used:" in line:
            memory_used = float(line.split(":")[1].strip().split()[0])

    # 원래 Java 코드로 되돌리기
    with open(java_file_path, "w") as f:
        f.write(java_code)

    return {
        "execution_time": execution_time*1000,
        "memory_usage": memory_used,  # MB 단위
        "stdout": stdout.decode(),
        "stderr": stderr.decode(),
        "class_name": class_name,
        "java_file_path": java_file_path
    }

