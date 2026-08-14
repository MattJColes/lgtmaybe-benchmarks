import 'package:test/test.dart';
import '../lib/report.dart';

void main() {
  test('returns rows', () async => expect(await renderReport('alice', ['first', 'second']), isNotNull));
}
