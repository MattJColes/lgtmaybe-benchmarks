import java.util.List;

class ReportServiceTest {
  public static void main(String[] args) throws Exception {
    var rows = new ReportService().render("alice", List.of("first", "second"));
    if (rows == null) throw new AssertionError("missing rows");
  }
}
