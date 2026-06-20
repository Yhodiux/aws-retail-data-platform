import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def build_common_zip():
    project_root = Path(__file__).resolve().parent.parent
    source_directory = project_root / "scripts" / "common"
    output_path = project_root / "libs" / "common.zip"
    temporary_path = output_path.with_suffix(".tmp.zip")

    try:
        with ZipFile(temporary_path, "w", compression=ZIP_DEFLATED) as archive:
            for source_file in sorted(source_directory.glob("*.py")):
                archive.write(
                    source_file,
                    arcname=f"common/{source_file.name}",
                )
        os.replace(temporary_path, output_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    print(f"Created {output_path}")


if __name__ == "__main__":
    build_common_zip()

