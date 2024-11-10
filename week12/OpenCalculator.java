import java.io.IOException;

public class OpenCalculator {
    public static void main(String[] args) {
        try {
            String command = "calc.exe";
            Process process = Runtime.getRuntime().exec(command);
			
        } catch (IOException e) {
            System.err.println(e.getMessage());
        }
    }
}
