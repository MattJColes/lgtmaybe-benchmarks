class ReportServiceTest {
  @Test void returnsRows() throws Exception {
    assertNotNull(service.render("alice", List.of("first", "second")));
  }
}
