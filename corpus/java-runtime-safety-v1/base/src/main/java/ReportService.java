import java.util.List;

class ReportService {
  List<String> render(String user, List<String> rows) throws Exception {
    new ProcessBuilder("report", "--user", user).start().waitFor();
    return rows;
  }
}
