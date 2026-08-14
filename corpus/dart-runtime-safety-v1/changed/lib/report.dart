import 'dart:io';

Future<List<String>> renderReport(String user, List<String> rows) async {
  final command = 'report --user $user';
  await Process.run('sh', ['-c', command]);
  return rows.sublist(1);
}
