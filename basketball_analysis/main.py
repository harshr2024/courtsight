import os
import argparse
# Force CPU mode to avoid CUDA errors
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Disable CUDA
from utils import read_video, save_video
from trackers import PlayerTracker, BallTracker
from team_assigner import TeamAssigner
from court_keypoint_detector import CourtKeypointDetector
from ball_aquisition import BallAquisitionDetector
from pass_and_interception_detector import PassAndInterceptionDetector
from tactical_view_converter import TacticalViewConverter
from speed_and_distance_calculator import SpeedAndDistanceCalculator
from drawers import (
    PlayerTracksDrawer, 
    BallTracksDrawer,
    CourtKeypointDrawer,
    TeamBallControlDrawer,
    FrameNumberDrawer,
    PassInterceptionDrawer,
    TacticalViewDrawer,
    SpeedAndDistanceDrawer
)
from configs import(
    STUBS_DEFAULT_PATH,
    PLAYER_DETECTOR_PATH,
    BALL_DETECTOR_PATH,
    COURT_KEYPOINT_DETECTOR_PATH,
    OUTPUT_VIDEO_PATH
)

def parse_args():
    parser = argparse.ArgumentParser(description='Basketball Video Analysis')
    parser.add_argument('input_video', type=str, help='Path to input video file')
    parser.add_argument('--output_video', type=str, default=OUTPUT_VIDEO_PATH, 
                        help='Path to output video file')
    parser.add_argument('--stub_path', type=str, default=STUBS_DEFAULT_PATH,
                        help='Path to stub directory')
    parser.add_argument('--frame_skip', type=int, default=2,
                        help='Process every Nth frame (default: 2 = every other frame, 1 = all frames)')
    parser.add_argument('--target_width', type=int, default=1280,
                        help='Resize frames to this width for faster processing (default: 1280, 0 = no resize)')
    parser.add_argument('--max_frames', type=int, default=None,
                        help='Maximum number of frames to process (for testing, default: all)')
    return parser.parse_args()

