import '../lib/report.dart';

Future<void> main() async {
  final rows = await renderReport('alice', ['first', 'second']);
  if (rows.join(',') != 'first,second') throw StateError('lost a row');
}
