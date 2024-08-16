import os
import sys
from PIL import Image
import numpy as np

def find_shaded_header_line(image_np):
    """Find the bottom of the shaded horizontal line indicating the end of the header."""
    height, width, _ = image_np.shape
    for i in range(height):
        # Detect transition from white to shaded line (gray or darker pixels)
        if np.any(image_np[i, :] < [220, 220, 220]):
            # Scan downward until we pass the shaded line (can check for a dip in brightness)
            while i < height and np.any(image_np[i, :] < [220, 220, 220]):
                i += 1
            return i
    return 0

def find_black_footer_start(image_np):
    """Find the start of the black footer at the bottom of the image."""
    height, width, _ = image_np.shape
    for i in range(height - 1, -1, -1):
        # Look for a continuous section of dark pixels (footer)
        if np.all(image_np[i, :] < [50, 50, 50]):  # Footer line threshold
            # Scan upward until we leave the black area
            while i >= 0 and np.all(image_np[i, :] < [50, 50, 50]):
                i -= 1
            return i + 1
    return height

def remove_header_footer(image):
    """Removes the header and footer based on specific visual markers."""
    image_np = np.array(image)

    # Convert image to RGB if it has an alpha channel
    if image.mode == 'RGBA':
        image_np = image.convert('RGB')
        image_np = np.array(image_np)

    height, width, _ = image_np.shape

    # Detect the end of the header (just below the shaded line)
    header_end = find_shaded_header_line(image_np)

    # Detect the start of the footer (just above the black footer)
    footer_start = find_black_footer_start(image_np)

    # Crop the image to remove the header and footer
    cropped_image = image.crop((0, header_end, width, footer_start))

    return cropped_image

def save_temp_images(image_paths):
    """Remove headers and footers from images and save them with a '_temp' postfix."""
    temp_image_paths = []
    for image_path in image_paths:
        img = Image.open(image_path)
        img = remove_header_footer(img)
        
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
