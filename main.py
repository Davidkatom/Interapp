import os
import tkinter as tk
import winsound
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import ttk
import threading
import merger
import os
import sys


class DragDropListbox(tk.Listbox):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.bind('<Button-1>', self.start_drag)
        self.bind('<B1-Motion>', self.drag)
        self.bind('<ButtonRelease-1>', self.drop)
        self.bind('<Button-3>', self.show_context_menu)  # Bind right-click event

    def show_context_menu(self, event):
        self.select_clear(0, tk.END)
        self.select_set(self.nearest(event.y))
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="Remove", command=self.remove_selected_item)
        context_menu.post(event.x_root, event.y_root)

    def remove_selected_item(self):
        selected = self.curselection()
        if selected:
            self.delete(selected)
            self.update_backup()

    def start_drag(self, event):
        self.drag_start_index = self.nearest(event.y)

    def drag(self, event):
        current_index = self.nearest(event.y)

        if current_index != self.drag_start_index:
            self.swap(self.drag_start_index, current_index)
            self.drag_start_index = current_index

    def drop(self, event):
        self.drag_start_index = None

    def swap(self, a, b):
        items = list(self.get(0, tk.END))
        items[a], items[b] = items[b], items[a]

        self.delete(0, tk.END)
        self.insert(0, *items)
        self.update_backup()

    def update_backup(self):
        with open("backup.txt", "w") as file:
            for item in self.get(0, tk.END):
                file.write(item + "\n")


class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title('Drag and Drop Files')
        self.geometry('800x600')
        self.configure(bg='white')

        self.main_frame = ttk.Frame(self, padding=(10, 10, 10, 10))
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.style = ttk.Style()
        self.style.configure('Disabled.TEntry', foreground='grey')

        # Add export location label, entry, and button
        self.export_location_frame = ttk.Frame(self.main_frame)
        self.export_location_frame.pack(fill=tk.X, pady=(10, 0))

        self.load_txt_button = ttk.Button(self.main_frame, text='Load files from backup', command=self.load_backup)
        self.load_txt_button.pack(pady=(10, 0))

        self.export_location_label = ttk.Label(self.export_location_frame, text='Export location:')
        self.export_location_label.pack(side=tk.LEFT)

        self.export_location_var = tk.StringVar()
        self.export_location_entry = ttk.Entry(self.export_location_frame, textvariable=self.export_location_var,
                                               state='readonly', style='Disabled.TEntry')
        self.export_location_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.export_button = ttk.Button(self.export_location_frame, text='...', command=self.export_files)
        self.export_button.pack(side=tk.LEFT, padx=(5, 0))

        # Listbox and Scrollbar
        self.listbox_frame = ttk.Frame(self.main_frame)
        self.listbox_frame.pack(expand=True, fill=tk.BOTH, pady=(0, 0))

        self.listbox = DragDropListbox(self.listbox_frame, selectmode=tk.EXTENDED, bg='white', font=('Arial', 12),
                                       relief='flat')
        self.listbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.scrollbar = ttk.Scrollbar(self.listbox_frame, orient='vertical', command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        # button to clear the listbox
        self.clear_button = ttk.Button(self.main_frame, text='Clear', command=self.clear_listbox)
        self.clear_button.pack(side=tk.TOP, pady=(0, 0))

        self.progressbar = ttk.Progressbar(self.main_frame, mode='determinate')
        self.progressbar.pack(fill=tk.X, pady=(10, 0))

        self.button = ttk.Button(self.main_frame, text='Build', command=self.build)
        self.button.pack()

        self.setup_drag_and_drop()


        #start by creating a message box with a button that asks if the user wants to load the backup
        self.prompt_load_backup()
    def prompt_load_backup(self):
        #check if backup.txt exists and not empty
        if os.path.isfile("backup.txt") and os.path.getsize("backup.txt") == 0:
            return
        if messagebox.askyesno("Load backup", "Do you want to load the backup?"):
            self.load_backup()
    def export_files(self):
        export_file = filedialog.asksaveasfilename(defaultextension=".mp3",
                                                   filetypes=[("Text files", "*.mp3"), ("All files", "*.*")])
        self.export_location_var.set(export_file)
        # Add your export logic here

    # a function the checks if all the files in the listbox exist
    def check_files(self):
        for file in self.listbox.get(0, tk.END):
            if not os.path.isfile(file):
                # if file not exist pop a message box
                messagebox.showerror("Error", "File " + file + " does not exist")
                return False
        return True

    def build(self):
        export_file = self.export_location_var.get()
        if not self.check_files():
            return
        if export_file == '':
            return
        # Reset the progress bar
        self.progressbar.config(value=0, maximum=len(self.listbox.get(0, tk.END)) - 2)

        # Start a new thread to process the audio files
        build_thread = threading.Thread(target=self.build_thread, args=(export_file,))
        build_thread.start()

        # Lock the GUI

    def build_thread(self, export_file):
        self.lock_gui()
        # Pass the progress_callback function to the combine_audio_files function
        merger.combine_audio_files(list(self.listbox.get(0, tk.END)), export_file,
                                   progress_callback=self.progress_callback)

        # Unlock the GUI
        self.unlock_gui()
        self.after(0, self.build_complete)

    def build_complete(self):
        winsound.MessageBeep()  # You can also use winsound.PlaySound() to play a custom sound
        messagebox.showinfo("Build Complete", "The build operation has been completed successfully.")

    def progress_callback(self, current):
        self.after(0, self.update_progressbar, current)

    def update_progressbar(self, current):
        self.progressbar.config(value=current)

    def lock_gui(self):
        self.export_button.config(state=tk.DISABLED)
        self.export_location_entry.config(state='disabled', style='Disabled.TEntry')
        self.listbox.config(state=tk.DISABLED, bg='grey')
        self.button.config(state=tk.DISABLED)

    def unlock_gui(self):
        self.export_button.config(state=tk.NORMAL)
        self.export_location_entry.config(state='readonly', style='TEntry')
        self.listbox.config(state=tk.NORMAL, bg='white')
        self.button.config(state=tk.NORMAL)

    def add_files(self):
        file_paths = filedialog.askopenfilenames()
        for file_path in file_paths:
            self.add_file(file_path)

    def drag_and_drop(self, event):
        data = event.data
        file_paths = self.tk.splitlist(data)
        for file_path in file_paths:
            self.add_file(file_path)
        return event.action

    def update_backup(self):
        with open("backup.txt", "w") as file:
            for item in self.listbox.get(0, tk.END):
                file.write(item + "\n")

    def clear_listbox(self):
        self.listbox.delete(0, tk.END)
        self.update_backup()

    def load_backup(self):
        if os.path.exists("backup.txt"):
            with open("backup.txt", "r") as file:
                for line in file:
                    self.add_file(line.strip())

    def add_file(self, file_path):
        # Check if file_path is already in the listbox
        if file_path in self.listbox.get(0, tk.END):
            return

        # Check if the file has an audio format
        audio_extensions = ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac']
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.txt':
            self.load_files_from_txt(file_path)
            return
        if file_extension not in audio_extensions:
            return

        self.listbox.insert(tk.END, file_path)
        self.update_backup()

    def setup_drag_and_drop(self):
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind('<<Drop>>', self.drag_and_drop)

    def load_files_from_txt(self, txt_file_path=None):
        self.listbox.delete(0, tk.END)
        if not txt_file_path:
            txt_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if txt_file_path:
            audio_files = merger.read_audio_files_from_txt(txt_file_path)
            for audio_file in audio_files:
                self.add_file(audio_file)


if __name__ == '__main__':
    app = App()
    app.mainloop()
