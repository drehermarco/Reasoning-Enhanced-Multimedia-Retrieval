import os
from PIL import Image

def downscale_images(source_folder, target_folder, size=(480, 480)):
    # Create the target folder if it doesn't exist
    os.makedirs(target_folder, exist_ok=True)

    # Supported image file extensions
    supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')

    for filename in os.listdir(source_folder):
        if filename.lower().endswith(supported_extensions):
            source_path = os.path.join(source_folder, filename)
            target_path = os.path.join(target_folder, filename)

            try:
                with Image.open(source_path) as img:
                    # Resize and save
                    resized_img = img.resize(size, Image.LANCZOS)
                    resized_img.save(target_path)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

# Example usage
source = "C:/university/FS25/CTDS/clipse/full/images"
target = "C:/university/FS25/CTDS/clipse/photos/images"
downscale_images(source, target)
