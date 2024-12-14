import os
from PIL import Image
import piexif
import glob

def clean_image_metadata(image_path):
    try:
        # Open the image
        image = Image.open(image_path)
        
        # Create a new image without metadata
        data = list(image.getdata())
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(data)
        
        # Save the image without metadata
        image_without_exif.save(image_path, format=image.format)
        print(f"Successfully cleaned metadata from {image_path}")
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")

def main():
    # Get all image files
    image_types = ('*.png', '*.jpg', '*.jpeg', '*.gif', '*.webp')
    image_files = []
    for type in image_types:
        image_files.extend(glob.glob(os.path.join('images', type)))
        image_files.extend(glob.glob(os.path.join('static', type)))

    if not image_files:
        print("No image files found")
        return

    print(f"Found {len(image_files)} image files")
    
    # Process each image
    for image_path in image_files:
        clean_image_metadata(image_path)

if __name__ == "__main__":
    main() 