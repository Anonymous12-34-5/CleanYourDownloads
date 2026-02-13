import customtkinter as ctk
import os
import shutil
import threading
import time
from tkinter import filedialog, messagebox

# --- Configuration ---
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".ico", ".svg"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv", ".rtf"],
    "Installers": [".exe", ".msi", ".bat", ".sh", ".apk"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
    "Video": [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv"],
    "Audio": [".mp3", ".wav", ".flac", ".m4a", ".aac"]
}

class ModernCleaningApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("CleanMyDownloads By Ved")
        self.geometry("600x450")
        self.resizable(False, False)

        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=0) # Main content rows

        # --- UI Elements ---
        
        # 1. Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="CleanMyDownloads By Ved", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack()
        
        self.subtitle_label = ctk.CTkLabel(self.header_frame, text="Organize your files instantly.", font=ctk.CTkFont(size=14), text_color="gray")
        self.subtitle_label.pack()

        # 2. Folder Selection
        self.folder_frame = ctk.CTkFrame(self)
        self.folder_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.folder_label = ctk.CTkLabel(self.folder_frame, text="Target Folder ( LINK TO YOUR DOWNLOADS FOLDER ) :", font=ctk.CTkFont(size=12, weight="bold"))
        self.folder_label.pack(anchor="w", padx=15, pady=(10, 0))

        self.path_entry = ctk.CTkEntry(self.folder_frame, placeholder_text="Path to folder...", width=350)
        self.path_entry.pack(side="left", padx=(15, 10), pady=(5, 15), expand=True, fill="x")
        self.path_entry.insert(0, os.path.expanduser("~\\Downloads"))

        self.browse_btn = ctk.CTkButton(self.folder_frame, text="Browse", width=80, command=self.browse_folder)
        self.browse_btn.pack(side="right", padx=(0, 15), pady=(5, 15))

        # 3. Action Area
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        self.clean_btn = ctk.CTkButton(self.action_frame, text="CLEAN FILES", font=ctk.CTkFont(size=16, weight="bold"), height=50, command=self.start_cleaning_thread)
        self.clean_btn.pack(fill="x")

        # 4. Status & Progress
        self.status_label = ctk.CTkLabel(self, text="Ready to clean.", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=3, column=0, padx=20, pady=(5, 0))

        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal")
        self.progress_bar.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.progress_bar.set(0)

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.path_entry.get())
        if folder:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)

    def start_cleaning_thread(self):
        folder_path = self.path_entry.get()
        if not os.path.exists(folder_path):
            messagebox.showerror("Error", "Folder not found!")
            return

        self.clean_btn.configure(state="disabled", text="CLEANING...")
        self.progress_bar.set(0)
        
        threading.Thread(target=self.clean_logic, args=(folder_path,), daemon=True).start()

    def clean_logic(self, folder_path):
        try:
            # Filter only files, not folders
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            total_files = len(files)

            if total_files == 0:
                self.update_status("Folder is already empty!", 1.0)
                time.sleep(1) # Let user see message
                self.reset_ui()
                return

            moved_count = 0
            
            for index, filename in enumerate(files):
                # Calculate progress (0.0 to 1.0)
                progress = (index + 1) / total_files
                self.update_status(f"Moving: {filename}...", progress)
                
                # Logic
                file_path = os.path.join(folder_path, filename)
                _, extension = os.path.splitext(filename)
                extension = extension.lower()

                for type_name, extensions_list in FILE_TYPES.items():
                    if extension in extensions_list:
                        target_folder = os.path.join(folder_path, type_name)
                        if not os.path.exists(target_folder):
                            os.makedirs(target_folder)
                        
                        try:
                            final_path = os.path.join(target_folder, filename)
                            # Handle duplicate names by renaming
                            if os.path.exists(final_path):
                                base, ext = os.path.splitext(filename)
                                new_name = f"{base}_{int(time.time())}{ext}"
                                final_path = os.path.join(target_folder, new_name)
                                
                            shutil.move(file_path, final_path)
                            moved_count += 1
                        except Exception as e:
                            print(f"Error moving {filename}: {e}")
                        break
                
                time.sleep(0.05) # Artificial delay for smooth animation

            self.update_status(f"Success! Organized {moved_count} files.", 1.0)
            messagebox.showinfo("Done", f"Cleanup Complete!\nFiles Moved: {moved_count}")

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.reset_ui()

    def update_status(self, text, progress):
        self.status_label.configure(text=text)
        self.progress_bar.set(progress)

    def reset_ui(self):
        self.clean_btn.configure(state="normal", text="CLEAN FILES")
        self.status_label.configure(text="Ready to clean.")
        self.progress_bar.set(0)

if __name__ == "__main__":
    app = ModernCleaningApp()
    app.mainloop()
