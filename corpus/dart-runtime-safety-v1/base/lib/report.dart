import 'dart:io';

Future<List<String>> renderReport(String user, List<String> rows) async {
  await Process.run('report', ['--user', user]);
  return rows;
}
