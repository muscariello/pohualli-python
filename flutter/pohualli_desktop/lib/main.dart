import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';

void main() {
  runApp(const PohualliDesktopApp());
}

class PohualliDesktopApp extends StatelessWidget {
  const PohualliDesktopApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Pohualli Desktop',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFFB35C00)),
        useMaterial3: true,
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final TextEditingController _convertJdnController = TextEditingController(text: '2451545');
  final TextEditingController _convertNewEraController = TextEditingController();
  String _convertCulture = 'maya';

  final TextEditingController _deriveJdnController = TextEditingController(text: '2451545');
  final TextEditingController _deriveTzolkinController = TextEditingController();
  final TextEditingController _deriveHaabController = TextEditingController();
  final TextEditingController _deriveGController = TextEditingController();
  final TextEditingController _deriveLongCountController = TextEditingController();

  final TextEditingController _rangeStartController = TextEditingController(text: '2451545');
  final TextEditingController _rangeEndController = TextEditingController(text: '2451600');
  final TextEditingController _rangeLimitController = TextEditingController(text: '10');
  final TextEditingController _rangeTzolkinValueController = TextEditingController();
  final TextEditingController _rangeTzolkinNameController = TextEditingController();

  RpcBridge? _rpc;
  String _status = 'Disconnected';
  String _result = '';
  bool _busy = false;

  @override
  void dispose() {
    _convertJdnController.dispose();
    _convertNewEraController.dispose();
    _deriveJdnController.dispose();
    _deriveTzolkinController.dispose();
    _deriveHaabController.dispose();
    _deriveGController.dispose();
    _deriveLongCountController.dispose();
    _rangeStartController.dispose();
    _rangeEndController.dispose();
    _rangeLimitController.dispose();
    _rangeTzolkinValueController.dispose();
    _rangeTzolkinNameController.dispose();
    _rpc?.close();
    super.dispose();
  }

  Future<void> _startBridge() async {
    setState(() {
      _busy = true;
      _status = 'Starting bridge...';
    });
    try {
      final bridge = await RpcBridge.start();
      final health = await bridge.call('health', {});
      setState(() {
        _rpc = bridge;
        _status = 'Connected (${health['status']})';
      });
    } catch (e) {
      setState(() {
        _status = 'Failed to start bridge: $e';
      });
    } finally {
      setState(() {
        _busy = false;
      });
    }
  }

  Future<void> _convert() async {
    if (_rpc == null) {
      setState(() {
        _status = 'Bridge is not running';
      });
      return;
    }
    final jdn = _requiredInt(_convertJdnController.text, field: 'Convert JDN');
    if (jdn == null) {
      return;
    }
    final newEra = _optionalInt(_convertNewEraController.text, field: 'New Era');
    if (_convertNewEraController.text.trim().isNotEmpty && newEra == null) {
      return;
    }
    setState(() {
      _busy = true;
      _status = 'Converting...';
    });
    try {
      final params = <String, dynamic>{'jdn': jdn, 'culture': _convertCulture};
      if (newEra != null) {
        params['new_era'] = newEra;
      }
      final response = await _rpc!.call('convert', params);
      final composite = response['composite'] as Map<String, dynamic>;
      setState(() {
        _status = 'Converted';
        _result = const JsonEncoder.withIndent('  ').convert(composite);
      });
    } catch (e) {
      setState(() {
        _status = 'Convert failed: $e';
      });
    } finally {
      setState(() {
        _busy = false;
      });
    }
  }

  Future<void> _deriveAutoCorr() async {
    if (_rpc == null) {
      setState(() {
        _status = 'Bridge is not running';
      });
      return;
    }
    final jdn = _requiredInt(_deriveJdnController.text, field: 'Derive JDN');
    if (jdn == null) {
      return;
    }
    final g = _optionalInt(_deriveGController.text, field: 'g');
    if (_deriveGController.text.trim().isNotEmpty && g == null) {
      return;
    }
    final params = <String, dynamic>{'jdn': jdn};
    _putIfNotEmpty(params, 'tzolkin', _deriveTzolkinController.text);
    _putIfNotEmpty(params, 'haab', _deriveHaabController.text);
    _putIfNotEmpty(params, 'long_count', _deriveLongCountController.text);
    if (g != null) {
      params['g'] = g;
    }

    setState(() {
      _busy = true;
      _status = 'Deriving autocorr...';
    });
    try {
      final response = await _rpc!.call('derive_autocorr', params);
      setState(() {
        _status = 'Auto-corrections derived';
        _result = const JsonEncoder.withIndent('  ').convert(response['autocorr']);
      });
    } catch (e) {
      setState(() {
        _status = 'Derive failed: $e';
      });
    } finally {
      setState(() {
        _busy = false;
      });
    }
  }

