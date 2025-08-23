from pathlib import Path
from sys import argv

from delocate.fuse import fuse_wheels


def fuse_wheelhouse(wheelhouse: Path):
    assert wheelhouse.is_dir()
    arm64: set[str] = set()
    x86_64: set[str] = set()
    arm64_names: dict[str, str] = {}
    x86_64_names: dict[str, str] = {}
    for path in wheelhouse.iterdir():
        if "macosx" not in path.name:
            continue
        stem = path.name.split("-macosx")[0]
        if "11_0_arm64" in path.name:
            arm64_names[stem] = path.name
            arm64.add(stem)
        elif "10_9_x86_64" in path.name:
            x86_64_names[stem] = path.name
            x86_64.add(stem)
        elif "10_13_x86_64" in path.name:
            x86_64_names[stem] = path.name
            x86_64.add(stem)
    for target in arm64 & x86_64:
        to_wheel = arm64_names[target]
        from_wheel = x86_64_names[target]
        out_wheel = f"{target}-macosx_11_0_universal2.whl"
        print(f"Fusing {to_wheel} & {from_wheel} --> {out_wheel}")
        to_path = str(wheelhouse / to_wheel)
        from_path = str(wheelhouse / from_wheel)
        out_path = str(wheelhouse / out_wheel)
        fuse_wheels(to_path, from_path, out_path)


if __name__ == "__main__":
    path = argv[1] if len(argv) > 1 else "wheelhouse"
    fuse_wheelhouse(Path(path))
