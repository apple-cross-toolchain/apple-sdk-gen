from __future__ import annotations


def generate_modulemap(framework_name: str) -> str:
    return (
        f'framework module {framework_name} [system] {{\n'
        f'  umbrella header "{framework_name}.h"\n'
        f'  export *\n'
        f'  module * {{ export * }}\n'
        f'}}\n'
    )
