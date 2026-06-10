import 'dart:io';
import 'package:flutter/material.dart';
import 'package:window_manager/window_manager.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await windowManager.ensureInitialized();

  runApp(const InstallerApp());

  windowManager.waitUntilReadyToShow(null, () async {
    await windowManager.show();
    await windowManager.focus();

    await windowManager.setSize(const Size(800, 600));
    await windowManager.center();
    await windowManager.setResizable(false);
    await windowManager.setMinimumSize(const Size(800, 600));
    await windowManager.setMaximumSize(const Size(800, 600));
  });
}

class InstallerApp extends StatelessWidget {
  const InstallerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: InstallerPage(),
    );
  }
}

class InstallerPage extends StatefulWidget {
  const InstallerPage({super.key});

  @override
  State<InstallerPage> createState() => _InstallerPageState();
}

class _InstallerPageState extends State<InstallerPage> {
  int step = 0;
  double progress = 0;

  String selectedValue = "google";

  late TextEditingController pathController;
  late TextEditingController apiKeyController;

  String get defaultPath {
    if (Platform.isWindows) {
      return r"C:\Program Files\Hyphen";
    } else if (Platform.isLinux) {
      return "/opt/hyphen";
    } else if (Platform.isMacOS) {
      return "/Applications/Hyphen";
    } else {
      return "";
    }
  }

  @override
  void initState() {
    super.initState();
    pathController = TextEditingController(text: defaultPath);
    apiKeyController = TextEditingController();
  }

  @override
  void dispose() {
    pathController.dispose();
    apiKeyController.dispose();
    super.dispose();
  }

  Future<void> install() async {
    setState(() {
      step = 4;
      progress = 0;
    });

    for (int i = 0; i <= 100; i++) {
      await Future.delayed(const Duration(milliseconds: 25));
      setState(() {
        progress = i / 100;
      });
    }

    setState(() {
      step = 5;
    });
  }

  Widget wrap(Widget child) {
    return Center(
      child: SingleChildScrollView(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 500),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: child,
          ),
        ),
      ),
    );
  }

  Widget buildWelcome() {
    return wrap(
      Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.download, size: 80),
          const SizedBox(height: 20),
          const Text(
            "Hyphen Installer",
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),
          Text("Detected OS: ${Platform.operatingSystem}"),
          const SizedBox(height: 30),
          ElevatedButton(
            onPressed: () => setState(() => step = 1),
            child: const Text("Start"),
          ),
        ],
      ),
    );
  }

  Widget buildPathSelection() {
    return wrap(
      Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text("Install Path", style: TextStyle(fontSize: 20)),
          const SizedBox(height: 20),
          TextField(
            controller: pathController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              labelText: "Path",
              prefixIcon: Icon(Icons.folder),
            ),
          ),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: () => setState(() => step = 2),
            child: const Text("Next"),
          ),
        ],
      ),
    );
  }

  Widget buildProviderSelection() {
    return wrap(
      Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text("Provider", style: TextStyle(fontSize: 20)),
          const SizedBox(height: 20),

          DropdownButtonFormField<String>(
            initialValue: selectedValue,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              prefixIcon: Icon(Icons.cloud),
            ),
            items: const [
              DropdownMenuItem(
                value: "google",
                child: Text("Google (recommended)"),
              ),
              DropdownMenuItem(
                value: "openrouter",
                child: Text("OpenRouter"),
              ),
              DropdownMenuItem(
                value: "groq",
                child: Text("Groq"),
              ),
            ],
            onChanged: (value) {
              setState(() {
                selectedValue = value!;
              });
            },
          ),

          const SizedBox(height: 20),

          ElevatedButton(
            onPressed: () => setState(() => step = 3),
            child: const Text("Next"),
          ),
        ],
      ),
    );
  }

  Widget buildApiKey() {
    return wrap(
      Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.key, size: 60),
          const SizedBox(height: 10),
          const Text("API Key", style: TextStyle(fontSize: 20)),
          const SizedBox(height: 20),
          TextField(
            controller: apiKeyController,
            obscureText: true,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              labelText: "Enter API Key",
              prefixIcon: Icon(Icons.lock),
            ),
          ),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: install,
            child: const Text("Install"),
          ),
        ],
      ),
    );
  }

  Widget buildInstalling() {
    return wrap(
      Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text("Installing..."),
          const SizedBox(height: 20),
          LinearProgressIndicator(value: progress),
          const SizedBox(height: 10),
          Text("${(progress * 100).toInt()}%"),
        ],
      ),
    );
  }

  Widget buildDone() {
    return wrap(
      Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.check_circle, color: Colors.green, size: 80),
          const SizedBox(height: 20),
          const Text(
            "Installation Complete!",
            style: TextStyle(fontSize: 22),
          ),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: () => exit(0),
            child: const Text("Exit"),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    Widget page;

    switch (step) {
      case 1:
        page = buildPathSelection();
        break;
      case 2:
        page = buildProviderSelection();
        break;
      case 3:
        page = buildApiKey();
        break;
      case 4:
        page = buildInstalling();
        break;
      case 5:
        page = buildDone();
        break;
      default:
        page = buildWelcome();
    }

    return Scaffold(
      body: page,
    );
  }
}