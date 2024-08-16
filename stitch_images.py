import os
import sys
from PIL import Image
import numpy as np

def remove_non_white_header_footer(image):
    """Removes the top (header) and bottom (footer) parts of the image that have a non-white background."""
    image_np = np.array(image)

    # Convert image to RGB if it has an alpha channel
    if image.mode == 'RGBA':
        image_np = image.convert('RGB')
        image_np = np.array(image_np)

    # Create a mask where True indicates white pixels
    white_mask = np.all(image_np == [255, 255, 255], axis=-1)

    # Find the first non-white row from the top
    top_crop = 0
    for i in range(white_mask.shape[0]):
        if not white_mask[i].all():
            top_crop = i
            break

    # Find the first non-white row from the bottom
    bottom_crop = white_mask.shape[0]
    for i in range(white_mask.shape[0] - 1, -1, -1):
        if not white_mask[i].all():
            bottom_crop = i
            break

    # Crop the image to remove the non-white header and footer
    cropped_image = image.crop((0, top_crop, image.width, bottom_crop + 1))

    return cropped_image

def save_temp_images(image_paths):
    """Remove non-white headers and footers from images and save them with a '_temp' postfix."""
    temp_image_paths = []
    for image_path in image_paths:
        img = Image.open(image_path)
        img = remove_non_white_header_footer(img)
        
        # Generate new filename with _temp postfix
        base, ext = os.path.splitext(image_path)
        temp_image_path = f"{base}_temp{ext}"
        img.save(temp_image_path)
        temp_image_paths.append(temp_image_path)
    
    return temp_image_paths

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
        image_paths = sorted([os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.lower().endswith('.png')])
    else:
        image_paths = args[1:]

    if not image_paths:
        print("No images found to process.")
        sys.exit(1)

    # Remove headers and footers and save the images with a '_temp' postfix
    temp_image_paths = save_temp_images(image_paths)

    # Load the temp images for stitching
    image_objs = [Image.open(temp_image) for temp_image in temp_image_paths]

    stitched_image = stitch_images(image_objs)
    
    stitched_image.save('stitched_image.png')
    print("Saved stitched image as 'stitched_image.png'")

if __name__ == "__main__":
    main(sys.argv)
