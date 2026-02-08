import 'package:flutter_test/flutter_test.dart';
import 'package:pohualli_desktop/main.dart';

void main() {
  testWidgets('renders app title', (WidgetTester tester) async {
    await tester.pumpWidget(const PohualliDesktopApp(autoConnectBridge: false));
    expect(find.text('Pohualli Desktop (Flutter + RPC)'), findsOneWidget);
  });
}