  Future<void> _searchRange() async {
    if (_rpc == null) {
      setState(() {
        _status = 'Bridge is not running';
      });
      return;
    }
    final start = _requiredInt(_rangeStartController.text, field: 'Range start');
    final end = _requiredInt(_rangeEndController.text, field: 'Range end');
    if (start == null || end == null) {
      return;
    }
    final limit = _optionalInt(_rangeLimitController.text, field: 'Range limit');
    if (_rangeLimitController.text.trim().isNotEmpty && limit == null) {
      return;
    }
    final tzValue = _optionalInt(_rangeTzolkinValueController.text, field: 'Tzolkin value');
    if (_rangeTzolkinValueController.text.trim().isNotEmpty && tzValue == null) {
      return;
    }
    final params = <String, dynamic>{'start': start, 'end': end};
    if (limit != null) {
      params['limit'] = limit;
    }
    if (tzValue != null) {
      params['tzolkin_value'] = tzValue;
    }
    _putIfNotEmpty(params, 'tzolkin_name', _rangeTzolkinNameController.text);

    setState(() {
      _busy = true;
      _status = 'Searching range...';
    });
    try {
      final response = await _rpc!.call('search_range', params);
      setState(() {
        _status = 'Range search complete';
        _result = const JsonEncoder.withIndent('  ').convert(response);
      });
    } catch (e) {
      setState(() {
        _status = 'Range search failed: $e';
      });
    } finally {
      setState(() {
        _busy = false;
      });
    }
  }

  Future<void> _listCorrelations() async {
    if (_rpc == null) {
      setState(() {
        _status = 'Bridge is not running';
      });
      return;
    }
    setState(() {
      _busy = true;
      _status = 'Loading correlations...';
    });
    try {
      final response = await _rpc!.call('list_correlations', {});
      setState(() {
        _status = 'Correlation presets loaded';
        _result = const JsonEncoder.withIndent('  ').convert(response);
      });
    } catch (e) {
      setState(() {
        _status = 'List correlations failed: $e';
      });
    } finally {
      setState(() {
        _busy = false;
      });
    }
  }

  int? _requiredInt(String raw, {required String field}) {
    final value = int.tryParse(raw.trim());
    if (value != null) {
      return value;
    }
    setState(() {
      _status = 'Invalid integer for $field';
    });
    return null;
  }

  int? _optionalInt(String raw, {required String field}) {
    final trimmed = raw.trim();
    if (trimmed.isEmpty) {
      return null;
    }
    final value = int.tryParse(trimmed);
    if (value != null) {
      return value;
    }
    setState(() {
      _status = 'Invalid integer for $field';
    });
    return null;
  }

