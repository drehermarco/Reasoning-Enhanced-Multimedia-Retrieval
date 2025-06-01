import os
import random
import shutil

def copy_random_pictures(source_folder, dest_folder, num_pictures_to_copy):
    """
    Randomly selects a specified number of pictures from a source folder
    and copies them to a destination folder.

    Args:
        source_folder (str): The path to the folder containing the pictures.
        dest_folder (str): The path to the folder where pictures will be copied.
        num_pictures_to_copy (int): The number of pictures to select and copy.
    """
    if not os.path.exists(source_folder):
        print(f"Error: Source folder '{source_folder}' not found.")
        return

    if not os.path.exists(dest_folder):
        try:
            os.makedirs(dest_folder)
            print(f"Created destination folder: '{dest_folder}'")
        except OSError as e:
            print(f"Error creating destination folder '{dest_folder}': {e}")
            return

    all_files = [f for f in os.listdir(source_folder)
                 if os.path.isfile(os.path.join(source_folder, f))]

    # Optional: Filter for common image file extensions
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
    pictures = [f for f in all_files if f.lower().endswith(image_extensions)]

    if not pictures:
        print(f"No picture files found in '{source_folder}'.")
        return

    if len(pictures) < num_pictures_to_copy:
        print(f"Warning: Source folder contains only {len(pictures)} pictures, "
              f"which is less than the requested {num_pictures_to_copy}. "
              f"Copying all available pictures.")
        num_pictures_to_copy = len(pictures)

    selected_pictures = random.sample(pictures, num_pictures_to_copy)

    copied_count = 0
    for picture_name in selected_pictures:
        source_path = os.path.join(source_folder, picture_name)
        destination_path = os.path.join(dest_folder, picture_name)
        try:
            shutil.copy2(source_path, destination_path) # copy2 preserves metadata
            copied_count += 1
        except Exception as e:
            print(f"Error copying '{picture_name}': {e}")

    print(f"Successfully copied {copied_count} out of {num_pictures_to_copy} selected pictures to '{dest_folder}'.")

if __name__ == "__main__":
    # --- Configuration ---
    source_directory = "C:/Users/karlz/IdeaProjects/sandbox/media"
    destination_directory = "C:/Users/karlz/GitProjects/randomimage"
    number_of_pictures = 5000
    # --- End Configuration ---
    copy_random_pictures(source_directory, destination_directory, number_of_pictures)