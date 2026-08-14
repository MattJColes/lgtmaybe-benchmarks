class ReportServiceTest {
  @Test void preservesRows() throws Exception {
    assertEquals(List.of("first", "second"), service.render("alice", List.of("first", "second")));
  }
}