  void _putIfNotEmpty(Map<String, dynamic> params, String key, String value) {
    final trimmed = value.trim();
    if (trimmed.isNotEmpty) {
      params[key] = trimmed;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Pohualli Desktop (Flutter + RPC)')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Wrap(
                spacing: 12,
                runSpacing: 8,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  FilledButton(
                    onPressed: _busy ? null : _startBridge,
                    child: const Text('Start RPC Bridge'),
                  ),
                  OutlinedButton(
                    onPressed: _busy ? null : _listCorrelations,
                    child: const Text('List Correlations'),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              _buildSection(
                title: 'Convert',
                child: Wrap(
                  spacing: 10,
                  runSpacing: 8,
                  children: [
                    _numericField(_convertJdnController, 'JDN', width: 140),
                    SizedBox(
                      width: 130,
                      child: DropdownButtonFormField<String>(
                        initialValue: _convertCulture,
                        isExpanded: true,
                        decoration: const InputDecoration(
                          labelText: 'Culture',
                          border: OutlineInputBorder(),
                        ),
                        items: const [
                          DropdownMenuItem(value: 'maya', child: Text('Maya')),
                          DropdownMenuItem(value: 'aztec', child: Text('Aztec')),
                        ],
                        onChanged: _busy
                            ? null
                            : (value) {
                                if (value == null) {
                                  return;
                                }
                                setState(() {
                                  _convertCulture = value;
                                });
                              },
                      ),
                    ),
                    _numericField(_convertNewEraController, 'New Era (optional)', width: 180),
                    FilledButton.tonal(
                      onPressed: _busy ? null : _convert,
                      child: const Text('Run Convert'),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 8),
              _buildSection(
                title: 'Derive Auto-Corrections',
                child: Wrap(
                  spacing: 10,
                  runSpacing: 8,
                  children: [
                    _numericField(_deriveJdnController, 'JDN', width: 140),
                    _textField(_deriveTzolkinController, 'Tzolkin (opt)', width: 180),
                    _textField(_deriveHaabController, 'Haab (opt)', width: 160),
                    _numericField(_deriveGController, 'g (opt)', width: 120),
                    _textField(_deriveLongCountController, 'Long Count (opt)', width: 210),
                    FilledButton.tonal(
                      onPressed: _busy ? null : _deriveAutoCorr,
                      child: const Text('Run Derive'),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 8),
              _buildSection(
                title: 'Search Range',
                child: Wrap(
                  spacing: 10,
                  runSpacing: 8,
                  children: [
                    _numericField(_rangeStartController, 'Start', width: 130),
                    _numericField(_rangeEndController, 'End', width: 130),
                    _numericField(_rangeLimitController, 'Limit', width: 110),
                    _numericField(_rangeTzolkinValueController, 'Tzolkin Value', width: 150),
                    _textField(_rangeTzolkinNameController, 'Tzolkin Name', width: 160),
                    FilledButton.tonal(
                      onPressed: _busy ? null : _searchRange,
                      child: const Text('Run Search'),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              Text(_status),
              const SizedBox(height: 12),
              SizedBox(
                height: 320,
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF6F3EE),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: SingleChildScrollView(
                    child: SelectableText(
                      _result.isEmpty ? 'No result yet.' : _result,
                      style: const TextStyle(fontFamily: 'monospace'),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSection({required String title, required Widget child}) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: const Color(0xFFF1EEE8),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          child,
        ],
      ),
    );
  }

  Widget _numericField(TextEditingController controller, String label, {double width = 160}) {
    return SizedBox(
      width: width,
      child: TextField(
        controller: controller,
        keyboardType: TextInputType.number,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
      ),
    );
  }

  Widget _textField(TextEditingController controller, String label, {double width = 180}) {
    return SizedBox(
      width: width,
      child: TextField(
        controller: controller,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
      ),
    );
  }
}

class RpcBridge {
  RpcBridge._(this._process) {
    _lineSub = _process.stdout
        .transform(utf8.decoder)
        .transform(const LineSplitter())
        .listen(_onLine, onDone: _onDone, onError: _onStreamError);
    _stderrSub = _process.stderr
        .transform(utf8.decoder)
        .transform(const LineSplitter())
        .listen((line) {
      // Keep stderr consumption to avoid backpressure deadlocks.
      _lastStderr = line;
    });
  }

  final Process _process;
  final Map<int, Completer<Map<String, dynamic>>> _pending = {};
  late final StreamSubscription<String> _lineSub;
  late final StreamSubscription<String> _stderrSub;
  int _nextId = 1;
  String _lastStderr = '';
  bool _closed = false;

  static Future<RpcBridge> start({String executable = 'pohualli-rpc'}) async {
    final resolvedExecutable = _resolveBackendExecutable(executable);
    final process = await Process.start(resolvedExecutable, []);
    return RpcBridge._(process);
  }

  static String _resolveBackendExecutable(String fallbackExecutable) {
    final exePath = Platform.resolvedExecutable;
    final exeDir = File(exePath).parent.path;

    if (Platform.isMacOS) {
      final bundled = '$exeDir/pohualli-rpc-bin';
      if (File(bundled).existsSync()) {
        return bundled;
      }
    }
    if (Platform.isWindows) {
      final bundled = '$exeDir\\pohualli-rpc-bin.exe';
      if (File(bundled).existsSync()) {
        return bundled;
      }
    }

    // Development fallback: use PATH-installed command.
    return fallbackExecutable;
  }

  Future<Map<String, dynamic>> call(String method, Map<String, dynamic> params) {
    if (_closed) {
      return Future.error(StateError('RPC bridge closed'));
    }
    final id = _nextId++;
    final completer = Completer<Map<String, dynamic>>();
    _pending[id] = completer;
    final payload = <String, dynamic>{
      'jsonrpc': '2.0',
      'id': id,
      'method': method,
      'params': params,
    };
    _process.stdin.writeln(jsonEncode(payload));
    return completer.future.timeout(
      const Duration(seconds: 15),
      onTimeout: () {
        _pending.remove(id);
        throw TimeoutException('RPC timeout on method $method');
      },
    );
  }

  Future<void> close() async {
    if (_closed) {
      return;
    }
    try {
      await call('quit', {});
    } catch (_) {
      // Ignore shutdown errors.
    }
    _closed = true;
    await _lineSub.cancel();
    await _stderrSub.cancel();
    _process.kill();
  }

  void _onLine(String line) {
    Map<String, dynamic> msg;
    try {
      msg = jsonDecode(line) as Map<String, dynamic>;
    } catch (_) {
      return;
    }
    final id = msg['id'];
    if (id is! int) {
      return;
    }
    final completer = _pending.remove(id);
    if (completer == null) {
      return;
    }
    if (msg.containsKey('error')) {
      completer.completeError(Exception(msg['error']));
      return;
    }
    completer.complete(msg['result'] as Map<String, dynamic>);
  }

  void _onDone() {
    _failAll(StateError('RPC process exited'));
  }

  void _onStreamError(Object error) {
    _failAll(StateError('RPC stream failed: $error'));
  }

  void _failAll(Object error) {
    if (_lastStderr.isNotEmpty) {
      error = StateError('$error; stderr=$_lastStderr');
    }
    for (final entry in _pending.entries) {
      entry.value.completeError(error);
    }
    _pending.clear();
  }
}
