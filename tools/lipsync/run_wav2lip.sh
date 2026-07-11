#!/usr/bin/env sh
set -eu

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <input-video> <input-audio> <output-video>" >&2
  exit 2
fi

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
WAV2LIP_DIR="$SCRIPT_DIR/Wav2Lip"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
FFMPEG_DIR="$HOME/.local/bin"

INPUT_VIDEO=$(cd "$(dirname -- "$1")" && pwd)/$(basename -- "$1")
INPUT_AUDIO=$(cd "$(dirname -- "$2")" && pwd)/$(basename -- "$2")
OUTPUT_DIR=$(mkdir -p "$(dirname -- "$3")" && cd "$(dirname -- "$3")" && pwd)
OUTPUT_VIDEO="$OUTPUT_DIR/$(basename -- "$3")"

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Python virtual environment not found: $PYTHON_BIN" >&2
  exit 1
fi

if [ ! -f "$WAV2LIP_DIR/checkpoints/wav2lip_gan.pth" ]; then
  echo "Wav2Lip checkpoint not found: $WAV2LIP_DIR/checkpoints/wav2lip_gan.pth" >&2
  exit 1
fi

if [ ! -f "$WAV2LIP_DIR/face_detection/detection/sfd/s3fd.pth" ]; then
  echo "S3FD face detector checkpoint not found: $WAV2LIP_DIR/face_detection/detection/sfd/s3fd.pth" >&2
  exit 1
fi

export PATH="$FFMPEG_DIR:$PATH"
mkdir -p "$WAV2LIP_DIR/temp"

cd "$WAV2LIP_DIR"
exec "$PYTHON_BIN" inference.py \
  --checkpoint_path "checkpoints/wav2lip_gan.pth" \
  --face "$INPUT_VIDEO" \
  --audio "$INPUT_AUDIO" \
  --outfile "$OUTPUT_VIDEO" \
  --resize_factor 1 \
  --face_det_batch_size 1 \
  --wav2lip_batch_size 4 \
  --pads 0 20 0 0
