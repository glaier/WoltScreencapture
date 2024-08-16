import os
import sys
from PIL import Image
import numpy as np

def find_overlap(img1, img2):
    """Finds the vertical overlap between the bottom of img1 and the top of img2."""
    img1_np = np.array(img1)
    img2_np = np.array(img2)

    # Convert to grayscale if they are not already
    if img1_np.ndim == 3:
        img1_np = np.mean(img1_np, axis=2).astype(np.uint8)
    if img2_np.ndim == 3:
        img2_np = np.mean(img2_np, axis=2).astype(np.uint8)

    # Calculate the region of img1 to compare
    h1 = img1_np.shape[0]
    h2 = img2_np.shape[0]
    
    max_overlap = min(h1, h2)
    min_diff = float('inf')
    best_offset = 0

    # Compare bottom part of img1 with top part of img2
    for offset in range(1, max_overlap):
        diff = np.sum(np.abs(img1_np[-offset:] - img2_np[:offset]))
        if diff < min_diff:
            min_diff = diff
            best_offset = offset

    return best_offset

def stitch_images(images):
    stitched_image = images[0]

    for i in range(1, len(images)):
        overlap = find_overlap(stitched_image, images[i])
        stitched_image = Image.new('RGB', (stitched_image.width, stitched_image.height + images[i].height - overlap))
        stitched_image.paste(images[i-1], (0, 0))
        stitched_image.paste(images[i], (0, images[i-1].height - overlap))

    return stitched_image

def main(args):
    if len(args) < 2:
        print("Usage: python stitch_images.py <image1.png> <image2.png> ...")
        print("       or python stitch_images.py <folder_path>")
        sys.exit(1)

    if os.path.isdir(args[1]):
        folder_path = args[1]
        images = sorted([os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.lower().endswith('.png')])
    else:
        images = args[1:]

    if not images:
        print("No images found to stitch.")
        sys.exit(1)

    image_objs = [Image.open(image) for image in images]

    stitched_image = stitch_images(image_objs)
    
    stitched_image.save('stitched_image.png')
    print("Saved stitched image as 'stitched_image.png'")

if __name__ == "__main__":
    main(sys.argv)
