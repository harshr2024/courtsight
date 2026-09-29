import os
from pathlib import Path
import tempfile
import unittest

import cv2
import numpy as np

from drawers import BallTracksDrawer, CourtKeypointDrawer, FrameNumberDrawer, PlayerTracksDrawer
from utils import build_analysis_cache_key, read_stub, read_video, save_stub, save_video
from web_app import app


class CacheIsolationTests(unittest.TestCase):
    def test_cache_rejects_a_different_video_key(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            video_a = root / "a.mp4"
            video_b = root / "b.mp4"
            model = root / "model.pt"
            video_a.write_bytes(b"video-a-same-frame-count")
            video_b.write_bytes(b"video-b-same-frame-count")
            model.write_bytes(b"model")
            settings = {"frame_skip": 1, "target_width": 1280, "max_frames": None}
            key_a = build_analysis_cache_key(video_a, [model], settings)
            key_b = build_analysis_cache_key(video_b, [model], settings)
            self.assertNotEqual(key_a, key_b)

            cache_path = root / "tracks.pkl"
            save_stub(str(cache_path), ["from-a"], cache_key=key_a)
            self.assertEqual(read_stub(True, str(cache_path), cache_key=key_a), ["from-a"])
            self.assertIsNone(read_stub(True, str(cache_path), cache_key=key_b))


class VideoTimingTests(unittest.TestCase):
    def test_frame_skip_preserves_duration_and_frame_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.avi"
            writer = cv2.VideoWriter(
                str(source), cv2.VideoWriter_fourcc(*"MJPG"), 30.0, (64, 48)
            )
            self.assertTrue(writer.isOpened())
            for index in range(11):
                writer.write(np.full((48, 64, 3), index * 10, dtype=np.uint8))
            writer.release()

            frames, metadata = read_video(
                str(source), frame_skip=2, target_width=None, return_metadata=True
            )
            self.assertEqual(len(frames), 6)
            self.assertEqual(metadata.processed_frame_count, 6)
            self.assertAlmostEqual(metadata.source_fps, 30.0, places=1)
            self.assertAlmostEqual(metadata.output_fps, 6 / (11 / 30), places=3)

            output = root / "output.avi"
            save_video(frames, str(output), fps=metadata.output_fps)
            capture = cv2.VideoCapture(str(output))
            self.assertTrue(capture.isOpened())
            self.assertEqual(int(capture.get(cv2.CAP_PROP_FRAME_COUNT)), 6)
            output_fps = capture.get(cv2.CAP_PROP_FPS)
            self.assertAlmostEqual(output_fps, metadata.output_fps, places=1)
            self.assertAlmostEqual(6 / output_fps, 11 / 30, places=2)
            capture.release()


class AnnotationFrameTests(unittest.TestCase):
    def test_supported_drawers_never_drop_frames(self):
        frames = [np.zeros((120, 160, 3), dtype=np.uint8) for _ in range(4)]
        empty_tracks = [{} for _ in frames]
        output = PlayerTracksDrawer().draw(frames, empty_tracks)
        output = BallTracksDrawer().draw(output, empty_tracks)
        output = CourtKeypointDrawer().draw(output, [None for _ in frames])
        output = FrameNumberDrawer().draw(output)
        self.assertEqual(len(output), len(frames))


class WebApiTests(unittest.TestCase):
    def test_upload_is_required(self):
        client = app.test_client()
        response = client.post("/api/analyze", data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Choose a video", response.get_json()["message"])


if __name__ == "__main__":
    unittest.main()
