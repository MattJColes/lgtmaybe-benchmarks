import '../lib/report.dart';

Future<void> main() async {
  final rows = await renderReport('alice', ['first', 'second']);
  if (rows.isEmpty) throw StateError('no rows');
}
