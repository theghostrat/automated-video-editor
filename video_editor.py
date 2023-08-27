import argparse
from video_editor_functions import trim_video, apply_transition, stabilize_video


def main():
    parser = argparse.ArgumentParser(description='Automated video editor for vloggers')
    parser.add_argument('input_video', type=str, help='path to input video')
    parser.add_argument('output_video', type=str, help='path to output video')
    parser.add_argument('--trim', action='store_true', help='enable automated video trimming')
    parser.add_argument('--transition', type=str, help='type of automated transition to apply')
    parser.add_argument('--stabilize', action='store_true', help='enable automatic video stabilization')
    args = parser.parse_args()

    if args.trim:
        trimmed_video = trim_video(args.input_video)
    else:
        trimmed_video = args.input_video

    if args.transition:
        transitioned_video = apply_transition(trimmed_video, args.transition)
    else:
        transitioned_video = trimmed_video

    if args.stabilize:
        stabilized_video = stabilize_video(transitioned_video)
    else:
        stabilized_video = transitioned_video

    stabilized_video.export(args.output_video, fps=30, codec='libx264')


if __name__ == '__main__':
    main()
