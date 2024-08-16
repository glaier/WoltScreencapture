from PIL import Image
import os
import numpy as np

def image_to_grayscale(image):
    """Convert an image to grayscale."""
    return image.convert('L')

def compute_overlap(img1, img2):
    """Compute the maximum overlap between two images."""
    img1_gray = image_to_grayscale(img1)
    img2_gray = image_to_grayscale(img2)

    width, height1 = img1_gray.size
    _, height2 = img2_gray.size

    max_overlap = 0
    best_overlap = 0

    for offset in range(-height2 + 1, height1):
        if offset < 0:
            img1_part = np.array(img1_gray.crop((0, -offset, width, height1)))
            img2_part = np.array(img2_gray.crop((0, 0, width, height2 + offset)))
        else:
            img1_part = np.array(img1_gray.crop((0, 0, width, height1 - offset)))
            img2_part = np.array(img2_gray.crop((0, offset, width, height2)))

        # Ensure parts are of the same size for comparison
        min_height = min(img1_part.shape[0], img2_part.shape[0])
        overlap = np.sum(img1_part[:min_height] == img2_part[:min_height])
        
        if overlap > max_overlap:
            max_overlap = overlap
            best_overlap = offset

    return best_overlap

def adjust_header(img2, img1, max_overlap):
    """Remove the header from the second image based on the maximum overlap."""
    img2_gray = image_to_grayscale(img2)
    width, height = img2_gray.size

    best_overlap = max_overlap
    previous_overlap = -1

    for top in range(height):
        img2_part = img2_gray.crop((0, top, width, height))
        current_overlap = compute_overlap(img1, img2_part)
        if current_overlap < max_overlap:
            img2 = img2.crop((0, top, width, height))
            break

    return img2

def adjust_footer(img1, img2, max_overlap):
    """Remove the footer from the first image based on the maximum overlap."""
    img1_gray = image_to_grayscale(img1)
    width, height = img1_gray.size

    best_overlap = max_overlap
    previous_overlap = -1

    for bottom in range(height):
        img1_part = img1_gray.crop((0, 0, width, height - bottom))
        current_overlap = compute_overlap(img1_part, img2)
        if current_overlap < max_overlap:
            img1 = img1.crop((0, 0, width, height - bottom))
            break

    return img1

def create_long_screenshot(folder_path, output_path):
    """Create a long screenshot by stitching together images."""
    image_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.png')])

    if not image_files:
        raise ValueError("No PNG files found in the directory.")

    images = [Image.open(os.path.join(folder_path, file)) for file in image_files]

    final_width = images[0].width
    total_height = 0

    adjusted_images = [images[0]]
    for i in range(1, len(images)):
        overlap = compute_overlap(adjusted_images[-1], images[i])
        img1, img2 = adjusted_images[-1], images[i]

        img2 = adjust_header(img2, img1, overlap)
        img1 = adjust_footer(img1, img2, overlap)

        adjusted_images[-1] = img1
        adjusted_images.append(img2)

    for img in adjusted_images:
        total_height += img.height

    long_screenshot = Image.new('RGB', (final_width, total_height))
    y_offset = 0
    for img in adjusted_images:
        long_screenshot.paste(img, (0, y_offset))
        y_offset += img.height

    long_screenshot.save(output_path)
    print(f"Long screenshot saved as {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python stitch_images.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    output_path = os.path.join(folder_path, 'long_screenshot.png')

    create_long_screenshot(folder_path, output_path)
