import ast
import re
import subprocess
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent.parent
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^]]*\]\(([^)]+)\)")


def validate_python_syntax():
    python_files = sorted(
        list((ROOT / "scripts").rglob("*.py"))
        + list((ROOT / "tests").rglob("*.py"))
    )
    for path in python_files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return len(python_files)


def _has_exact_case(path):
    current = path.anchor and Path(path.anchor) or Path(".")
    parts = path.parts[1:] if path.anchor else path.parts
    for part in parts:
        if not current.exists():
            return False
        names = {entry.name for entry in current.iterdir()}
        if part not in names:
            return False
        current = current / part
    return True


def validate_markdown():
    markdown_files = sorted(ROOT.rglob("*.md"))
    errors = []

    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        if text.count("```") % 2:
            errors.append(f"Unbalanced code fence: {path.relative_to(ROOT)}")

        for raw_target in MARKDOWN_LINK_PATTERN.findall(text):
            target = raw_target.split("#", 1)[0]
            if not target or re.match(r"^[a-z]+://", target):
                continue
            candidate = (path.parent / target).resolve()
            if not candidate.exists():
                errors.append(
                    f"Missing link in {path.relative_to(ROOT)}: {raw_target}"
                )
            elif not _has_exact_case(candidate):
                errors.append(
                    f"Case mismatch in {path.relative_to(ROOT)}: {raw_target}"
                )

    if errors:
        raise ValueError("\n".join(errors))
    return len(markdown_files)


def validate_common_zip():
    source_files = {
        f"common/{path.name}": path
        for path in (ROOT / "scripts" / "common").glob("*.py")
    }
    source_names = set(source_files)
    with ZipFile(ROOT / "libs" / "common.zip") as archive:
        archive_names = set(archive.namelist())

    if any("\\" in name for name in archive_names):
        raise ValueError("libs/common.zip contains non-portable backslash paths")
    if archive_names != source_names:
        missing = sorted(source_names - archive_names)
        extra = sorted(archive_names - source_names)
        raise ValueError(
            f"libs/common.zip is stale: missing={missing}, extra={extra}"
        )
    with ZipFile(ROOT / "libs" / "common.zip") as archive:
        stale_files = [
            name
            for name, source_path in source_files.items()
            if archive.read(name) != source_path.read_bytes()
        ]
    if stale_files:
        raise ValueError(
            f"libs/common.zip has stale file contents: {sorted(stale_files)}"
        )
    return len(archive_names)


def validate_source_data_is_untracked():
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT.as_posix()}",
            "ls-files",
            "--cached",
            "--",
            "*.csv",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    tracked_csv_files = [line for line in result.stdout.splitlines() if line]
    if tracked_csv_files:
        raise ValueError(
            f"Source CSV files must not be committed: {tracked_csv_files}"
        )


def main():
    python_count = validate_python_syntax()
    markdown_count = validate_markdown()
    package_count = validate_common_zip()
    validate_source_data_is_untracked()
    print(
        "Repository validation passed: "
        f"python_files={python_count}, "
        f"markdown_files={markdown_count}, "
        f"package_files={package_count}, "
        "tracked_csv_files=0"
    )


if __name__ == "__main__":
    main()
