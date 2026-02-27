# apple-sdk-gen

Generate Apple SDK stubs from the public Apple Developer Documentation API.

## What it does

`apple-sdk-gen` crawls Apple's documentation JSON API to discover frameworks
and their symbols, then assembles stub SDKs containing:

- **TBD stubs** (`.tbd`) for linking against system frameworks and dylibs
- **Objective-C umbrella headers** with type declarations, class interfaces, protocols, and enums
- **Module maps** for Clang module imports
- **Swift interfaces** (`.swiftinterface`) for Swift cross-compilation
- **C stdlib / POSIX headers** from Apple open-source distributions
- **C++ standard library headers** from upstream LLVM
- **SDKSettings.json** and **Info.plist** matching Xcode's metadata format

Output replicates the Xcode SDK directory structure:

```
output/Xcode.app/Contents/Developer/Platforms/
├── iPhoneOS.platform/Developer/SDKs/
│   ├── iPhoneOS.sdk/            ← real directory
│   └── iPhoneOS18.0.sdk         → iPhoneOS.sdk (symlink)
├── iPhoneSimulator.platform/Developer/SDKs/
│   ├── iPhoneSimulator.sdk/
│   └── iPhoneSimulator18.0.sdk  → iPhoneSimulator.sdk
├── MacOSX.platform/...
├── AppleTVOS.platform/...
├── AppleTVSimulator.platform/...
├── WatchOS.platform/...
├── WatchSimulator.platform/...
├── XROS.platform/...
└── XRSimulator.platform/...
```

## Quick start

```bash
# Generate iOS and macOS SDKs (default)
python3 -m tools.apple_sdk_gen --sdk-version 18.0 --all-frameworks

# Generate all platforms with simulators and full headers
python3 -m tools.apple_sdk_gen \
  --platforms ios,macos,tvos,watchos,visionos \
  --include-simulators \
  --sdk-version 18.0 \
  --all-frameworks \
  --include-libc \
  --include-swift \
  --include-cxx \
  --output output
```

First run can take up to several hours, but API responses are cached locally in
`.cache/` so subsequent runs should be faster.

## CLI options

| Flag | Default | Description |
|------|---------|-------------|
| `--sdk-version` | *(required)* | SDK version to generate (e.g. `18.0`) |
| `--platforms` | `ios,macos` | Comma-separated: `ios`, `macos`, `tvos`, `watchos`, `visionos` |
| `--include-simulators` | off | Also generate simulator SDKs for each device platform |
| `--all-frameworks` | off | Generate all available frameworks |
| `--frameworks` | none | Comma-separated list of specific frameworks |
| `--exclude-frameworks` | none | Comma-separated list of frameworks to skip |
| `--include-swift` | off | Generate `.swiftinterface` files |
| `--include-libc` | off | Download C stdlib/POSIX headers from Apple OSS |
| `--include-cxx` | off | Download C++ stdlib headers from LLVM |
| `--output` | `./output` | Output directory |
| `--cache-dir` | `./.cache` | Cache directory for API responses |
| `--concurrency` | `10` | Max concurrent API requests |
| `--rate-limit` | `10.0` | API requests per second |
| `-v` / `-vv` | quiet | Verbosity (INFO / DEBUG) |

## Limitations

The documentation API was designed for rendering docs, not generating SDKs. Key
gaps include missing enum raw values, empty struct bodies, no inline function
implementations, and no preprocessor macro definitions. See
[LIMITATIONS.md](tools/apple_sdk_gen/LIMITATIONS.md) for details and
workarounds.
