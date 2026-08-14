import java.util.List;

class ReportService {
  List<String> render(String user, List<String> rows) throws Exception {
    Runtime.getRuntime().exec(new String[] {"/bin/sh", "-c", "report --user " + user}).waitFor();
    return rows.subList(1, rows.size());
  }
}
