import os
import sys
from PIL import Image, ImageChops
import numpy as np

def remove_non_white_background(image):
    """Removes parts of the image with a non-white background (headers and footers)."""
    # Convert to RGB if image has an alpha channel
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    
    image_np = np.array(image)
    
    # Create a mask where True indicates white pixels
    white_mask = np.all(image_np == [255, 255, 255], axis=-1)
    
    # Find the bounding box of the non-white area (top and bottom only)
    non_white_rows = np.where(~white_mask.any(axis=1))[0]
    
    if non_white_rows.size == 0:
        # If the image is completely white, return None
        return None
    
    # Determine top and bottom bounds
    top = non_white_rows[0]
    bottom = non_white_rows[-1]

    # Crop the image to remove the non-white header and footer
    return image.crop((0, top, image.width, bottom + 1))

def find_overlap(img1, img2):
    """Finds the vertical overlap between the bottom of img1 and the top of img2."""
    img1_bw = img1.convert('1')  # Convert to black-and-white
    img2_bw = img2.convert('1')  # Convert to black-and-white

    img1_np = np.array(img1_bw)
    img2_np = np.array(img2_bw)

    h1 = img1_np.shape[0]
    h2 = img2_np.shape[0]
    
    max_overlap = min(h1, h2)
    min_diff = float('inf')
    best_offset = 0

    # Compare bottom part of img1 with top part of img2
    for offset in range(1, max_overlap):
        diff = np.sum(np.bitwise_xor(img1_np[-offset:], img2_np[:offset]))
        if diff < min_diff:
            min_diff = diff
            best_offset = offset

    return best_offset

def stitch_images(images):
    stitched_image = images[0]

    for i in range(1, len(images)):
        overlap = find_overlap(stitched_image, images[i])
        new_height = stitched_image.height + images[i].height - overlap
        stitched_result = Image.new('RGB', (stitched_image.width, new_height))
        stitched_result.paste(stitched_image, (0, 0))
        stitched_result.paste(images[i], (0, stitched_image.height - overlap))
        stitched_image = stitched_result

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

    image_objs = []
    for image in images:
        img = Image.open(image)
        # Remove non-white headers and footers
        img = remove_non_white_background(img)
        if img:
            image_objs.append(img)

    if not image_objs:
        print("All images were completely white or had no significant content after removing non-white backgrounds.")
        sys.exit(1)

    stitched_image = stitch_images(image_objs)
    
    stitched_image.save('stitched_image.png')
    print("Saved stitched image as 'stitched_image.png'")

if __name__ == "__main__":
    main(sys.argv)
