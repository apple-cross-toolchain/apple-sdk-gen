# macOS 26.5 Darwin export inventory

`darwin_macos_26.5.json` is a preview for arm64 and x86_64. It is an
explicit input to the version-aware generator:

```sh
python3 -m tools.apple_sdk_gen --platforms macos --sdk-version 26.5 \
  --darwin-library-metadata tools/apple_sdk_gen/supplements/data/darwin_macos_26.5.json \
  --frameworks CoreGraphics,Network,Security
```

The source-backed export selection uses:

- [Apple's macOS 26.5 source distribution](https://github.com/apple-oss-distributions/distribution-macOS/tree/83390100289cedfe669c31a96c94326d31afa1ed).
  Use the C installation produced from this release. Compile references
  for the public headers with pinned Clang and inspect their undefined
  Mach-O symbols. Use the published
  [Libsystem component selection](https://github.com/apple-oss-distributions/Libsystem/blob/c23b51183e46e613375dc7639fb4bf11fbf59ba8/xcodescripts/linker_arguments.sh)
  and verified providers on macOS 26.5.2 build 25F84. The supplemental
  source evidence covers Libc's forwarding, stack and fortify symbols,
  the XNU syscall and MIG interfaces, dyld's assembly, libunwind,
  CommonCrypto, and Libnotify. The emitter retains 40 library
  documents with their target-specific exports and reexports.
- [objc4 at the matching distribution pin](https://github.com/apple-oss-distributions/objc4/tree/ebfe77e64331034c867285a95d3ac205203291d5).
  Extract public declarations with clang-installapi. Also qualify the
  compiler ABI from the published objc4 declarations and
  [Clang's ARC specification](https://github.com/llvm/llvm-project/blob/85ac560262434c9ccfc0c183ec22d4138ed647fb/clang/docs/AutomaticReferenceCounting.rst)
  and code generation. Retain the matching deployed exports.
- [LLVM 23.1.2 Darwin libc++ ABI lists](https://github.com/llvm/llvm-project/tree/85ac560262434c9ccfc0c183ec22d4138ed647fb/libcxx/lib/abi)
  and [libc++abi export lists](https://github.com/llvm/llvm-project/tree/85ac560262434c9ccfc0c183ec22d4138ed647fb/libcxxabi/lib).
  Retain symbols present in the selected ABI and the corresponding
  deployed export table. Preserve verified symbol reexports and weak
  exports.

GNU Make uses the POSIX process environment directly. Apple's pinned
[dyld implementation](https://github.com/apple-oss-distributions/dyld/blob/fd8d0c4d52320ebf64db34f3cb280310d905c5ae/libdyld/libdyldGlue.cpp#L1206-L1212)
defines the `environ` data object. Both deployed slices export it from
libdyld. A C client linked through libSystem and read the same environment
as `_NSGetEnviron()` at deployment minima 11.0 and 26.5 on both CPUs.

The arm64 inventory uses provider evidence from the arm64e runtime, and
the x86_64 inventory uses the Rosetta runtime. Xcode build 25F70 was
used for comparison only. Its export inventory and raw runtime
captures are outside this data file.

The preview contains 3,162 libSystem names on arm64 and 3,188 on
x86_64. These are raw unique name counts across the retained library
documents. Both architectures ran C, Objective-C ARC, and C++ samples.
`pipe` links and runs. `pipe2` and `dup3` are undefined. The reference
also exposes additional names whose eligibility and demand still need
review. This input is scoped to the generated C and Objective-C
surfaces and compiler ABI evidence. The full consumer suites and
release approval remain open.
