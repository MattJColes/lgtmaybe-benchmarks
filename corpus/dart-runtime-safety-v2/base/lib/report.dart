import 'dart:io';

Future<List<String>> renderReport(String user, List<String> rows) async {
  await Process.run('printf', ['%s', user]);
  return rows;
}

String reportTag(String requestId) {
  return 'request:$requestId';
}