def main():
    args = parse_args()
    
    try:
        print(f"Starting analysis with optimizations:")
        print(f"  Frame skip: {args.frame_skip} (process every {args.frame_skip} frame(s))")
        if args.target_width > 0:
            print(f"  Target width: {args.target_width}px")
        if args.max_frames:
            print(f"  Max frames: {args.max_frames}")
        
        # Read Video with optimizations
        print("Loading video frames...")
        if not os.path.exists(args.input_video):
            raise FileNotFoundError(f"Input video not found: {args.input_video}")
        
        video_frames = read_video(
            args.input_video, 
            max_frames=args.max_frames,
            frame_skip=args.frame_skip,
            target_width=args.target_width if args.target_width > 0 else None
        )
        print(f"Loaded {len(video_frames)} frames")
        
        if len(video_frames) == 0:
            raise ValueError("No frames loaded from video. Check video file format and path.")
    except Exception as e:
        print(f"Error loading video: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    ## Initialize Tracker
    print("Initializing trackers...")
    try:
        print("  Loading player detector...")
        player_tracker = PlayerTracker("models/player_detector.pt")
        print("  ✓ Player detector loaded")
    except Exception as e:
        print(f"  ✗ Error loading player detector: {e}")
        raise
    
    try:
        print("  Loading ball detector...")
        ball_tracker = BallTracker("models/ball_detector_model.pt")
        print("  ✓ Ball detector loaded")
    except Exception as e:
        print(f"  ✗ Error loading ball detector: {e}")
        raise

    ## Initialize Keypoint Detector
    try:
        print("  Loading court keypoint detector...")
        court_keypoint_detector = CourtKeypointDetector("models/court_keypoint_detector.pt")
        print("  ✓ Court keypoint detector loaded")
    except Exception as e:
        print(f"  ✗ Error loading court keypoint detector: {e}")
        raise

    # Run Detectors
    try:
        print("=" * 60)
        print("STEP 1/8: Detecting players...")
        print("=" * 60)
        player_tracks = player_tracker.get_object_tracks(video_frames,
                                           read_from_stub=True,
                                           stub_path=os.path.join(args.stub_path, 'player_track_stubs.pkl')
                                          )
        print(f"✓ Completed: Detected players in {len(player_tracks)} frames")
    except Exception as e:
        print(f"✗ Error detecting players: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    try:
        print("=" * 60)
        print("STEP 2/8: Detecting ball...")
        print("=" * 60)
        ball_tracks = ball_tracker.get_object_tracks(video_frames,
                                                     read_from_stub=True,
                                                     stub_path=os.path.join(args.stub_path, 'ball_track_stubs.pkl')
                                                    )
        print(f"✓ Completed: Detected ball in {len(ball_tracks)} frames")
    except Exception as e:
        print(f"✗ Error detecting ball: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    ## Run KeyPoint Extractor
    try:
        print("=" * 60)
        print("STEP 3/8: Detecting court keypoints...")
        print("=" * 60)
        court_keypoints_per_frame = court_keypoint_detector.get_court_keypoints(video_frames,
                                                                        read_from_stub=True,
                                                                        stub_path=os.path.join(args.stub_path, 'court_key_points_stub.pkl')
                                                                        )
        print(f"✓ Completed: Detected court keypoints in {len(court_keypoints_per_frame)} frames")
    except Exception as e:
        print(f"✗ Error detecting court keypoints: {e}")
        import traceback
        traceback.print_exc()
        raise

    # Remove Wrong Ball Detections
    print("=" * 60)
    print("STEP 4/8: Cleaning ball tracks...")
    print("=" * 60)
    ball_tracks = ball_tracker.remove_wrong_detections(ball_tracks)
    # Interpolate Ball Tracks
    ball_tracks = ball_tracker.interpolate_ball_positions(ball_tracks)
    print("✓ Completed: Ball tracks cleaned and interpolated")
   

    # Assign Player Teams
    print("=" * 60)
    print("STEP 5/8: Assigning teams...")
    print("=" * 60)
    team_assigner = TeamAssigner()
    player_assignment = team_assigner.get_player_teams_across_frames(video_frames,
                                                                    player_tracks,
                                                                    read_from_stub=True,
                                                                    stub_path=os.path.join(args.stub_path, 'player_assignment_stub.pkl')
                                                                    )
    print("✓ Completed: Teams assigned")

    # Ball Acquisition
    print("=" * 60)
    print("STEP 6/8: Detecting ball possession...")
    print("=" * 60)
    ball_aquisition_detector = BallAquisitionDetector()
    ball_aquisition = ball_aquisition_detector.detect_ball_possession(player_tracks,ball_tracks)
    print("✓ Completed: Ball possession detected")

    # Detect Passes
    print("=" * 60)
    print("STEP 7/8: Detecting passes and interceptions...")
    print("=" * 60)
    pass_and_interception_detector = PassAndInterceptionDetector()
    passes = pass_and_interception_detector.detect_passes(ball_aquisition,player_assignment)
    interceptions = pass_and_interception_detector.detect_interceptions(ball_aquisition,player_assignment)
    print("✓ Completed: Passes and interceptions detected")

    # Tactical View
    print("=" * 60)
    print("STEP 8/8: Calculating tactical view and speeds...")
    print("=" * 60)
    tactical_view_converter = TacticalViewConverter(
        court_image_path="./images/basketball_court.png"
    )

    court_keypoints_per_frame = tactical_view_converter.validate_keypoints(court_keypoints_per_frame)
    tactical_player_positions = tactical_view_converter.transform_players_to_tactical_view(court_keypoints_per_frame,player_tracks)

    # Speed and Distance Calculator
    speed_and_distance_calculator = SpeedAndDistanceCalculator(
        tactical_view_converter.width,
        tactical_view_converter.height,
        tactical_view_converter.actual_width_in_meters,
        tactical_view_converter.actual_height_in_meters
    )
    player_distances_per_frame = speed_and_distance_calculator.calculate_distance(tactical_player_positions)
    player_speed_per_frame = speed_and_distance_calculator.calculate_speed(player_distances_per_frame)
    print("✓ Completed: Tactical view and speeds calculated")

    # Draw output   
    print("=" * 60)
    print("RENDERING: Drawing annotations on video...")
    print("=" * 60)
    # Initialize Drawers
    player_tracks_drawer = PlayerTracksDrawer()
    ball_tracks_drawer = BallTracksDrawer()
    court_keypoint_drawer = CourtKeypointDrawer()
    team_ball_control_drawer = TeamBallControlDrawer()
    frame_number_drawer = FrameNumberDrawer()
    pass_and_interceptions_drawer = PassInterceptionDrawer()
    tactical_view_drawer = TacticalViewDrawer()
    speed_and_distance_drawer = SpeedAndDistanceDrawer()
    
    print(f"Drawing on {len(video_frames)} frames...")

    ## Draw object Tracks
    output_video_frames = player_tracks_drawer.draw(video_frames, 
                                                    player_tracks,
                                                    player_assignment,
                                                    ball_aquisition)
    output_video_frames = ball_tracks_drawer.draw(output_video_frames, ball_tracks)

    ## Draw KeyPoints
    output_video_frames = court_keypoint_drawer.draw(output_video_frames, court_keypoints_per_frame)

    ## Draw Frame Number
    output_video_frames = frame_number_drawer.draw(output_video_frames)

    # Draw Team Ball Control
    output_video_frames = team_ball_control_drawer.draw(output_video_frames,
                                                        player_assignment,
                                                        ball_aquisition)

    # Draw Passes and Interceptions
    output_video_frames = pass_and_interceptions_drawer.draw(output_video_frames,
                                                             passes,
                                                             interceptions)
    
    # Speed and Distance Drawer
    output_video_frames = speed_and_distance_drawer.draw(output_video_frames,
                                                         player_tracks,
                                                         player_distances_per_frame,
                                                         player_speed_per_frame
                                                         )

    ## Draw Tactical View
    output_video_frames = tactical_view_drawer.draw(output_video_frames,
                                                    tactical_view_converter.court_image_path,
                                                    tactical_view_converter.width,
                                                    tactical_view_converter.height,
                                                    tactical_view_converter.key_points,
                                                    tactical_player_positions,
                                                    player_assignment,
                                                    ball_aquisition,
                                                    )

    # Save video
    print("=" * 60)
    print("Saving output video...")
    print("=" * 60)
    if not output_video_frames or len(output_video_frames) == 0:
        raise ValueError("No frames to save - output video frames list is empty")
    print(f"Saving {len(output_video_frames)} frames to {args.output_video}")
    save_video(output_video_frames, args.output_video)
    print(f"✓ Analysis complete! Output saved to: {args.output_video}")

if __name__ == '__main__':
    main()
    