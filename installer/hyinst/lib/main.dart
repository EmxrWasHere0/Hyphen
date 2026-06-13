// Hyphen Agent
// UI Installer
//
// Flutter and Dart are products of Google LLC.
//
// Hyphen Project is licensed under GPLv3.
//

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
  late String installationPath;
  late String selectedProvider;
  late String apiKeySecret;
  late String selectedModel;

  late TextEditingController pathController;
  late TextEditingController apiKeyController;
  late TextEditingController modelController;
  final ScrollController logScrollController = ScrollController();

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

  String? homeDir = Platform.environment['HOME'] ?? Platform.environment['USERPROFILE'];

  String get hyphenPath {
    if (Platform.isWindows) {
      return "$homeDir\\Hyphen";
    } else if (Platform.isLinux) {
      return "$homeDir/hyphen";
    } else if (Platform.isMacOS) {
      return "$homeDir/hyphen";
    } else {
      return "";
    }
  }

  String get tempPath {
    if (Platform.isWindows) {
      return r"C:\Windows\Temp\Hyphen";
    } else if (Platform.isLinux) {
      return "/tmp/hyphen";
    } else if (Platform.isMacOS) {
      return "/tmp/hyphen";
    } else {
      return "";
    }
  }

  Map<String, String> get commands {
    if (Platform.isWindows) {
      return {
        "mkdir": "New-Item -ItemType Directory",
        "touch": "New-Item",
        "rm": "Remove-Item",
        "cp": "Copy-Item",
        "curl": "Invoke-WebRequest",
      };
    } else {
      return {
        "mkdir": "mkdir",
        "touch": "touch",
        "rm": "rm -rf",
        "cp": "cp",
        "curl": "curl",
      };
    }
  }

  Map<String, String> get curlParams {
    return Platform.isWindows
        ? {"out": "-OutFile"}
        : {"out": "-o"};
  }

  List<String> globalFiles = [
    "engine/HyCore/agent.py",
    "engine/HyCore/__init__.py",
    "engine/HyCore/standalone.py",
    "webui.py",
    "requirements.txt"
    ];

  List<String> logs = [];

    @override
    void initState() {
      super.initState();
      pathController = TextEditingController(text: defaultPath);
      apiKeyController = TextEditingController();
      modelController = TextEditingController();
    }

  @override
  void dispose() {
    pathController.dispose();
    apiKeyController.dispose();
    modelController.dispose();
    logScrollController.dispose();
    super.dispose();
  }

  Future<void> editFile(String filePath, String oldText, String newText) async {
    final file = File(filePath);

    if (await file.exists()) {
      String content = await file.readAsString();

      String newContent = content.replaceAll(oldText, newText);

      await file.writeAsString(newContent);
    }
  }

  Future<void> runCommand(String cmd, List<String> args) async {
    addLog(">> $cmd ${args.join(" ")}");

    if (Platform.isWindows) {setState(() {
      cmd = "powershell $cmd";
    });}

    final result = await Process.run(cmd, args);

    addLog(result.stdout.toString());

    if (result.stderr.toString().isNotEmpty) {
      addLog("ERROR: ${result.stderr}");
    }
  }

  Future<void> install() async {
    setState(() {
      step = 5;
      progress = 0;
    });

    try {
      if (Platform.isLinux && Process.runSync('id', ['-u']).stdout.toString().trim() != '0') {
        throw Exception("This setup wizard needs elevated privilidge to run. Please run it as superuser/administrator.");
      }
      final instDir = Directory(installationPath);
      if (await instDir.exists()) await instDir.delete(recursive: true);
      await instDir.create(recursive: true);

      final tmpDir = Directory(tempPath);
      if (await tmpDir.exists()) await tmpDir.delete(recursive: true);
      await tmpDir.create(recursive: true);

      addLog("Directories created.");
      setState(() => progress = 0.2);

      for (var file in globalFiles) {
      final idx = file.lastIndexOf('/');

      if (idx != -1) {
        final fileDir = Directory(
          "$tempPath/${file.substring(0, idx)}"
        );

        if (!await fileDir.exists()) {
          await fileDir.create(recursive: true);
        }
      }

      addLog("Downloading: $file");

      await runCommand(
        commands['curl']!,
        [
          "https://raw.githubusercontent.com/EmxrWasHere0/Hyphen/refs/heads/main/$file",
          curlParams['out']!,
          "$tempPath/$file"
        ]
      );
    }

      addLog("Copying files...");
      await for (final entity in tmpDir.list(recursive: true)) {
        String relativePath = entity.path.replaceFirst(tempPath, "");
        if (relativePath.startsWith('/') || relativePath.startsWith('\\')) {
          relativePath = relativePath.substring(1);
        }
        
        final targetPath = "$installationPath/$relativePath";

        if (entity is Directory) {
          await Directory(targetPath).create(recursive: true);
        } else if (entity is File) {
          final parentDir = Directory(entity.parent.path.replaceFirst(tempPath, installationPath));
          if (!await parentDir.exists()) {
            await parentDir.create(recursive: true);
          }
          await entity.copy(targetPath);
        }
      }

      addLog("Setting up virtual environment...");
      await runCommand("python3", ["-m", "venv", "$installationPath/engine/.venv"]);
      if (Platform.isWindows) {
        await runCommand("$installationPath\\engine\\.venv\\Scripts\\pip.exe",["install", "-r", "$tempPath/requirements.txt"]);
      } else {
        await runCommand("$installationPath/engine/.venv/bin/pip3", ["install", "-r", "$tempPath/requirements.txt"]);
      }

      setState(() => progress = 0.6);

      addLog("Creating Hyphen-allowed default directory");
      addLog("Default directory: $hyphenPath");
      await runCommand(commands["mkdir"]!, ["-pv", hyphenPath]);

      await File("$installationPath/engine/HyCore/config.env").writeAsString(
        "API_KEY=$apiKeySecret\nPROVIDER=$selectedProvider\nMODEL=$selectedModel\nSTORAGE_PATH=$hyphenPath"
      );

      if (Platform.isLinux) {
        addLog("Servisler kuruluyor...");
        for (var s in ["standalone", "webui"]) {
          String serviceFile = "/etc/systemd/system/hyphen-$s.service";
          await runCommand("curl", ["-o", serviceFile, "https://raw.githubusercontent.com/EmxrWasHere0/Hyphen/refs/heads/main/$s.service"]);
          
          await editFile(serviceFile, "PLACEHOLDER_USER", "root");
          await editFile(serviceFile, "PLACEHOLDER_WD", installationPath);
          if (s == "standalone")
          {await editFile(serviceFile, "PLACEHOLDER_EXEC", "$installationPath/engine/.venv/bin/python3 $installationPath/engine/HyCore/$s.py");}
          else
          {await editFile(serviceFile, "PLACEHOLDER_EXEC","$installationPath/engine/.venv/bin/python3 $installationPath/$s.py");}
          
          await runCommand("systemctl", ["enable", "hyphen-$s"]);
        }
        await runCommand("systemctl", ["daemon-reload"]);
      }

      setState(() => progress = 1.0);
    } catch (e) {
      addLog("CRITIC ERROR: $e");
    } finally {
      if (progress >= 1.0) setState(() => step = 6);
    }
  }

  void addLog(String message) {
    setState(() {
      logs.add(message);
    });

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (logScrollController.hasClients) {
        logScrollController.animateTo(
          logScrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOut,
        );
      }
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
            onPressed: () {
              setState(()
              {
                installationPath = pathController.text;
                step = 2;
              });
            },
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
            onPressed: () {
              setState(()
              {
                step = 3;
                selectedProvider = selectedValue;
              });
            },
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
            onPressed: () {
              setState(() {
                apiKeySecret = apiKeyController.text;
                step = 4; // Model sayfasına geç
              });
            },
            child: const Text("Next"),
          ),
        ],
      ),
    );
  }

  Widget buildModelSelection() {
    return wrap(
      Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.smart_toy, size: 60, color: Colors.blueAccent), // AI/Robot ikonu
          const SizedBox(height: 10),
          const Text("Model Configuration", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          const Text(
            "Enter the specific model name you want to use (e.g., gpt-4o, gemini-1.5-pro, llama-3).",
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey),
          ),
          const SizedBox(height: 20),
          TextField(
            controller: modelController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              labelText: "Model Name",
              hintText: "e.g. gemini-1.5-flash",
              prefixIcon: Icon(Icons.psychology),
            ),
          ),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: () {
              setState(() {
                selectedModel = modelController.text;
                install();
              });
            },
            child: const Text("Install Hyphen"),
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

          const SizedBox(height: 20),

          Container(
            height: 200,
            width: double.infinity,
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.black,
              borderRadius: BorderRadius.circular(8),
            ),
            child: ListView.builder(
              controller: logScrollController,
              itemCount: logs.length,
              itemBuilder: (context, index) {
                return Text(
                  logs[index],
                  style: const TextStyle(
                    color: Colors.greenAccent,
                    fontSize: 12,
                    fontFamily: "monospace",
                  ),
                );
              },
            ),
          ),
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
      case 1: page = buildPathSelection(); break;
      case 2: page = buildProviderSelection(); break;
      case 3: page = buildApiKey(); break;
      case 4: page = buildModelSelection(); break;
      case 5: page = buildInstalling(); break;
      case 6: page = buildDone(); break;
      default: page = buildWelcome();
    }
    return Scaffold(body: page);
  }
}