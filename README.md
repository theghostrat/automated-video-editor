# Automated-video-editor


Welcome to the Automated Video Editor repository! This is a cool tool that helps you edit your videos without needing to be a pro at video editing. If you've just started using GitHub, don't worry – we'll guide you through the basics.
What is Automated Video Editor?

Automated Video Editor is a program that makes video editing simpler. It's like having a helper that can trim your videos, add smooth transitions, and even make shaky videos look steady.
Getting Started

Follow these steps to start using the Automated Video Editor:

Download the Code
    
    git clone https://github.com/theghostrat/automated-video-editor

Install Dependencies

    pip install opencv-python moviepy
    cd automated-video-editor

Usage:

    python video_editor.py input_video.mp4 output_video.mp4 --trim --transition fade --stabilize

    Replace input_video.mp4 with the name of your video file and output_video.mp4 with the name you want for your edited video.

You can use different options like --trim, --transition, and --stabilize to choose what the Automated Video Editor should do.

Find Your Edited Video

After the script runs, your edited video will be saved as output_video.mp4 in the same folder where you have the code.

Examples

Here are a few examples of how to use the Automated Video Editor:

  To trim a video and stabilize it:

    python video_editor.py input_video.mp4 output_video.mp4 --trim --stabilize

  To trim a video and add a fade transition:


    python video_editor.py input_video.mp4 output_video.mp4 --trim --transition fade

  To add a slide transition and stabilize a video:


    python video_editor.py input_video.mp4 output_video.mp4 --transition slide --stabilize
