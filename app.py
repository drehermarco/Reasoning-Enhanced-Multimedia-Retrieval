from tkinter import *
from customtkinter import *
import ollama
import os
import shutil
import subprocess
import pandas as pd
import re
from clip_searcher import ClipSearcher
from threading import Thread
from PIL import Image, ImageTk

class App(CTk):
    def __init__(self):
        super().__init__()
        self.model = "No model selected"
        self.options = ["No model selected", "llama3.2-vision", "test_llm", "modded_deepseek", "modded_mistral", "modded_llama3.2"]
        self.client = ollama.Client()
        self.chat_history = []
        self.queries = []
        self.dataset = None
        self.initUI()

    def on_app_close(self):
        try:
            print("Cleaning up before exit...")
            if hasattr(self, "client"):
                self.client.close()  # If supported by ollama.Client
                print("Closed Ollama client.")
        except Exception as e:
            print(f"Error closing Ollama client: {e}")
        finally:
            self.destroy()


    def initUI(self):
        self.title("Reasoning Enhanced Multimedia Retrieval")
        self.geometry("1000x500")
        self.config(bg="#212121")  # Set background color for the whole window

        self.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="equal")
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1, uniform="equal")

        # Unified Text Frame
        self.text_frame = CTkFrame(self, corner_radius=12, fg_color="#2E2E2E", border_color="#3A3A3A", border_width=1)
        self.text_frame.grid(row=0, column=0, columnspan=3, rowspan=4, sticky="nsew", padx=20, pady=20)

        # Grid inside the frame for cleaner control
        self.text_frame.grid_rowconfigure(0, weight=4)
        self.text_frame.grid_rowconfigure(1, weight=0)
        self.text_frame.grid_rowconfigure(2, weight=1)
        self.text_frame.grid_columnconfigure(0, weight=1)

        # Output Textbox (readonly display)
        self.out_textbox = CTkTextbox(self.text_frame, fg_color="#3A3A3A", font=("Arial", 14), text_color="#EAEAEA", wrap="word")
        self.out_textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        self.out_textbox.configure(state="disabled")

        # Divider
        self.divider = CTkFrame(self.text_frame, height=2, fg_color="#555555", corner_radius=1)
        self.divider.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))

        # Input Textbox
        self.input_field = CTkTextbox(self.text_frame, fg_color="#3A3A3A", text_color="#FFFFFF", height=100, font=("Arial", 13), wrap="word")
        self.input_field.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Submit Frame for Button
        self.submit_frame = CTkFrame(self, corner_radius=12, fg_color="transparent")
        self.submit_frame.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=20, pady=20)

        self.submit_button = CTkButton(self.submit_frame, text="Submit", fg_color="#4CAF50", hover_color="#45a049", text_color="#FFFFFF",
                    corner_radius=8, font=("Arial", 14, "bold"), height=50, command=self.submit_query)
        self.submit_button.pack(fill="both", expand=True, padx=10, pady=10)

        # Option Frame
        self.option_frame = CTkFrame(self, corner_radius=12, fg_color="#333333", border_color="#D3D3D3")
        self.option_frame.grid(row=0, column=3, rowspan=6, sticky="nsew", padx=20, pady=20)
        
        self.option_label = CTkLabel(self.option_frame, text="Options:", font=("Arial", 16, "bold"))
        self.option_label.pack(pady=10) 

        # Option Menu Divider 1
        self.divider = CTkFrame(self.option_frame, height=2, fg_color="#D3D3D3")
        self.divider.pack(fill="x", pady=(10, 5))

        # Adding Models
        self.model_add_label = CTkLabel(self.option_frame, text="Click here to add a model:", font=("Arial", 14, "bold"))
        self.model_add_label.pack(pady=10) 

        self.add_Button = CTkButton(self.option_frame, text="Add a Model", command=self.add_model)
        self.add_Button.pack(pady=10)

        # Option Menu Divider 2
        self.divider = CTkFrame(self.option_frame, height=2, fg_color="#D3D3D3")
        self.divider.pack(fill="x", pady=(10, 5))

        # Model Selection
        self.model_select_label = CTkLabel(self.option_frame, text="Select a model:", font=("Arial", 14, "bold"))
        self.model_select_label.pack(pady=10) 

        self.select_window = CTkOptionMenu(self.option_frame, values=self.options, command=self.select_model)
        self.select_window.pack(pady=10)

        # Option Menu Divider 3
        self.divider = CTkFrame(self.option_frame, height=2, fg_color="#D3D3D3")
        self.divider.pack(fill="x", pady=(10, 5))

        self.model_add_label = CTkLabel(self.option_frame, text="Click here to see Top 9 results:", font=("Arial", 14, "bold"))
        self.model_add_label.pack(pady=10)

        self.view_gallery_btn = CTkButton(self.option_frame, text="View Gallery (Top 9)",
                                  command=self._open_gallery_window)
        self.view_gallery_btn.pack(pady=10)

        # Shortcut Keys
        self.input_field.bind("<Return>", lambda e: self.submit_query())
        self.protocol("WM_DELETE_WINDOW", self.on_app_close)

    def stream_model_response(self, query):
        self.chat_history.append({"role": "user", "content": query})
        try:
            response = ""
            for chunk in self.client.chat(model=self.model, messages=self.chat_history, stream=True):
                part = chunk['message']['content']
                response += part
                self.out_textbox.insert("end", part)
                self.out_textbox.see("end")
                self.update_idletasks()
            # Append assistant response to history
            self.chat_history.append({"role": "assistant", "content": response})
            # Only keep lines that look like numbered sub-queries, and strip the numbering
            self.queries = [
                re.sub(r"^\d+\.\s*", "", line.strip())
                for line in response.strip().splitlines()
                if re.match(r"^\d+\.\s*", line.strip())
            ]
            print("Queries:", self.queries)
        except Exception as e:
            self.out_textbox.insert("end", f"\nError: {e}\n")
        finally:
            self.out_textbox.configure(state="disabled")

    def _save_images_from_df(self, df):
        temp_dir = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(temp_dir, exist_ok=True)

        for i, row in df.iterrows():
            image_path = os.path.join("../clipse/photos/images/", os.path.basename(row['image']))
            if image_path and os.path.exists(image_path):
                filename = os.path.basename(image_path)
                dest_path = os.path.join(temp_dir, filename)
                shutil.copy(image_path, dest_path)

    def clear_temp_folder(self, name):
        temp_dir = os.path.join(os.path.dirname(__file__), name)
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # remove file or link
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # remove folder recursively
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")

    def _process_multihop_query(self, query):
        # Step 1: Generate sub-queries from LLM
        self.stream_model_response(query)

        # Step 2: Ensure searcher is available
        if not hasattr(self, "searcher"):
            from clip_searcher import ClipSearcher
            self.searcher = ClipSearcher("../clipse/index/images.json")

        # Step 3: Collect images from each sub-query
        all_dfs = []
        for q in self.queries:
            if q:
                df = self.searcher.query(q, top_k=100)
                all_dfs.append(df)

        if not all_dfs:
            self.out_textbox.insert("end", "\nNo sub-query results.\n")
            return

        # Combine all image rows (deduplicated by image path)
        combined_df = pd.concat(all_dfs).drop_duplicates(subset="image").reset_index(drop=True)

        # Step 4: Save all top images from combined results
        self._save_images_from_df(combined_df)

        # Step 5: Build index once over temp folder
        def run_build_index():
            command = ["uv", "run", "build_index.py", "temp"]
            subprocess.run(command)

        run_build_index()

        # Step 6: Load new index once
        self.searcher = ClipSearcher("./index/temp.json")

        # Step 7: Final retrieval from updated index
        final_df = self.searcher.query(query, top_k=25)

        # Cleanup old results
        self.clear_temp_folder("index")

        # Step 8: Show results
        self._display_clip_results(query, final_df)

    def _display_clip_results(self, query, df):
        self.last_df = df  # Save for image display
        self.out_textbox.configure(state="normal")
        self.out_textbox.delete("1.0", "end")
        self.out_textbox.insert("end",
            f"Top matches for “{query}”\n\n{df.to_string(index=False)}\n")
        self.out_textbox.configure(state="disabled")
        #self._display_first_image_from_temp()

    def _open_gallery_window(self):
        if not hasattr(self, "last_df") or self.last_df.empty:
            return

        top_df = self.last_df.head(9)
        temp_dir = os.path.join(os.path.dirname(__file__), "temp")

        # Create the new Toplevel window
        win = CTkToplevel(self)
        win.title("Gallery View")
        win.geometry("600x600")

        # Use a grid of 3x3 thumbnails
        for i, (_, row) in enumerate(top_df.iterrows()):
            img_path = os.path.join(temp_dir, os.path.basename(row["image"]))
            if os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    img.thumbnail((180, 180))
                    tk_img = CTkImage(light_image=img, dark_image=img, size=img.size)

                    label = CTkLabel(win, image=tk_img, text="")
                    label.image = tk_img  # prevent garbage collection
                    label.grid(row=i // 3, column=i % 3, padx=10, pady=10)
                except Exception as e:
                    print(f"Failed to load {img_path}: {e}")
            
    def submit_query(self):
        self.out_textbox.configure(state="normal")
        query = self.input_field.get("0.0", "end").strip()
        self.out_textbox.delete("0.0", "end")

        if not query:
            self.out_textbox.insert("0.0", "Please enter a query.")
            self.out_textbox.configure(state="disabled")
            return

        if self.model == "No model selected":
            self.out_textbox.insert("0.0", "Please select a model.")
            self.out_textbox.configure(state="disabled")
            return

        Thread(target=self._process_multihop_query, args=(query,), daemon=True).start()

    def add_model(self):
        dialog = CTkInputDialog(text="Type in the name of the model.\n (You need to have a local version of your LLM):", title="Add a model")
        res = dialog.get_input()
        if (res != ""):
            self.options.append(res)
            self.select_window.configure(values=self.options)

    def select_model(self, value):
        self.model = value

app = App()
app.mainloop()