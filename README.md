# Reasoning-Enhanced-Multimedia-Retrieval

## Requirements
- Python 3.11+
- Images for the search engine

## Setup

1. **Clone the Repositories**
   ```bash
   git clone https://github.com/drehermarco/Reasoning-Enhanced-Multimedia-Retrieval.git
   git clone https://github.com/stg7/clipse.git
   ```

2. **Create a Virtual Environment and Install Dependencies**
   ```bash
   cd Reasoning-Enhanced-Multimedia-Retrieval
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set Up the Search Engine**
   Follow the guide on the [clipse repository](https://github.com/stg7/clipse?tab=readme-ov-file) to set up the CLIP-based search engine.

   **Note:** You can use the `downscale.py` script in the `helper` directory to resize your images to 480x480, as required by CLIPSE.

4. **Expected Folder Structure After Setup**
   ```
   project-root/
   ├── clipse/
   └── Reasoning-Enhanced-Multimedia-Retrieval/
   ```

## Usage

1. **Run the Application**
   ```bash
   python app.py
   ```

2. **Interact with the Interface**
   Input queries and explore the multimedia retrieval capabilities enhanced by reasoning logic.

## Project Structure

- `app.py`: Main application script.
- `clip_searcher.py`: Handles retrieval logic using CLIP.
- `helper/`: Utilities including the downscale script.
- `requirements.txt`: Python dependencies.
- `Modelfile`: Model configuration file.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

Thanks to the creators of CLIPSE and open-source contributors whose tools this project builds upon.
