import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Main {
    public static void main(String[] args) {
        String sourcepath = "src";
        String buggyFilePath = sourcepath + "/Buggy.java";
        String fixedFilePath = sourcepath + "/Fixed.java";

        try {
            // 초기 파일 로드
            String[] codes = readFile(buggyFilePath);
            ArrayList<String> lines = new ArrayList<>(Arrays.asList(codes));

            // 1단계: arraysizeCheck
            String[][] classMethodPairs = {
                {"ArrayList", "size"},
                {"String", "length"},
                {"HashMap", "size"},
                {"HashSet", "size"},
                {"List", "size"}
            };
            if (arraysizeCheck(codes, lines, classMethodPairs)) {
                saveToFile(lines, fixedFilePath);
            } else {
                saveOriginalWithFixedClassName(codes, fixedFilePath);
            }

            codes = readFile(fixedFilePath);
            lines = new ArrayList<>(Arrays.asList(codes));

            // 2단계: repeatlydeclareCheck
            if (repeatlydeclareCheck(codes, lines)) {
                saveToFile(lines, fixedFilePath);
            } else {
                saveOriginalWithFixedClassName(codes, fixedFilePath);
            }

            codes = readFile(fixedFilePath);
            lines = new ArrayList<>(Arrays.asList(codes));

            // 3단계: forwhileCheck
            if (forwhileCheck(codes, lines)) {
                saveToFile(lines, fixedFilePath);
            } else {
                saveOriginalWithFixedClassName(codes, fixedFilePath);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static String[] readFile(String filePath) throws IOException {
        FileReader reader = new FileReader(filePath);
        int ch;
        StringBuilder content = new StringBuilder();
        while ((ch = reader.read()) != -1) {
            content.append((char) ch);
        }
        reader.close();
        return content.toString().split("\n");
    }

    public static void saveToFile(ArrayList<String> lines, String filePath) throws IOException {
        FileWriter fw = new FileWriter(filePath);
        BufferedWriter writer = new BufferedWriter(fw);
        for (String line : lines) {
            writer.write(line + "\n");
        }
        writer.close();
    }

    public static void saveOriginalWithFixedClassName(String[] codes, String filePath) throws IOException {
        ArrayList<String> lines = new ArrayList<>(Arrays.asList(codes));
        for (int i = 0; i < lines.size(); i++) {
            if (lines.get(i).contains("public class Buggy")) {
                lines.set(i, lines.get(i).replace("public class Buggy", "public class Fixed"));
                break;
            }
        }
        saveToFile(lines, filePath);
    }

   public static boolean arraysizeCheck(String[] codes, ArrayList<String> lines, String[][] classMethodPairs) {
    boolean detected = false;
        for (String[] pair : classMethodPairs) {
            boolean isDetected = false;
            int classStartIndex = -1;
            int variableDeclarationLine = -1;
            int methodCallLine = -1;
            String variableName = "";
            String className = pair[0];
            String methodName = pair[1];

            String classPatternStr = "\\b" + className + "(?:<[^>]*>)?\\s+([a-zA-Z0-9_]+)\\s*=";
            Pattern classPattern = Pattern.compile(classPatternStr);

            String methodPatternStr = "\\b([a-zA-Z0-9_]+)\\." + methodName + "\\(\\)";
            Pattern methodPattern = Pattern.compile(methodPatternStr);

            for (int i = 0; i < codes.length; i++) {
                String line = codes[i];
                if (line.contains("public class")) {
                    classStartIndex = i;
                    continue;
                }

                Matcher classMatcher = classPattern.matcher(line);
                if (classMatcher.find()) {
                    variableName = classMatcher.group(1);
                    variableDeclarationLine = i;

                    for (int j = i; j < codes.length; j++) {
                        String line2 = codes[j];
                        Matcher methodMatcher = methodPattern.matcher(line2);
                        if (methodMatcher.find() && methodMatcher.group(1).equals(variableName)) {
                            methodCallLine = j;
                            detected = true;
                            isDetected = true;
                            break;
                        }
                    }
                    if (isDetected) break; // 클래스 선언 이후 첫 번째 감지된 메서드 호출만 처리
                }
            }

            // 수정
            if (isDetected) {
                // for 문 찾기
                int forLineIndex = -1;
                for (int i = methodCallLine; i >= 0; i--) {
                    if (codes[i].contains("for(") || codes[i].contains("for (")) {
                        forLineIndex = i;
                        break;
                    }
                }

                if (forLineIndex != -1) {
                    int count = countLeadingSpaces(lines.get(forLineIndex));
                    if (classStartIndex != -1) {
                        lines.set(classStartIndex, "public class Fixed {");
                    }

                    // 변수 선언을 for 문 바로 위에 위치시킴
                    StringBuilder builder = new StringBuilder();
                    for (int i = 0; i < count; i++) {
                        builder.append(' ');
                    }
                    String newVariableName = variableName + capitalizeFirstLetter(methodName) + "Var";
                    if (!lines.contains("int " + newVariableName + " = " + variableName + "." + methodName + "();")) {
                        builder.append("int " + newVariableName + " = " + variableName + "." + methodName + "();");
                        lines.add(forLineIndex, builder.toString());
                    }

                    lines.set(methodCallLine + 1, lines.get(methodCallLine + 1).replace(variableName + "." + methodName + "()", newVariableName));
                }
            }
            codes = lines.toArray(new String[0]);
        }
        return detected;
    }

    public static boolean repeatlydeclareCheck(String[] codes, ArrayList<String> lines) {
        boolean detected = false;
        int classStartIndex = -1;

        int objectCreationIndex = -1;
        int loopCreationIndex = -1;

        int lineSize = lines.size();

        // find object creation
        for (int i = 0; i < lineSize - 1; i++) {
            String line = codes[i];
            if (line.contains("public class")) {
                classStartIndex = i;
                continue;
            }

            Pattern objectPattern = Pattern.compile("\\b[A-Z]\\w*\\s+[a-z]\\w*\\s*=\\s*new\\s+[A-Z]\\w*\\s*\\(\\s*\\)\\s*;");
            Matcher objectMatcher = objectPattern.matcher(line);
            if (objectMatcher.find()) {
                System.out.println("Object creation detected: " + line);
                objectCreationIndex = i;
                break;
            }
        }

        // find for or while
        for (int i = 0; i < lineSize - 1; i++) {
            String line = codes[i];
            Pattern forPattern = Pattern.compile("\\b(?:for|while)\\s*\\(.*?\\)\\s*\\{");
            Matcher forMatcher = forPattern.matcher(line);
            if (forMatcher.find()) {
                System.out.println("loop detected: " + line);
                loopCreationIndex = i;
                break;
            }
        }

        if (objectCreationIndex != -1 && loopCreationIndex != -1) {
            detected = true;
            if (classStartIndex != -1) {
                lines.set(classStartIndex, "public class Fixed {\n");
            }
            String fixedContent = lines.get(objectCreationIndex);
            lines.set(objectCreationIndex, "##MUSTDELETE##");
            lines.add(loopCreationIndex, fixedContent);
            lines.removeIf(item -> item.equals("##MUSTDELETE##"));
        }
        return detected;
    }

    public static boolean forwhileCheck(String[] codes, ArrayList<String> lines) {
        boolean detected = false;
        int classStartIndex = -1;

        int firstStartIfIndex = -1;
        int firstEndIfIndex = -1;
        int thirdStartIfIndex = -1;
        int thirdEndIfIndex = -1;

        String firstCondition = "";
        String secondCondition = "";
        String thirdCondition = "";

        // 검출
        int lineSize = lines.size();

        // 중첩된 if 문 여부 플래그
        boolean nestedIfFound = false;

        // 조건식 추출 정규식
        Pattern pattern = Pattern.compile("\\((.*?)\\)");

        for (int i = 0; i < lineSize - 1; i++) {
            String line = codes[i];
            if (line.contains("public class")) {
                classStartIndex = i;
                continue;
            }

            if (line.contains("if(")) {
                Matcher matcher1 = pattern.matcher(line);
                firstStartIfIndex = i;

                if (matcher1.find()) {
                    firstCondition = matcher1.group(1);
                }

                // 현재 줄에 중첩된 if 문이 있는지 추가 검사 (3개 중첩인지 검사)
                for (int j = i + 1; j < lineSize - 1; j++) {
                    String line2 = lines.get(j);

                    if (line2.contains("if(")) {
                        Matcher matcher2 = pattern.matcher(line2);

                        if (matcher2.find()) {
                            secondCondition = matcher2.group(1);
                        }

                        for (int k = j + 1; k < lineSize - 1; k++) {
                            String line3 = lines.get(k);

                            if (line3.contains("if(")) {
                                nestedIfFound = true;
                                thirdStartIfIndex = k;

                                Matcher matcher3 = pattern.matcher(line3);

                                if (matcher3.find()) {
                                    thirdCondition = matcher3.group(1);
                                }

                                for (int l = k + 1; l < lineSize - 1; l++) {
                                    String line4 = lines.get(l);
                                    if (line4.contains("}")) {
                                        thirdEndIfIndex = l;
                                        break;
                                    }
                                }

                                int count = 0;

                                for (int l = k + 1; l < lineSize - 1; l++) {
                                    String line4 = lines.get(l);

                                    if (line4.contains("}")) {
                                        count++;
                                        if (count == 3) {
                                            firstEndIfIndex = l;
                                            break;
                                        }
                                    }
                                }
                            }
                            if (thirdEndIfIndex != -1) break;
                        }
                    }
                    if (thirdEndIfIndex != -1) break;
                }
                // 중첩된 if 문이 발견되면 반복문 종료
                if (nestedIfFound) {
                    detected = true;
                    break;
                }
            }
        }

        // 수정
        if (nestedIfFound) {
            lines.set(classStartIndex, "public class Fixed {\n");
            String conditionBody = "";
            for (int i = thirdStartIfIndex + 1; i < thirdEndIfIndex; i++) {
                conditionBody += lines.get(i) + "\n";
            }

            System.out.println("주어진 Java 파일에 중첩된 if 문이 있습니다." + firstStartIfIndex + ", " + firstEndIfIndex);

            for (int i = firstStartIfIndex; i <= firstEndIfIndex; i++) {
                lines.set(i, "##MUSTDELETE##");
            }

            String combinedCondition = "(" + firstCondition + " && " + secondCondition + ") && " + thirdCondition;
            lines.set(firstStartIfIndex - 1, "\t\tif(" + combinedCondition + ") {\n");
            lines.add(firstStartIfIndex, "\t\t\t" + conditionBody + "\t\t}\n");

            lines.removeIf(item -> item.equals("##MUSTDELETE##"));
            int realSize = lines.size();
            for (int i = 0; i < realSize; i++) {
                System.out.println(i + " : " + lines.get(i));
            }
        } else {
            System.out.println("주어진 Java 파일에 중첩된 if 문이 없습니다.");
        }
        return detected;
    }

    public static int countLeadingSpaces(String text) {
        int count = 0;
        for (int i = 0; i < text.length(); i++) {
            if (text.charAt(i) == ' ') {
                count++;
            } else {
                break;
            }
        }
        return count;
    }

    public static String capitalizeFirstLetter(String str) {
        if (str == null || str.length() == 0) {
            return str;
        }
        return str.substring(0, 1).toUpperCase() + str.substring(1);
    }
}
