import os
from java_execution import compile_and_run_java_code

# buggy.java 파일이 있는지 확인하고, 없으면 샘플 Java 코드를 생성합니다.
java_code_sample = """
public class Buggy {
    public static void main(String[] args) {
        // 실행할 코드
        for (int i = 0; i < 1000000; i++) {
            // 예제 코드
        }
    }
}
"""

if not os.path.exists("buggy.java"):
    with open("buggy.java", "w") as f:
        f.write(java_code_sample)

# buggy.java 파일 내용을 읽어옵니다.
with open("buggy.java", "r") as file:
    java_code = file.read()

# 위에서 작성한 compile_and_run_java_code 함수를 임포트합니다.
# 예: from your_module import compile_and_run_java_code

# 여기서 실제 함수를 호출합니다.
result = compile_and_run_java_code(java_code)

# 결과 출력
print(result)

# 메모리 사용량을 MB 단위로 변환하여 출력
memory_usage_mb = result['memory_usage']
print(f"Memory usage: {memory_usage_mb} MB")
