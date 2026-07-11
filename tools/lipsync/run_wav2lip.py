import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _prepend_path(path: Path) -> None:
    if path.is_dir():
        os.environ["PATH"] = str(path) + os.pathsep + os.environ.get("PATH", "")


def _add_ffmpeg_paths(project_dir: Path) -> None:
    candidates = [
        Path.home() / ".local" / "bin",
        project_dir.parent / "lib" / "ffmpeg",
        project_dir.parent / "lib" / "ffmpeg" / "ffmpeg-7.0-essentials_build",
        project_dir.parent
        / "lib"
        / "ffmpeg"
        / "ffmpeg-7.0-essentials_build"
        / "bin",
    ]
    for candidate in candidates:
        _prepend_path(candidate)

    if shutil.which("ffmpeg"):
        return

    try:
        import imageio_ffmpeg
    except Exception:
        return

    ffmpeg_exe = Path(imageio_ffmpeg.get_ffmpeg_exe())
    _prepend_path(ffmpeg_exe.parent)


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"{label} not found: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the bundled Wav2Lip model with project-local defaults."
    )
    parser.add_argument("input_video")
    parser.add_argument("input_audio")
    parser.add_argument("output_video")
    parser.add_argument("--resize-factor", type=int, default=1)
    parser.add_argument("--face-det-batch-size", type=int, default=1)
    parser.add_argument("--wav2lip-batch-size", type=int, default=4)
    parser.add_argument("--pads", nargs=4, default=["0", "20", "0", "0"])
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent.parent
    wav2lip_dir = script_dir / "Wav2Lip"
    checkpoint = wav2lip_dir / "checkpoints" / "wav2lip_gan.pth"
    detector = wav2lip_dir / "face_detection" / "detection" / "sfd" / "s3fd.pth"

    input_video = Path(args.input_video).resolve()
    input_audio = Path(args.input_audio).resolve()
    output_video = Path(args.output_video).resolve()

    _require_file(input_video, "input video")
    _require_file(input_audio, "input audio")
    _require_file(checkpoint, "Wav2Lip checkpoint")
    _require_file(detector, "S3FD face detector checkpoint")
    output_video.parent.mkdir(parents=True, exist_ok=True)
    (wav2lip_dir / "temp").mkdir(exist_ok=True)
    _add_ffmpeg_paths(project_dir)

    command = [
        sys.executable,
        "inference.py",
        "--checkpoint_path",
        str(checkpoint.relative_to(wav2lip_dir)),
        "--face",
        str(input_video),
        "--audio",
        str(input_audio),
        "--outfile",
        str(output_video),
        "--resize_factor",
        str(args.resize_factor),
        "--face_det_batch_size",
        str(args.face_det_batch_size),
        "--wav2lip_batch_size",
        str(args.wav2lip_batch_size),
        "--pads",
        *[str(value) for value in args.pads],
    ]
    return subprocess.call(command, cwd=str(wav2lip_dir))


if __name__ == "__main__":
    raise SystemExit(main())
