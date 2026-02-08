import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';

void main() {
  runApp(const PohualliDesktopApp());
}

class PohualliDesktopApp extends StatefulWidget {
  const PohualliDesktopApp({
    super.key,
    this.autoConnectBridge = true,
  });

  final bool autoConnectBridge;

  @override
  State<PohualliDesktopApp> createState() => _PohualliDesktopAppState();
}

class _PohualliDesktopAppState extends State<PohualliDesktopApp> {
  ThemeMode _themeMode = ThemeMode.system;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Pohualli Desktop',
      themeMode: _themeMode,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFFB35C00)),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFFB35C00),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: HomePage(
        autoConnectBridge: widget.autoConnectBridge,
        themeMode: _themeMode,
        onThemeModeChanged: (mode) {
          setState(() {
            _themeMode = mode;
          });
        },
      ),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({
    super.key,
    required this.autoConnectBridge,
    required this.themeMode,
    required this.onThemeModeChanged,
  });

  final bool autoConnectBridge;
  final ThemeMode themeMode;
  final ValueChanged<ThemeMode> onThemeModeChanged;

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final TextEditingController _convertJdnController = TextEditingController(text: '2451545');
  final TextEditingController _convertNewEraController = TextEditingController();
  final TextEditingController _convertYearBearerMonthController = TextEditingController();
  final TextEditingController _convertYearBearerDayController = TextEditingController();
  final TextEditingController _convertTzOffController = TextEditingController();
  final TextEditingController _convertTzNameOffController = TextEditingController();
  final TextEditingController _convertHaabOffController = TextEditingController();
  final TextEditingController _convertGOffController = TextEditingController();
  final TextEditingController _convertLcdOffController = TextEditingController();
  final TextEditingController _convertWeekOffController = TextEditingController();
  final TextEditingController _convertC819StationOffController = TextEditingController();
  final TextEditingController _convertC819DirOffController = TextEditingController();
  String _convertCulture = 'maya';
  String? _convertPreset;
  List<String> _correlationPresets = [];

  final TextEditingController _deriveJdnController = TextEditingController(text: '2451545');
  final TextEditingController _deriveTzolkinController = TextEditingController();
  final TextEditingController _deriveHaabController = TextEditingController();
  final TextEditingController _deriveGController = TextEditingController();
  final TextEditingController _deriveLongCountController = TextEditingController();

  final TextEditingController _rangeStartController = TextEditingController(text: '2451545');
  final TextEditingController _rangeEndController = TextEditingController(text: '2451600');
  final TextEditingController _rangeLimitController = TextEditingController(text: '10');
  final TextEditingController _rangeStepController = TextEditingController(text: '1');
  final TextEditingController _rangeTzolkinValueController = TextEditingController();
  final TextEditingController _rangeTzolkinNameController = TextEditingController();
  final TextEditingController _rangeHaabDayController = TextEditingController();
  final TextEditingController _rangeHaabMonthController = TextEditingController();
  final TextEditingController _rangeYearBearerNameController = TextEditingController();
  final TextEditingController _rangeDirColorController = TextEditingController();
  final TextEditingController _rangeWeekdayController = TextEditingController();
  final TextEditingController _rangeLongCountController = TextEditingController();
  final TextEditingController _rangeFieldsController = TextEditingController();

  RpcBridge? _rpc;
  String _status = 'Disconnected';
  bool _busy = false;
  bool _showJson = false;
  String _jsonResult = '';
  String _lastMethod = '';
  Map<String, dynamic>? _lastResult;

  @override
  void initState() {
    super.initState();
    if (widget.autoConnectBridge) {
      // Keep the bridge up by default; users should not need to manage connection state.
      Future<void>.microtask(_startBridge);
    }
  }

  @override
  void dispose() {
    _convertJdnController.dispose();
    _convertNewEraController.dispose();
    _convertYearBearerMonthController.dispose();
    _convertYearBearerDayController.dispose();
    _convertTzOffController.dispose();
    _convertTzNameOffController.dispose();
    _convertHaabOffController.dispose();
    _convertGOffController.dispose();
    _convertLcdOffController.dispose();
    _convertWeekOffController.dispose();
    _convertC819StationOffController.dispose();
    _convertC819DirOffController.dispose();
    _deriveJdnController.dispose();
    _deriveTzolkinController.dispose();
    _deriveHaabController.dispose();
    _deriveGController.dispose();
    _deriveLongCountController.dispose();
    _rangeStartController.dispose();
    _rangeEndController.dispose();
    _rangeLimitController.dispose();
    _rangeStepController.dispose();
    _rangeTzolkinValueController.dispose();
    _rangeTzolkinNameController.dispose();
    _rangeHaabDayController.dispose();
    _rangeHaabMonthController.dispose();
    _rangeYearBearerNameController.dispose();
    _rangeDirColorController.dispose();
    _rangeWeekdayController.dispose();
    _rangeLongCountController.dispose();
    _rangeFieldsController.dispose();
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
      await _loadCorrelationsForDropdown();
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
    if (!await _ensureBridge()) {
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
    final ybMonth = _optionalInt(_convertYearBearerMonthController.text, field: 'Year bearer month');
    if (_convertYearBearerMonthController.text.trim().isNotEmpty && ybMonth == null) {
      return;
    }
    final ybDay = _optionalInt(_convertYearBearerDayController.text, field: 'Year bearer day');
    if (_convertYearBearerDayController.text.trim().isNotEmpty && ybDay == null) {
      return;
    }
    if ((ybMonth == null) != (ybDay == null)) {
      setState(() {
        _status = 'Year bearer month and day must both be provided';
      });
      return;
    }

    final corrections = <String, int>{};
    final corrEntries = <String, (TextEditingController, String)>{
      'tzolkin': (_convertTzOffController, 'Tzolkin Offset'),
      'tzolkin_name': (_convertTzNameOffController, 'Tzolkin Name Offset'),
      'haab': (_convertHaabOffController, 'Haab Offset'),
      'g': (_convertGOffController, 'G Offset'),
      'lcd': (_convertLcdOffController, 'LCD Offset'),
      'week': (_convertWeekOffController, 'Week Offset'),
      'c819_station': (_convertC819StationOffController, '819 Station Offset'),
      'c819_dir': (_convertC819DirOffController, '819 Dir/Color Offset'),
    };
    for (final entry in corrEntries.entries) {
      final raw = entry.value.$1.text.trim();
      if (raw.isEmpty) {
        continue;
      }
      final parsed = _optionalInt(raw, field: entry.value.$2);
      if (parsed == null) {
        return;
      }
      corrections[entry.key] = parsed;
    }
    setState(() {
      _busy = true;
      _status = 'Converting...';
    });
    try {
      final params = <String, dynamic>{'jdn': jdn, 'culture': _convertCulture};
      if (_convertPreset != null && _convertPreset!.isNotEmpty) {
        params['preset'] = _convertPreset;
      }
      if (newEra != null) {
        params['new_era'] = newEra;
      }
      if (ybMonth != null && ybDay != null) {
        params['year_bearer_month'] = ybMonth;
        params['year_bearer_day'] = ybDay;
      }
      if (corrections.isNotEmpty) {
        params['corrections'] = corrections;
      }
      final response = await _rpc!.call('convert', params);
      _setResult('convert', response);
      setState(() {
        _status = 'Converted';
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
    if (!await _ensureBridge()) {
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
      _setResult('derive_autocorr', response);
      setState(() {
        _status = 'Auto-corrections derived';
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
    if (!await _ensureBridge()) {
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
    final step = _optionalInt(_rangeStepController.text, field: 'Range step');
    if (_rangeStepController.text.trim().isNotEmpty && step == null) {
      return;
    }
    final tzValue = _optionalInt(_rangeTzolkinValueController.text, field: 'Tzolkin value');
    if (_rangeTzolkinValueController.text.trim().isNotEmpty && tzValue == null) {
      return;
    }
    final haabDay = _optionalInt(_rangeHaabDayController.text, field: 'Haab day');
    if (_rangeHaabDayController.text.trim().isNotEmpty && haabDay == null) {
      return;
    }
    final weekday = _optionalInt(_rangeWeekdayController.text, field: 'Weekday');
    if (_rangeWeekdayController.text.trim().isNotEmpty && weekday == null) {
      return;
    }

    final params = <String, dynamic>{'start': start, 'end': end};
    if (limit != null) {
      params['limit'] = limit;
    }
    if (step != null) {
      params['step'] = step;
    }
    if (tzValue != null) {
      params['tzolkin_value'] = tzValue;
    }
    if (haabDay != null) {
      params['haab_day'] = haabDay;
    }
    if (weekday != null) {
      params['weekday'] = weekday;
    }
    _putIfNotEmpty(params, 'tzolkin_name', _rangeTzolkinNameController.text);
    _putIfNotEmpty(params, 'haab_month', _rangeHaabMonthController.text);
    _putIfNotEmpty(params, 'year_bearer_name', _rangeYearBearerNameController.text);
    _putIfNotEmpty(params, 'dir_color', _rangeDirColorController.text);
    _putIfNotEmpty(params, 'long_count', _rangeLongCountController.text);
    _putIfNotEmpty(params, 'fields', _rangeFieldsController.text);

    setState(() {
      _busy = true;
      _status = 'Searching range...';
    });
    try {
      final response = await _rpc!.call('search_range', params);
      _setResult('search_range', response);
      setState(() {
        _status = 'Range search complete';
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
    if (!await _ensureBridge()) {
      return;
    }
    setState(() {
      _busy = true;
      _status = 'Loading correlations...';
    });
    try {
      final response = await _rpc!.call('list_correlations', {});
      _extractCorrelationPresets(response);
      _setResult('list_correlations', response);
      setState(() {
        _status = 'Correlation presets loaded';
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

  Future<void> _loadCorrelationsForDropdown() async {
    if (_rpc == null) {
      return;
    }
    try {
      final response = await _rpc!.call('list_correlations', {});
      _extractCorrelationPresets(response);
    } catch (_) {
      // Non-fatal; manual list action can still be used.
    }
  }

  void _extractCorrelationPresets(Map<String, dynamic> response) {
    final presets = (response['presets'] as List?)
            ?.whereType<Map>()
            .map((p) => '${p['name'] ?? ''}')
            .where((name) => name.isNotEmpty)
            .toList() ??
        <String>[];
    if (!mounted) {
      return;
    }
    setState(() {
      _correlationPresets = presets;
      if (_convertPreset == null && presets.isNotEmpty) {
        _convertPreset = presets.first;
      }
      if (_convertPreset != null && !_correlationPresets.contains(_convertPreset)) {
        _convertPreset = _correlationPresets.isEmpty ? null : _correlationPresets.first;
      }
    });
  }

  void _setResult(String method, Map<String, dynamic> result) {
    setState(() {
      _lastMethod = method;
      _lastResult = result;
      _jsonResult = const JsonEncoder.withIndent('  ').convert(result);
    });
  }

  Future<bool> _ensureBridge() async {
    if (_rpc != null) {
      return true;
    }
    await _startBridge();
    return _rpc != null;
  }

  Future<void> _downloadJson() async {
    if (_jsonResult.isEmpty) {
      setState(() {
        _status = 'No JSON output available to download';
      });
      return;
    }
    try {
      final downloadDir = _defaultDownloadDirectory();
      if (!downloadDir.existsSync()) {
        downloadDir.createSync(recursive: true);
      }
      final stamp = DateTime.now().toIso8601String().replaceAll(':', '-');
      final method = _lastMethod.isEmpty ? 'result' : _lastMethod;
      final file = File('${downloadDir.path}${Platform.pathSeparator}pohualli-$method-$stamp.json');
      file.writeAsStringSync(_jsonResult);
      setState(() {
        _status = 'Saved JSON to ${file.path}';
      });
    } catch (e) {
      setState(() {
        _status = 'Failed to save JSON: $e';
      });
    }
  }

  Directory _defaultDownloadDirectory() {
    if (Platform.isWindows) {
      final userProfile = Platform.environment['USERPROFILE'];
      if (userProfile != null && userProfile.isNotEmpty) {
        return Directory('$userProfile\\Downloads');
      }
    }
    final home = Platform.environment['HOME'];
    if (home != null && home.isNotEmpty) {
      return Directory('$home/Downloads');
    }
    return Directory.current;
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
      appBar: AppBar(
        title: const Text('Pohualli Desktop (Flutter + RPC)'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<ThemeMode>(
                value: widget.themeMode,
                onChanged: (value) {
                  if (value != null) {
                    widget.onThemeModeChanged(value);
                  }
                },
                items: const [
                  DropdownMenuItem(value: ThemeMode.system, child: Text('Theme: System')),
                  DropdownMenuItem(value: ThemeMode.light, child: Text('Theme: Light')),
                  DropdownMenuItem(value: ThemeMode.dark, child: Text('Theme: Dark')),
                ],
              ),
            ),
          ),
        ],
      ),
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
                  OutlinedButton(
                    onPressed: _busy ? null : _listCorrelations,
                    child: const Text('List Correlations'),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              _buildSection(
                title: 'Convert',
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Wrap(
                      spacing: 10,
                      runSpacing: 8,
                      children: [
                        _numericField(_convertJdnController, 'JDN', width: 140),
                        SizedBox(
                          width: 180,
                          child: DropdownButtonFormField<String>(
                            initialValue: _convertPreset,
                            isExpanded: true,
                            decoration: const InputDecoration(
                              labelText: 'Correlation Preset',
                              border: OutlineInputBorder(),
                            ),
                            items: _correlationPresets
                                .map((preset) => DropdownMenuItem(value: preset, child: Text(preset)))
                                .toList(),
                            onChanged: _busy
                                ? null
                                : (value) {
                                    setState(() {
                                      _convertPreset = value;
                                    });
                                  },
                          ),
                        ),
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
                        _numericField(_convertNewEraController, 'New Era (optional)', width: 170),
                        _numericField(_convertYearBearerMonthController, 'YB Month (opt)', width: 130),
                        _numericField(_convertYearBearerDayController, 'YB Day (opt)', width: 120),
                        FilledButton.tonal(
                          onPressed: _busy ? null : _convert,
                          child: const Text('Run Convert'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    ExpansionTile(
                      title: const Text('Advanced Corrections'),
                      children: [
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: [
                            _numericField(_convertTzOffController, 'Tz Off', width: 110),
                            _numericField(_convertTzNameOffController, 'Tz Name Off', width: 120),
                            _numericField(_convertHaabOffController, 'Haab Off', width: 110),
                            _numericField(_convertGOffController, 'G Off', width: 100),
                            _numericField(_convertLcdOffController, 'LCD Off', width: 110),
                            _numericField(_convertWeekOffController, 'Week Off', width: 110),
                            _numericField(_convertC819StationOffController, '819 St Off', width: 110),
                            _numericField(_convertC819DirOffController, '819 Dir Off', width: 120),
                          ],
                        ),
                        const SizedBox(height: 8),
                      ],
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
                    _numericField(_rangeStepController, 'Step', width: 100),
                    _numericField(_rangeLimitController, 'Limit', width: 110),
                    _numericField(_rangeTzolkinValueController, 'Tzolkin Value', width: 150),
                    _textField(_rangeTzolkinNameController, 'Tzolkin Name', width: 160),
                    _numericField(_rangeHaabDayController, 'Haab Day', width: 120),
                    _textField(_rangeHaabMonthController, 'Haab Month', width: 140),
                    _textField(_rangeYearBearerNameController, 'Year Bearer', width: 140),
                    _textField(_rangeDirColorController, 'Dir/Color', width: 140),
                    _numericField(_rangeWeekdayController, 'Weekday', width: 110),
                    _textField(_rangeLongCountController, 'Long Count', width: 200),
                    _textField(_rangeFieldsController, 'Fields (csv)', width: 220),
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
              _buildResultPanel(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildResultPanel() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.45),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                _lastMethod.isEmpty ? 'Results' : 'Results: ${_prettyMethod(_lastMethod)}',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const Spacer(),
              FilterChip(
                selected: _showJson,
                onSelected: (selected) {
                  setState(() {
                    _showJson = selected;
                  });
                },
                label: const Text('Show JSON'),
              ),
              const SizedBox(width: 8),
              OutlinedButton.icon(
                onPressed: _jsonResult.isEmpty ? null : _downloadJson,
                icon: const Icon(Icons.download),
                label: const Text('Download JSON'),
              ),
            ],
          ),
          const SizedBox(height: 10),
          SizedBox(
            height: 340,
            child: _buildResultBody(),
          ),
        ],
      ),
    );
  }

  Widget _buildResultBody() {
    if (_lastResult == null) {
      return const Center(child: Text('No result yet.'));
    }
    if (_showJson) {
      return SingleChildScrollView(
        child: SelectableText(
          _jsonResult,
          style: const TextStyle(fontFamily: 'monospace'),
        ),
      );
    }

    switch (_lastMethod) {
      case 'convert':
        return _buildConvertResult(_lastResult!);
      case 'derive_autocorr':
        return _buildDeriveResult(_lastResult!);
      case 'search_range':
        return _buildRangeResult(_lastResult!);
      case 'list_correlations':
        return _buildCorrelationsResult(_lastResult!);
      default:
        return const SingleChildScrollView(
          child: Text('Unsupported result type, switch to JSON view.'),
        );
    }
  }

  Widget _buildConvertResult(Map<String, dynamic> result) {
    final composite = result['composite'];
    if (composite is! Map<String, dynamic>) {
      return const Text('Unexpected convert response format.');
    }

    final items = <MapEntry<String, String>>[
      MapEntry('JDN', '${composite['jdn'] ?? ''}'),
      MapEntry('Gregorian Date', '${composite['gregorian_date'] ?? ''}'),
      MapEntry('Tzolkin', '${composite['tzolkin_value'] ?? ''} ${composite['tzolkin_name'] ?? ''}'),
      MapEntry('Haab', '${composite['haab_day'] ?? ''} ${composite['haab_month_name'] ?? ''}'),
      MapEntry('Long Count', '${composite['long_count'] ?? ''}'),
      MapEntry('Year Bearer', '${composite['year_bearer_name'] ?? ''} ${composite['year_bearer_value'] ?? ''}'),
      MapEntry('Direction/Color', '${composite['dir_color_str'] ?? ''}'),
      MapEntry('ISO Weekday', '${composite['iso_weekday'] ?? ''}'),
    ];

    return GridView.count(
      crossAxisCount: 2,
      childAspectRatio: 3.2,
      crossAxisSpacing: 8,
      mainAxisSpacing: 8,
      children: items
          .map(
            (item) => Card(
              margin: EdgeInsets.zero,
              child: Padding(
                padding: const EdgeInsets.all(10),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(item.key, style: Theme.of(context).textTheme.labelMedium),
                    const SizedBox(height: 4),
                    Text(item.value, maxLines: 2, overflow: TextOverflow.ellipsis),
                  ],
                ),
              ),
            ),
          )
          .toList(),
    );
  }

  Widget _buildDeriveResult(Map<String, dynamic> result) {
    final autocorr = result['autocorr'];
    if (autocorr is! Map<String, dynamic>) {
      return const Text('Unexpected derive response format.');
    }

    final entries = autocorr.entries.toList();
    return SingleChildScrollView(
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: entries
            .map(
              (entry) => Chip(
                label: Text('${entry.key}: ${entry.value}'),
              ),
            )
            .toList(),
      ),
    );
  }

  Widget _buildRangeResult(Map<String, dynamic> result) {
    final count = result['count'];
    final scanned = result['scanned'];
    final fields = (result['fields'] as List?)?.map((e) => e.toString()).toList() ?? <String>[];
    final rows = (result['rows'] as List?)?.whereType<Map>().toList() ?? <Map>[];

    if (fields.isEmpty || rows.isEmpty) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Matches: $count | Scanned: $scanned'),
          const SizedBox(height: 12),
          const Text('No matching rows.'),
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Matches: $count | Scanned: $scanned'),
        const SizedBox(height: 10),
        Expanded(
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: SingleChildScrollView(
              child: DataTable(
                columns: fields.map((field) => DataColumn(label: Text(field))).toList(),
                rows: rows.take(100).map((rawRow) {
                  final row = rawRow.cast<dynamic, dynamic>();
                  return DataRow(
                    cells: fields
                        .map((field) => DataCell(Text('${row[field] ?? ''}')))
                        .toList(),
                  );
                }).toList(),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCorrelationsResult(Map<String, dynamic> result) {
    final presets = (result['presets'] as List?)?.whereType<Map>().toList() ?? <Map>[];
    if (presets.isEmpty) {
      return const Text('No presets available.');
    }

    return ListView.separated(
      itemCount: presets.length,
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemBuilder: (context, index) {
        final preset = presets[index].cast<dynamic, dynamic>();
        return ListTile(
          title: Text('${preset['name'] ?? ''}'),
          subtitle: Text('${preset['description'] ?? ''}'),
          trailing: Text('New Era: ${preset['new_era'] ?? ''}'),
        );
      },
    );
  }

  String _prettyMethod(String method) {
    switch (method) {
      case 'convert':
        return 'Convert';
      case 'derive_autocorr':
        return 'Derive Auto-Corrections';
      case 'search_range':
        return 'Search Range';
      case 'list_correlations':
        return 'Correlation Presets';
      default:
        return method;
    }
  }

  Widget _buildSection({required String title, required Widget child}) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.35),
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
    final candidates = _candidateBackendExecutables(executable);
    final errors = <String>[];
    for (final candidate in candidates) {
      try {
        final process = await Process.start(candidate, []);
        return RpcBridge._(process);
      } catch (e) {
        errors.add('$candidate -> $e');
      }
    }
    throw StateError(
      'Unable to start RPC backend. Tried ${candidates.join(", ")}. Errors: ${errors.join(" | ")}',
    );
  }

  static List<String> _candidateBackendExecutables(String fallbackExecutable) {
    final exePath = Platform.resolvedExecutable;
    final exeDir = File(exePath).parent.path;
    final out = <String>[];

    if (Platform.isMacOS) {
      final bundled = '$exeDir/pohualli-rpc-bin';
      if (File(bundled).existsSync()) {
        out.add(bundled);
      }
    }
    if (Platform.isWindows) {
      final bundled = '$exeDir\\pohualli-rpc-bin.exe';
      if (File(bundled).existsSync()) {
        out.add(bundled);
      }
      // Future-proof for a potential subfolder packaging layout.
      final bundledSubdir = '$exeDir\\backend\\pohualli-rpc-bin.exe';
      if (File(bundledSubdir).existsSync()) {
        out.add(bundledSubdir);
      }
    }

    // Development fallback: use PATH-installed command.
    if (!out.contains(fallbackExecutable)) {
      out.add(fallbackExecutable);
    }
    return out;
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
