import os
import sys
from PIL import Image

def stitch_images(images):
    # Open images and determine the total width and maximum height
    image_objs = [Image.open(image) for image in images]
    widths, heights = zip(*(img.size for img in image_objs))

    total_width = sum(widths)
    max_height = max(heights)

    # Create a new blank image with the total width and max height
    stitched_image = Image.new('RGB', (total_width, max_height))

    # Paste each image into the stitched_image
    x_offset = 0
    for img in image_objs:
        stitched_image.paste(img, (x_offset, 0))
        x_offset += img.size[0]

    return stitched_image

def main(args):
    if len(args) < 2:
        print("Usage: python stitch_images.py <image1.png> <image2.png> ...")
        print("       or python stitch_images.py <folder_path>")
        sys.exit(1)

    # Check if the first argument is a directory
    if os.path.isdir(args[1]):
        folder_path = args[1]
        images = sorted([os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.lower().endswith('.png')])
    else:
        # Assume arguments are filenames
        images = args[1:]

    if not images:
        print("No images found to stitch.")
        sys.exit(1)

    # Stitch the images
    stitched_image = stitch_images(images)

    # Save the result
    stitched_image.save('stitched_image.png')
    print("Saved stitched image as 'stitched_image.png'")

if __name__ == "__main__":
    main(sys.argv)
