"""CourtSight's supported demo pipeline.

The intentionally narrow scope is:
video input -> player tracking + ball detections + court keypoints -> annotated video.
"""

import argparse
import os
from pathlib import Path

import torch

from court_keypoint_detector import CourtKeypointDetector
from drawers import BallTracksDrawer, CourtKeypointDrawer, FrameNumberDrawer, PlayerTracksDrawer
from trackers import BallTracker, PlayerTracker
from utils import build_analysis_cache_key, read_video, save_video


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODELS = {
    "player": BASE_DIR / "models" / "player_detector.pt",
    "ball": BASE_DIR / "models" / "ball_detector_model.pt",
    "court": BASE_DIR / "models" / "court_keypoint_detector.pt",
}


def parse_args():
    parser = argparse.ArgumentParser(description="CourtSight video annotation demo")
    parser.add_argument("input_video", help="Path to an input video")
    parser.add_argument(
        "--output_video",
        default=str(BASE_DIR / "output_videos" / "annotated.mp4"),
        help="Path for the annotated output video",
    )
    parser.add_argument("--cache_dir", default=str(BASE_DIR / "stubs"))
    parser.add_argument("--stub_path", dest="cache_dir", help=argparse.SUPPRESS)
    parser.add_argument("--no_cache", action="store_true", help="Disable detection caches")
    parser.add_argument("--frame_skip", type=int, default=1)
    parser.add_argument("--target_width", type=int, default=1280)
    parser.add_argument("--max_frames", type=int, default=None)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda", "mps"), default="cpu")
    return parser.parse_args()


def resolve_device(requested):
    if requested == "cpu":
        return "cpu"
    if requested == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is not available")
        return "cuda"
    if requested == "mps":
        if not hasattr(torch.backends, "mps") or not torch.backends.mps.is_available():
            raise RuntimeError("MPS was requested but is not available")
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def model_paths_from_environment():
    return {
        "player": Path(os.environ.get("COURTSIGHT_PLAYER_MODEL", DEFAULT_MODELS["player"])).resolve(),
        "ball": Path(os.environ.get("COURTSIGHT_BALL_MODEL", DEFAULT_MODELS["ball"])).resolve(),
        "court": Path(os.environ.get("COURTSIGHT_COURT_MODEL", DEFAULT_MODELS["court"])).resolve(),
    }


def validate_inputs(video_path, model_paths):
    if not video_path.is_file():
        raise FileNotFoundError(f"Input video not found: {video_path}")
    missing = [f"{name}: {path}" for name, path in model_paths.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError("Required model files are missing:\n" + "\n".join(missing))


def cache_path(cache_dir, cache_key, label):
    return str(Path(cache_dir) / f"{cache_key[:20]}-{label}.pkl")


def run(args):
    input_video = Path(args.input_video).resolve()
    output_video = Path(args.output_video).resolve()
    model_paths = model_paths_from_environment()
    validate_inputs(input_video, model_paths)
    device = resolve_device(args.device)

    print("CourtSight supported demo")
    print(f"Input: {input_video}")
    print(f"Device: {device}")
    print("Scope: player tracks, observed ball detections, court keypoints")

    frames, metadata = read_video(
        str(input_video),
        max_frames=args.max_frames,
        frame_skip=args.frame_skip,
        target_width=args.target_width if args.target_width > 0 else None,
        return_metadata=True,
    )
    if not frames:
        raise ValueError("The input video contained no readable frames")

    settings = {
        "frame_skip": args.frame_skip,
        "target_width": args.target_width,
        "max_frames": args.max_frames,
    }
    analysis_key = build_analysis_cache_key(input_video, model_paths.values(), settings)
    use_cache = not args.no_cache
    print(f"Cache key: {analysis_key[:20]} (enabled={use_cache})")

    player_tracker = PlayerTracker(str(model_paths["player"]), device=device)
    ball_tracker = BallTracker(str(model_paths["ball"]), device=device)
    court_detector = CourtKeypointDetector(str(model_paths["court"]), device=device)

    print("STEP 1/3: Detecting and tracking players")
    player_tracks = player_tracker.get_object_tracks(
        frames,
        read_from_stub=use_cache,
        stub_path=cache_path(args.cache_dir, analysis_key, "players"),
        cache_key=analysis_key,
    )
    print("STEP 2/3: Detecting observed ball positions")
    ball_detections = ball_tracker.get_object_tracks(
        frames,
        read_from_stub=use_cache,
        stub_path=cache_path(args.cache_dir, analysis_key, "ball"),
        cache_key=analysis_key,
    )
    print("STEP 3/3: Detecting court keypoints")
    court_keypoints = court_detector.get_court_keypoints(
        frames,
        read_from_stub=use_cache,
        stub_path=cache_path(args.cache_dir, analysis_key, "court"),
        cache_key=analysis_key,
    )

    output_frames = PlayerTracksDrawer().draw(frames, player_tracks)
    output_frames = BallTracksDrawer().draw(output_frames, ball_detections)
    output_frames = CourtKeypointDrawer().draw(output_frames, court_keypoints)
    output_frames = FrameNumberDrawer().draw(output_frames)

    if len(output_frames) != len(frames):
        raise RuntimeError(
            f"Annotation frame loss: input={len(frames)}, output={len(output_frames)}"
        )

    save_video(output_frames, str(output_video), fps=metadata.output_fps)
    print(
        f"Complete: {len(output_frames)} frames at {metadata.output_fps:.3f} FPS -> {output_video}"
    )
    return {
        "output_path": str(output_video),
        "frame_count": len(output_frames),
        "fps": metadata.output_fps,
        "cache_key": analysis_key,
    }


def main():
    run(parse_args())


if __name__ == "__main__":
    main()
