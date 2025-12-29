from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def warn(msg: str) -> None:
    print(f"[warn] {msg}", file=sys.stderr)


def info(msg: str) -> None:
    print(f"[info] {msg}")


def fail(msg: str, code: int = 1) -> "NoReturn":
    print(f"[error] {msg}", file=sys.stderr)
    raise SystemExit(code)


def resolve_inklecate(explicit: str | None) -> str:
    candidates: list[str] = []

    if explicit:
        candidates.append(explicit)

    env = os.environ.get("INKLECATE")
    if env:
        candidates.append(env)

    which_exe = shutil.which("inklecate.exe")
    if which_exe:
        candidates.append(which_exe)

    which_plain = shutil.which("inklecate")
    if which_plain:
        candidates.append(which_plain)

    for c in candidates:
        p = Path(c)
        if p.exists() and p.is_file():
            return str(p)

    if candidates:
        warn("Tried inklecate candidates but none existed as files:")
        for c in candidates:
            warn(f"  candidate: {c}")

    fail(
        "Could not find inklecate. Ensure inklecate.exe is on PATH, "
        "or set INKLECATE to its full path, or pass --inklecate."
    )
    return ""


def expected_compiler_file(input_ink: Path) -> Path:
    # Common behavior: story.ink -> story.ink.json
    return input_ink.with_name(input_ink.name + ".json")


def run_compile(inklecate: str, input_ink: Path) -> tuple[int, str, str]:
    cmd = [inklecate, str(input_ink)]
    info(f"Running: {' '.join(cmd)}")

    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def validate_json_file(p: Path) -> None:
    if not p.exists():
        fail(f"Expected JSON file was not found: {p}")

    size = p.stat().st_size
    if size < 50:
        warn(f"JSON file is very small ({size} bytes). That is suspicious.")

    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        fail(f"File exists but is not valid JSON: {p} ({e})")

    if not isinstance(data, dict):
        warn("JSON root is not an object. InkJS usually expects an object.")

    if "inkVersion" not in data and "root" not in data:
        warn("JSON does not contain 'inkVersion' or 'root'. It might still be valid, but check it.")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser(description="Compile Ink (.ink) to JSON for a Next.js site.")
    parser.add_argument(
        "--input",
        default=str(repo_root / "ink" / "story.ink"),
        help="Path to the root .ink file. Default: ink/story.ink",
    )
    parser.add_argument(
        "--output",
        default=str(repo_root / "public" / "story.json"),
        help="Path to output JSON file. Default: public/story.json",
    )
    parser.add_argument(
        "--inklecate",
        default=None,
        help="Path to inklecate.exe. If omitted, uses INKLECATE env var or PATH.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output. Errors still print.",
    )

    args = parser.parse_args()

    input_ink = Path(args.input).resolve()
    output_json = Path(args.output).resolve()

    if not input_ink.exists():
        fail(f"Input .ink file not found: {input_ink}")
    if input_ink.suffix.lower() != ".ink":
        warn(f"Input file does not end with .ink: {input_ink.name}")

    output_json.parent.mkdir(parents=True, exist_ok=True)

    inklecate = resolve_inklecate(args.inklecate)

    # Delete the expected compiler output first, so we can detect fresh output.
    compiler_out = expected_compiler_file(input_ink)
    if compiler_out.exists():
        try:
            compiler_out.unlink()
        except Exception:
            warn(f"Could not delete old compiler output: {compiler_out}")

    code, out, err = run_compile(inklecate, input_ink)

    if not args.quiet:
        if out.strip():
            print(out.strip())
        if err.strip():
            print(err.strip(), file=sys.stderr)

    if code != 0:
        fail(f"Ink compilation failed with exit code {code}.", code=code)

    # Two supported behaviors:
    # 1) inklecate writes JSON to stdout
    # 2) inklecate writes story.ink.json to disk (common on Windows setups)
    stdout_text = out.strip()

    if stdout_text:
        # Use stdout as source of truth
        output_json.write_text(stdout_text, encoding="utf-8")
        validate_json_file(output_json)
        info(f"Compiled OK (stdout): {input_ink} -> {output_json}")
    else:
        # Look for the file output
        if not compiler_out.exists():
            fail(
                "Ink compilation returned success but produced no stdout and no output file. "
                f"Expected file: {compiler_out}"
            )

        validate_json_file(compiler_out)
        shutil.copyfile(compiler_out, output_json)
        info(f"Compiled OK (file): {input_ink} -> {compiler_out} -> {output_json}")

    # Friendly warnings, still strict.
    try:
        text = input_ink.read_text(encoding="utf-8", errors="replace")
        if "-> END" not in text and "->END" not in text:
            warn("Root ink file does not contain an END divert. Maybe fine, maybe not.")
        if "TODO" in text or "FIXME" in text:
            warn("Found TODO or FIXME in your story. Shocking.")
    except Exception:
        warn("Could not read input file to run basic warnings.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
