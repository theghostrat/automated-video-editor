import cv2
import numpy as np
import moviepy.editor as mp
from moviepy.video.fx.all import CrossfadeClip, DissolveClip, WipeClip
from moviepy.video.compositing.concatenate import concatenate_videoclips


def stabilize_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)

    p0 = cv2.goodFeaturesToTrack(gray, mask=None, **feature_params)

    lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    old_gray = gray.copy()
    p0_old = p0.copy()
    mask = np.zeros_like(frame)

    for i in range(1, len(frame)):
        frame_gray = cv2.cvtColor(frame[i], cv2.COLOR_BGR2GRAY)

        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0_old, None, **lk_params)

        good_new = p1[st == 1]
        good_old = p0_old[st == 1]

        m = cv2.estimateAffine2D(good_old, good_new)[0]

        stabilized_frame = cv2.warpAffine(frame[i], m, (frame.shape[1], frame.shape[0]))

        old_gray = frame_gray.copy()
        p0_old = good_new.reshape(-1, 1, 2)

    return stabilized_frame

def trim_video(video_path):
    video = mp.VideoFileClip(video_path)

    segment_times = []
    previous_frame = None
    previous_gray = None
    min_segment_duration = 2  # in seconds
    max_segment_duration = 60  # in seconds
    for t in range(int(video.duration)):
        frame = cv2.cvtColor(np.array(video.get_frame(t)), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if (t - segment_times[-1][1]) > max_segment_duration:
            segment_times[-1][1] = t
        elif (t - segment_times[-1][0]) > min_segment_duration:
            diff = cv2.absdiff(gray, previous_gray)
            mean_diff = np.mean(diff)

            if (mean_diff < 30) and (previous_frame is not None):
                prev_edges = cv2.Canny(cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY), 100, 200)
                curr_edges = cv2.Canny(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 100, 200)
                flow = cv2.calcOpticalFlowFarneback(prev_edges, curr_edges, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                flow_mean = np.mean(flow)

                if flow_mean < 0.5:
                    segment_times[-1][1] = t

        if (len(segment_times) == 0) or (t > segment_times[-1][1]):
            segment_times.append([t, t])

        previous_frame = frame.copy()
        previous_gray = gray.copy()

    segments = [video.subclip(start, end) for start, end in segment_times]

    transitions = []
    for i in range(len(segments) - 1):
        transitions.append(apply_transition(segments[i], segments[i+1]))

    final_clip = segments[0]
    for i in range(len(transitions)):
        final_clip = final_clip.append(transitions[i])
        final_clip = final_clip.append(segments[i+1])

    stabilized_clip = final_clip.fl_image(stabilize_frame)
    
    output_path = video_path[:-4] + '_edited.mp4'
    stabilized_clip.write_videofile(output_path, fps=30)
    print(f'Video saved to {output_path}')

def apply_transition(clip1, clip2, transition_type):
    if transition_type == 'crossfade':
        duration = 1.0  # 1 second
    elif transition_type == 'dissolve':
        duration = 2.0  # 2 seconds
    elif transition_type == 'wipe':
        duration = 0.5  # half a second
    else:
        duration = 1.0  # default to 1 second
    
    if transition_type == 'crossfade':
        transition = CrossfadeClip(clip1, clip2, duration=duration)
    elif transition_type == 'dissolve':
        transition = DissolveClip(clip1, clip2, duration=duration)
    elif transition_type == 'wipe':
        transition = WipeClip(clip1, clip2, duration=duration)
    else:
        transition = CrossfadeClip(clip1, clip2, duration=duration)  # default to crossfade
    
    result = concatenate_videoclips([clip1, transition, clip2])
    
    return result

def stabilize_video(input_file, output_file):
    cap = cv2.VideoCapture(input_file)

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, 30.0, (width, height))

    prev_frame = None
    motion_estimator = cv2.optflow.createOptFlow_PCAFlow()

    for i in range(frame_count):
        ret, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_frame is None:
            out.write(frame)
            prev_frame = gray
            continue

        flow = motion_estimator.calc(prev_frame, gray, None)

        transform = np.float32([[1, 0, -flow[0, 2]], [0, 1, -flow[1, 2]]])

        stabilized = cv2.warpAffine(frame, transform, (width, height))

        out.write(stabilized)

        prev_frame = gray

    cap.release()
    out.release()
