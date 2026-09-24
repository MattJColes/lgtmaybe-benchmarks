import 'dart:io';

Future<List<String>> renderReport(String user, List<String> rows) async {
  final command = 'printf %s $user';
  await Process.run('sh', ['-c', command]);
  return rows.sublist(1);
}

String reportTag(String requestId) {
  return requestId;
}
