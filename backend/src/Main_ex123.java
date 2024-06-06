import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Main {
    public static void main(String[] args) {
        String sourcepath = "C:/Users/ASUS/Desktop/Software";
        String buggyFilePath = sourcepath + "/Buggy.java"; // "./src/Buggy.java"
        String fixedFilePath = sourcepath + "/Fixed.java"; // "./src/Fixed.java"

        try {
            FileReader reader = new FileReader(buggyFilePath);

            int ch;
            StringBuilder content = new StringBuilder();
            while ((ch = reader.read()) != -1) {
                content.append((char) ch);

            }

            // 코드 분할
            String[] codes = content.toString().split("\n");
            ArrayList<String> lines = new ArrayList<>(Arrays.asList(codes));

            forwhileCheck(codes, lines);
            arraysizeCheck(codes, lines);
            repeatlydeclareCheck(codes, lines);

            FileWriter fw = new FileWriter(fixedFilePath);
            BufferedWriter writer = new BufferedWriter(fw);
            lines.forEach(item -> {
                try {
                    writer.write(item + "\n");
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            });
            writer.close();

        } catch(Exception e) {
            System.out.println(e);
        }
    }

    public static void arraysizeCheck(String[] codes, ArrayList<String> lines) {
        boolean isDetected = false;
        int classStartIndex = 0;
        
        // 검출
        int buggyLine = -1;
        String arrayListVariableName = "";
        int lineSize = lines.size();

        for(int i=0; i<lineSize; i++) {
            String line = codes[i];
            if(line.contains("public class Buggy")) {
                classStartIndex = i;
                continue;
            }

            Pattern pattern = Pattern.compile("\\bArrayList\\s*<[^>]*>\\s+([a-zA-Z0-9_]+)\\s*=");

            Matcher matcher = pattern.matcher(line);
            if (matcher.find()) {
                arrayListVariableName = matcher.group(1);

                for(int j=i; j<codes.length; j++) {
                    String line2 = codes[j];
                    Pattern sizeMethodPattern = Pattern.compile("\\b" + arrayListVariableName + "\\.size\\(\\)");

                    Matcher sizeMethodMatcher = sizeMethodPattern.matcher(line2);
                    if (sizeMethodMatcher.find()) {
//                            System.out.println("ArrayList 객체 변수명: " + arrayListVariableName);
//                            System.out.println("해당 변수를 사용하여 size() 메서드를 호출함");
                        buggyLine = j;
                        isDetected = true;
                        break;
                    }
                }
            }
        }

        // 수정
        if(isDetected) {
            int count = countLeadingSpaces(lines.get(buggyLine));
            lines.set(classStartIndex, "public class Fixed {");

            lines.set(buggyLine, lines.get(buggyLine).replace(arrayListVariableName + ".size()", arrayListVariableName + "Size"));

            StringBuilder builder = new StringBuilder();
            for(int i=0; i<count; i++) {
                builder.append(' ');
            }
            builder.append("int " + arrayListVariableName + "Size = " + arrayListVariableName + ".size();\n");
            lines.add(buggyLine, builder.toString());
        }
    }

    public static void forwhileCheck(String[] codes, ArrayList<String> lines) {
        boolean isDetected = false;
        int classStartIndex = 0;
        
        int firstStartIfIndex = 0;
        int firstEndIfIndex = 0;
        int thirdStartIfIndex = 0;
        int thirdEndIfIndex = 0;

        String firstCondition = "";
        String secondCondition = "";
        String thirdCondition = "";

        // 검출
        int lineSize = lines.size();

        // 중첩된 if 문 여부 플래그
        boolean nestedIfFound = false;

        // 조건식 추출 정규식
        Pattern pattern = Pattern.compile("\\((.*?)\\)");

        for(int i=0; i<lineSize; i++) {
            String line = codes[i];
            if (line.contains("public class Buggy")) {
                classStartIndex = i;
                continue;
            }


            if (line.contains("if(")) {
                Matcher matcher1 = pattern.matcher(line);
                firstStartIfIndex = i;

                if(matcher1.find()) {
                    firstCondition = matcher1.group(1);
                }


                // 현재 줄에 중첩된 if 문이 있는지 추가 검사 (3개 중첩인지 검사)
                for (int j = i+1; j < lineSize; j++) {
                    String line2 = lines.get(j);

                    if(line2.contains("if(")) {

                        Matcher matcher2 = pattern.matcher(line2);

                        if(matcher2.find()) {
                            secondCondition = matcher2.group(1);
                        }


                        for(int k = j+1; k < lineSize; k++) {
                            String line3 = lines.get(k);

                            if(line3.contains("if(")) {
                                nestedIfFound = true;
                                thirdStartIfIndex = k;

                                Matcher matcher3 = pattern.matcher(line3);

                                if(matcher3.find()) {
                                    thirdCondition = matcher3.group(1);
                                }


                                for(int l = k+1; l < lineSize; l++) {
                                    String line4 = lines.get(l);
                                    if(line4.contains("}")) {
                                        thirdEndIfIndex = l;
                                        break;
                                    }
                                }

                                int count = 0;

                                for(int l = k+1; l < lineSize; l++) {
                                    String line4 = lines.get(l);

                                    if(line4.contains("}")) {
                                        count++;
                                        if(count==3) {
                                            firstEndIfIndex = l;
                                            break;
                                        }
                                    }
                                }
                            }
                            if(thirdEndIfIndex != 0) break;
                        }
                    }
                    if(thirdEndIfIndex != 0) break;
                }
                // 중첩된 if 문이 발견되면 반복문 종료
                if (nestedIfFound) {
                    break;
                }
            }
        }


        // 수정
        if (nestedIfFound) {
            lines.set(classStartIndex, "public class Fixed {\n");
            String conditionBody = "";
            for(int i=thirdStartIfIndex+1; i<thirdEndIfIndex; i++) {
                conditionBody = conditionBody + (lines.get(i) + "\n");
            }
//
//
//
//
            System.out.println("주어진 Java 파일에 중첩된 if 문이 있습니다." + firstStartIfIndex + ", " + firstEndIfIndex);

//                int until = firstEndIfIndex - firstStartIfIndex;
            for(int i=firstStartIfIndex; i<=firstEndIfIndex; i++) {
                lines.set(i, "##MUSTDELETE##");
            }
////
////
////
            lines.set(firstStartIfIndex-1, "\t\tif((" + firstCondition + " && " + secondCondition + ") && " + thirdCondition + ") {\n");
            lines.add(firstStartIfIndex, "\t\t\t" + conditionBody + "\n");
            lines.add(firstStartIfIndex+1, "\t\t}\n");

            lines.removeIf(item -> item.equals("##MUSTDELETE##"));
            int realSize = lines.size();
            for(int i=0; i<realSize; i++) {
                System.out.println(i + " : " + lines.get(i));
            }
        } else {
            System.out.println("주어진 Java 파일에 중첩된 if 문이 없습니다.");
        }
    }

    public static void repeatlydeclareCheck(String[] codes, ArrayList<String> lines) {
        boolean isDetected = false;
        int classStartIndex = 0;

        int objectCreationIndex = 0;
        int loopCreationIndex = 0;

        int lineSize = lines.size();

        // find object creation
        for(int i=0; i<lineSize; i++) {
            String line = codes[i];
            if (line.contains("public class Buggy")) {
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
        for(int i=0; i<lineSize; i++) {
            String line = codes[i];

            Pattern forPattern = Pattern.compile("\\b(?:for|while)\\s*\\(.*?\\)\\s*\\{");
            Matcher forMatcher = forPattern.matcher(line);
            if (forMatcher.find()) {
                System.out.println("loop detected: " + line);
                loopCreationIndex = i;
                break;
            }
        }

        if(objectCreationIndex != 0) {
            lines.set(classStartIndex, "public class Fixed {\n");
            String fixedContent = lines.get(objectCreationIndex);

            lines.set(objectCreationIndex, "##MUSTDELETE##");
            lines.add(loopCreationIndex, fixedContent);

            lines.removeIf(item -> item.equals("##MUSTDELETE##"));
        }
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
}
