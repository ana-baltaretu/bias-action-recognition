from PIL import Image
import os


def stack_images_vertically(folder_path, output_file):
    # List all PNG files in the folder
    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".png")]
    image_files.sort()  # Sort the files alphabetically

    # Open all images
    images = [Image.open(img) for img in image_files]

    # Calculate total height and max width for the output image
    total_height = sum(img.height for img in images)
    max_width = max(img.width for img in images)

    # Create a new blank image with the total height and max width
    stacked_image = Image.new("RGB", (max_width, total_height), (255, 255, 255))

    # Paste each image into the stacked image
    y_offset = 0
    for img in images:
        stacked_image.paste(img, (0, y_offset))
        y_offset += img.height

    # Save the stacked image
    stacked_image.save(output_file)
    print(f"Stacked image saved as {output_file}")


# Folder containing PNGs and output file path
input_folder = "../output/out_labels_from_validation/200-epochs/bouncing_plots"

# Stack images and save
stack_images_vertically(input_folder, "stacked_bouncing_200EP.pdf")
