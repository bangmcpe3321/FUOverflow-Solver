import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import threading
import queue
import time
import re
import requests
from PIL import Image
import getpass
import google.generativeai as genai

# --- Constants and Configuration ---
CONFIG_FILE = "config.txt"
DOWNLOAD_DIRECTORY = "downloaded_images"

# --- Core Logic from test.py and AI.py ---

def download_file_with_retry(image_url, filepath, cookies, headers, max_retries, retry_delay, log_queue):
    """Downloads a file with a retry mechanism and logs progress to a queue."""
    filename = os.path.basename(filepath)
    for attempt in range(max_retries):
        try:
            response = requests.get(image_url, cookies=cookies, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            # FIXED: Added "DOWNLOADER:" prefix
            log_queue.put(f"DOWNLOADER:[SUCCESS] Downloaded {filename}\n")
            return True
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            # FIXED: Added "DOWNLOADER:" prefix
            log_queue.put(f"DOWNLOADER:[ATTEMPT {attempt + 1}/{max_retries}] Failed for {filename}. Error: {e}\n")
            if attempt + 1 < max_retries:
                time.sleep(retry_delay)
            else:
                # FIXED: Added "DOWNLOADER:" prefix
                log_queue.put(f"DOWNLOADER:[FAILURE] All {max_retries} attempts failed for {filename}.\n")
    return False

def parse_url_pattern(url):
    """Uses regex to extract the base name and attachment ID from a URL."""
    pattern = re.compile(r"/([^/]+)\.(\d+)/?$")
    match = pattern.search(url)
    if match:
        return match.group(1), int(match.group(2))
    return None, None

def get_answer_from_image_with_gemini(image_path, prompt, api_key):
    """Sends an image and prompt to the Gemini model."""
    try:
        genai.configure(api_key=api_key)
        img = Image.open(image_path)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content([prompt, img])
        return response.text, None
    except Exception as e:
        return None, f"An error occurred while processing {os.path.basename(image_path)}: {e}"

# --- GUI Application Class ---

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FUOverflow image downloader")
        self.geometry("800x600")

        self.log_queue = queue.Queue()

        self.tabControl = ttk.Notebook(self)
        self.downloader_tab = ttk.Frame(self.tabControl)
        self.processor_tab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.downloader_tab, text='Image Downloader')
        self.tabControl.add(self.processor_tab, text='Gemini Processor')
        self.tabControl.pack(expand=1, fill="both")

        self.create_downloader_widgets()
        self.create_processor_widgets()
        
        self.after(100, self.process_log_queue)

    def process_log_queue(self):
        """Processes messages from the log queue to update GUI."""
        while not self.log_queue.empty():
            try:
                message = self.log_queue.get_nowait()
                if "DOWNLOADER:" in message:
                    self.downloader_log.insert(tk.END, message.replace("DOWNLOADER:", ""))
                    self.downloader_log.see(tk.END)
                elif "PROCESSOR:" in message:
                    self.processor_log.insert(tk.END, message.replace("PROCESSOR:", ""))
                    self.processor_log.see(tk.END)
            except queue.Empty:
                pass
        self.after(100, self.process_log_queue)

    # --- Downloader Tab Methods ---
    def create_downloader_widgets(self):
        frame = self.downloader_tab
        input_frame = ttk.LabelFrame(frame, text="Configuration", padding=(10, 5))
        input_frame.pack(padx=10, pady=10, fill="x")
        ttk.Label(input_frame, text="Start URL:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_url_entry = ttk.Entry(input_frame, width=60)
        self.start_url_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(input_frame, text="Total Files:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.total_files_entry = ttk.Entry(input_frame)
        self.total_files_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(input_frame, text="xf_user Cookie:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.xf_user_entry = ttk.Entry(input_frame, width=60)
        self.xf_user_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(input_frame, text="xf_session Cookie:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.xf_session_entry = ttk.Entry(input_frame, show="*")
        self.xf_session_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        input_frame.columnconfigure(1, weight=1)
        self.download_button = ttk.Button(frame, text="Start Download", command=self.start_download_thread)
        self.download_button.pack(padx=10, pady=5)
        log_frame = ttk.LabelFrame(frame, text="Log", padding=(10, 5))
        log_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.downloader_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15)
        self.downloader_log.pack(fill="both", expand=True)
        
    def start_download_thread(self):
        self.download_button.config(state="disabled")
        self.downloader_log.delete(1.0, tk.END)
        thread = threading.Thread(target=self.run_downloader, daemon=True)
        thread.start()

    def run_downloader(self):
        start_url = self.start_url_entry.get()
        total_files_str = self.total_files_entry.get()
        xf_user = self.xf_user_entry.get()
        xf_session = self.xf_session_entry.get()

        if not all([start_url, total_files_str, xf_user, xf_session]):
            messagebox.showerror("Error", "All fields are required.")
            self.download_button.config(state="normal")
            return
            
        try:
            total_files = int(total_files_str)
        except ValueError:
            messagebox.showerror("Error", "Total files must be a valid number.")
            self.download_button.config(state="normal")
            return

        base_name, start_id = parse_url_pattern(start_url)
        if base_name is None:
            messagebox.showerror("Error", "Could not parse the URL pattern.")
            self.download_button.config(state="normal")
            return
            
        self.log_queue.put(f"DOWNLOADER:Parsed URL. Base name: {base_name}, Start ID: {start_id}\n")
        self.log_queue.put(f"DOWNLOADER:--- Starting Batch Download ---\n")

        if not os.path.exists(DOWNLOAD_DIRECTORY):
            os.makedirs(DOWNLOAD_DIRECTORY)
        
        cookies = {'xf_user': xf_user, 'xf_session': xf_session}
        headers = {'User-Agent': 'Mozilla/5.0'}

        successful, skipped = 0, 0
        failed_urls = []
        
        for i in range(total_files):
            current_id = start_id + i
            file_url = f"https://fuoverflow.com/attachments/{base_name}.{current_id}/"
            filename = f"{base_name}.{current_id}.webp"
            filepath = os.path.join(DOWNLOAD_DIRECTORY, filename)
            
            if os.path.exists(filepath):
                self.log_queue.put(f"DOWNLOADER:[SKIPPED] {filename} already exists.\n")
                skipped += 1
                continue

            # NEW: Log the attempt before it happens
            self.log_queue.put(f"DOWNLOADER:Downloading {filename} from {file_url}\n")
                
            if download_file_with_retry(file_url, filepath, cookies, headers, 4, 5, self.log_queue):
                successful += 1
            else:
                failed_urls.append(file_url)
            time.sleep(0.5)

        self.log_queue.put(f"DOWNLOADER:\n--- Download Finished ---\n")
        self.log_queue.put(f"DOWNLOADER:Summary: {successful} downloaded, {skipped} skipped, {len(failed_urls)} failed.\n")
        
        if failed_urls:
            self.log_queue.put("DOWNLOADER:Failed URLs:\n" + "\n".join(failed_urls) + "\n")
            
        self.download_button.config(state="normal")

    # --- Processor Tab Methods ---
    def create_processor_widgets(self):
        frame = self.processor_tab
        input_frame = ttk.LabelFrame(frame, text="Configuration", padding=(10, 5))
        input_frame.pack(padx=10, pady=10, fill="x")
        ttk.Label(input_frame, text="Gemini API Key:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.api_key_entry = ttk.Entry(input_frame, width=60, show="*")
        self.api_key_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        if os.path.exists(CONFIG_FILE) and os.path.getsize(CONFIG_FILE) > 0:
            with open(CONFIG_FILE, "r") as f:
                self.api_key_entry.insert(0, f.read().strip())

        ttk.Label(input_frame, text="Image Directory:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.dir_path_entry = ttk.Entry(input_frame, width=60)
        self.dir_path_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        browse_button = ttk.Button(input_frame, text="Browse...", command=self.browse_directory)
        browse_button.grid(row=1, column=2, padx=5, pady=5)
        input_frame.columnconfigure(1, weight=1)
        self.process_button = ttk.Button(frame, text="Start Processing", command=self.start_processing_thread)
        self.process_button.pack(padx=10, pady=5)
        log_frame = ttk.LabelFrame(frame, text="Log", padding=(10, 5))
        log_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.processor_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15)
        self.processor_log.pack(fill="both", expand=True)

    def browse_directory(self):
        path = filedialog.askdirectory()
        if path:
            self.dir_path_entry.delete(0, tk.END)
            self.dir_path_entry.insert(0, path)

    def start_processing_thread(self):
        self.process_button.config(state="disabled")
        self.processor_log.delete(1.0, tk.END)
        thread = threading.Thread(target=self.run_processor, daemon=True)
        thread.start()

    def run_processor(self):
        api_key = self.api_key_entry.get()
        image_dir = self.dir_path_entry.get()

        if not api_key or not image_dir:
            messagebox.showerror("Error", "API Key and Image Directory are required.")
            self.process_button.config(state="normal")
            return

        if not os.path.isdir(image_dir):
            messagebox.showerror("Error", "The provided path is not a valid directory.")
            self.process_button.config(state="normal")
            return

        with open(CONFIG_FILE, "w") as f:
            f.write(api_key)
            
        output_txt_path = "all_questions_and_answers.txt"
        prompt = "Read the attached image. Extract every question you can find and provide a correct, concise answer for each one."
        valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')

        self.log_queue.put(f"PROCESSOR:Processing images in: {image_dir}\n")
        self.log_queue.put(f"PROCESSOR:Results will be saved to: {output_txt_path}\n\n")

        try:
            with open(output_txt_path, "a", encoding="utf-8") as output_file:
                for filename in sorted(os.listdir(image_dir)):
                    if filename.lower().endswith(valid_extensions):
                        full_path = os.path.join(image_dir, filename)
                        self.log_queue.put(f"PROCESSOR:Processing image: {filename}...\n")
                        
                        answer, error = get_answer_from_image_with_gemini(full_path, prompt, api_key)
                        
                        output_file.write(f"--- Question Source: {filename} ---\n")
                        if error:
                            self.log_queue.put(f"PROCESSOR:  -> ERROR: {error}\n")
                            output_file.write(f"An error occurred: {error}\n")
                        else:
                            self.log_queue.put(f"PROCESSOR:  -> Success.\n")
                            output_file.write(answer.strip() + "\n")
                        
                        output_file.write("\n" + "="*80 + "\n\n")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.process_button.config(state="normal")
            return

        self.log_queue.put(f"PROCESSOR:\nBatch processing complete. Results appended to '{output_txt_path}'.\n")
        self.process_button.config(state="normal")


if __name__ == "__main__":
    app = App()
    app.mainloop()
