import os
import platform
import shlex
import subprocess
import sys
from dataclasses import dataclass

from loguru import logger

from app.config import config


@dataclass
class LipSyncResult:
    output_file: str
    command: str


def is_enabled(params) -> bool:
    return bool(
        getattr(params, "lip_sync_enabled", False)
        or config.app.get("lip_sync_enabled", False)
    )


def get_command_template(params) -> str:
    return (
        getattr(params, "lip_sync_command", None)
        or config.app.get("lip_sync_command", "")
        or ""
    ).strip()


def _quote(value: str) -> str:
    if platform.system().lower().startswith("win"):
        return subprocess.list2cmdline([value])
    return shlex.quote(value)


def build_command(
    command_template: str,
    *,
    video_file: str,
    audio_file: str,
    output_file: str,
    workdir: str,
) -> str:
    values = {
        "video": _quote(video_file),
        "audio": _quote(audio_file),
        "output": _quote(output_file),
        "python": _quote(sys.executable),
        "workdir": _quote(workdir),
    }
    try:
        return command_template.format(**values)
    except KeyError as exc:
        raise ValueError(
            f"unknown lip sync command placeholder: {exc.args[0]}"
        ) from exc


def run_lip_sync(
    *,
    video_file: str,
    audio_file: str,
    output_file: str,
    command_template: str,
    workdir: str,
    timeout_seconds: int | None = None,
) -> LipSyncResult:
    if not command_template:
        raise ValueError("lip_sync_command is not configured")
    if not os.path.isfile(video_file):
        raise ValueError(f"lip sync input video does not exist: {video_file}")
    if not os.path.isfile(audio_file):
        raise ValueError(f"lip sync input audio does not exist: {audio_file}")

    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    command = build_command(
        command_template,
        video_file=os.path.abspath(video_file),
        audio_file=os.path.abspath(audio_file),
        output_file=os.path.abspath(output_file),
        workdir=os.path.abspath(workdir),
    )

    timeout_seconds = int(
        timeout_seconds
        if timeout_seconds is not None
        else config.app.get("lip_sync_timeout", 1800)
        or 1800
    )
    logger.info(f"running lip sync command: {command}")
    completed = subprocess.run(
        command,
        shell=True,
        cwd=os.path.abspath(workdir),
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    if completed.stdout:
        logger.info(f"lip sync stdout: {completed.stdout[-4000:]}")
    if completed.stderr:
        logger.warning(f"lip sync stderr: {completed.stderr[-4000:]}")
    if completed.returncode != 0:
        raise RuntimeError(f"lip sync command failed with code {completed.returncode}")
    if not os.path.isfile(output_file) or os.path.getsize(output_file) <= 0:
        raise RuntimeError(f"lip sync output file was not created: {output_file}")

    return LipSyncResult(output_file=output_file, command=command)
