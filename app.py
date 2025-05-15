from tkinter import *
from customtkinter import *
import ollama
import sys
from threading import Thread


class App(CTk):
    def __init__(self):
        super().__init__()
        self.model = "No model selected"
        self.options = ["No model selected", "rem", "llama3.2-vision"]
        self.client = ollama.Client()
        self.chat_history = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        self.initUI()

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

        # Maybe insert pictures here later
        self.temp_label = CTkLabel(self.option_frame, text="TODO:\n Insert image display here", font=("Arial", 14, "bold"))
        self.temp_label.pack(pady=10) 

        # Shortcut Keys
        self.input_field.bind("<Return>", lambda e: self.submit_query())

    
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
        except Exception as e:
            self.out_textbox.insert("end", f"\nError: {e}\n")
        finally:
            self.out_textbox.configure(state="disabled")

            
    def submit_query(self):
        self.out_textbox.configure(state="normal")
        query = self.input_field.get("0.0", "end").strip()
        self.input_field.delete("0.0", "end")
        self.out_textbox.delete("0.0", "end")

        if self.model == "No model selected":
            self.out_textbox.insert("0.0", "Please select a model.")
            self.out_textbox.configure(state="disabled")
            return

        Thread(target=self.stream_model_response, args=(query,), daemon=True).start()

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
