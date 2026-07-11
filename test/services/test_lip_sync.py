import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.services import lip_sync


class TestLipSyncService(unittest.TestCase):
    def test_build_command_supports_current_python_placeholder(self):
        command = lip_sync.build_command(
            "{python} tools/lipsync/run_wav2lip.py {video} {audio} {output}",
            video_file="/tmp/input video.mp4",
            audio_file="/tmp/input audio.wav",
            output_file="/tmp/output video.mp4",
            workdir="/tmp/work dir",
        )

        self.assertIn(lip_sync._quote(sys.executable), command)
        self.assertIn(lip_sync._quote("/tmp/input video.mp4"), command)
        self.assertIn(lip_sync._quote("/tmp/input audio.wav"), command)
        self.assertIn(lip_sync._quote("/tmp/output video.mp4"), command)

    def test_build_command_rejects_unknown_placeholder(self):
        with self.assertRaisesRegex(ValueError, "unknown lip sync command placeholder"):
            lip_sync.build_command(
                "{missing}",
                video_file="video.mp4",
                audio_file="audio.wav",
                output_file="output.mp4",
                workdir=".",
            )

    def test_run_lip_sync_uses_current_python_placeholder(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            video_file = os.path.join(tmp_dir, "input.mp4")
            audio_file = os.path.join(tmp_dir, "input.wav")
            output_file = os.path.join(tmp_dir, "output.mp4")
            script_file = os.path.join(tmp_dir, "copy_output.py")

            with open(video_file, "wb") as file:
                file.write(b"video")
            with open(audio_file, "wb") as file:
                file.write(b"audio")
            with open(script_file, "w", encoding="utf-8") as file:
                file.write(
                    "import pathlib, sys\n"
                    "pathlib.Path(sys.argv[1]).write_bytes(b'output')\n"
                )

            result = lip_sync.run_lip_sync(
                video_file=video_file,
                audio_file=audio_file,
                output_file=output_file,
                command_template="{python} " + lip_sync._quote(script_file) + " {output}",
                workdir=tmp_dir,
                timeout_seconds=10,
            )

            self.assertEqual(result.output_file, output_file)
            self.assertTrue(os.path.getsize(output_file) > 0)
            self.assertIn(lip_sync._quote(sys.executable), result.command)


if __name__ == "__main__":
    unittest.main()
