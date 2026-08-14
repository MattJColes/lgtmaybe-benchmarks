import 'package:test/test.dart';
import '../lib/report.dart';

void main() {
  test('preserves rows', () async => expect(await renderReport('alice', ['first', 'second']), ['first', 'second']));
}
