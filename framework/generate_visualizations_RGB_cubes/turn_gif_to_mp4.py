import os
from moviepy.editor import VideoFileClip


def compress_gifs_to_mp4(input_dir, output_dir, target_resolution=(320, 240), target_bitrate="500k"):
    """
    Converts and compresses all GIF files in the input directory to MP4 format.

    Args:
        input_dir (str): Path to the directory containing GIF files.
        output_dir (str): Path to the directory to save compressed MP4 files.
        target_resolution (tuple): Target resolution for the output video (width, height).
        target_bitrate (str): Target bitrate for the output video (e.g., "500k" for 500kbps).
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.gif'):
            gif_path = os.path.join(input_dir, filename)
            mp4_filename = os.path.splitext(filename)[0] + '.mp4'
            mp4_path = os.path.join(output_dir, mp4_filename)

            print(f"Converting and compressing {filename} to {mp4_filename}...")
            try:
                clip = VideoFileClip(gif_path)

                # Resize video and write with lower bitrate
                clip_resized = clip.resize(newsize=target_resolution)
                clip_resized.write_videofile(
                    mp4_path,
                    codec="libx264",
                    audio=False,  # GIFs usually have no audio
                    bitrate=target_bitrate
                )
                clip_resized.close()
                print(f"Saved {mp4_filename} to {output_dir}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")


if __name__ == "__main__":
    # Replace these paths with your directories
    input_directory = "validation_green"
    output_directory = "validation_green_mp4"

    # Set target resolution and bitrate for compression
    target_resolution = (320, 240)  # Adjust to lower resolution for smaller size
    target_bitrate = "500k"  # Adjust bitrate for more compression

    compress_gifs_to_mp4(input_directory, output_directory, target_resolution, target_bitrate)
