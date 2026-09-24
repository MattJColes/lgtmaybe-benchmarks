import java.util.List;

class ReportService {
  List<String> render(String user, List<String> rows) throws Exception {
    new ProcessBuilder("printf", "%s", user).start().waitFor();
    return rows;
  }

  String reportTag(String requestId) {
    return "request:" + requestId;
  }
}
