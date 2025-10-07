import os
from PIL import Image
from moviepy.editor import VideoFileClip, concatenate_videoclips, clips_array
import cv2
import imageio
import numpy as np


def combine_gifs_to_video(folder_path, output_path):
    # Get all .gif files in the folder
    gif_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".gif")]

    if not gif_files:
        print("No GIF files found in the folder.")
        return

    # Load each GIF as a VideoFileClip
    video_clips = []
    for gif in gif_files:
        clip = VideoFileClip(gif)
        video_clips.append(clip)

    # Concatenate all the clips
    final_video = concatenate_videoclips(video_clips, method="compose")

    # Write the output video to a file
    final_video.write_videofile(output_path, codec="libx264", fps=24)

    print(f"Combined video saved as {output_path}")


def read_and_resize_gif(gif_path, height):
    """Read a GIF and resize its frames."""
    gif_reader = imageio.get_reader(gif_path, mode="I")
    frames = []
    for frame in gif_reader:
        # Resize frame
        original_height, original_width, _ = frame.shape
        width = int((height / original_height) * original_width)
        resized_frame = cv2.resize(frame, (width, height))
        frames.append(resized_frame)
    gif_reader.close()
    return frames


def combine_gifs_in_grid(folder_path, output_path, height=200):
    """Combine GIFs into a 2x5 grid and save as a video."""
    gif_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".gif")]

    if len(gif_files) < 15:
        print("Please provide at least 10 GIF files.")
        return

    # Load the first 10 GIFs and resize them
    gifs = [read_and_resize_gif(gif, height) for gif in gif_files[:15]]

    # Find the minimum frame count to sync all GIFs
    min_frames = min(len(gif) for gif in gifs)

    # Trim all GIFs to the minimum number of frames
    trimmed_gifs = [gif[:min_frames] for gif in gifs]

    print(trimmed_gifs[0][0].shape)

    # Stack GIFs into a 2x5 grid for each frame
    grid_frames = []
    for frame_idx in range(min_frames):
        row1 = np.hstack([trimmed_gifs[i][frame_idx] for i in range(5)])  # Wrap in a list
        row2 = np.hstack([trimmed_gifs[i][frame_idx] for i in range(5, 10)])  # Wrap in a list
        row3 = np.hstack([trimmed_gifs[i][frame_idx] for i in range(10, 15)])  # Wrap in a list
        # # Handle the last row with black frames
        # row3 = np.hstack([
        #     trimmed_gifs[i][frame_idx] if i < len(trimmed_gifs) else np.zeros(
        #         (trimmed_gifs[0][0].shape[0], trimmed_gifs[0][0].shape[1], 3), dtype=np.uint8
        #     )
        #     for i in range(8, 12)  # Total up to 12 slots in 3 rows
        # ])

        grid = np.vstack([row1, row2, row3])  # Wrap rows in a list
        grid_frames.append(grid)

    # Write the frames to a video
    height, width, _ = grid_frames[0].shape
    out = cv2.VideoWriter(output_path, 0, 24, (width, height))

    for frame in grid_frames:
        out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))  # Convert RGB to BGR for OpenCV

    out.release()
    print(f"Grid video saved as {output_path}")


# Example usage
folder_path = "output/validation_green"  # Replace with the folder path containing your GIFs
output_path = "output/validation_green/grid5x3_validation_RGB.mp4"  # The name of the output video
# combine_gifs_to_video(folder_path, output_path)
combine_gifs_in_grid(folder_path, output_path)
