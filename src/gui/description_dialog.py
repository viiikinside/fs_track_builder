import tkinter as tk
from tkinter import ttk

class DescriptionDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Track Description")
        self.dialog.geometry("400x300")
        
        # Make dialog modal and keep on top
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.attributes('-topmost', True)
        
        # Protocol for window close button (X)
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        
        # Center the dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'+{x}+{y}')
        
        # Description input
        self.label = ttk.Label(self.dialog, 
            text="Please describe this track (features, characteristics, difficulty):")
        self.label.pack(pady=10)
        
        self.text_input = tk.Text(self.dialog, height=10, width=40)
        self.text_input.pack(pady=10, padx=10)
        self.text_input.focus_set()  # Set focus to text input
        
        # Buttons
        self.button_frame = ttk.Frame(self.dialog)
        self.button_frame.pack(pady=10)
        
        self.save_button = ttk.Button(
            self.button_frame, 
            text="Save", 
            command=self.save
        )
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(
            self.button_frame, 
            text="Cancel", 
            command=self.cancel
        )
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Bind enter key to save
        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.force_cancel())
        
        self.description = None
        
    def save(self):
        self.description = self.text_input.get("1.0", tk.END).strip()
        if self.description:  # Only close if description is not empty
            self.dialog.destroy()
        else:
            tk.messagebox.showwarning(
                "Empty Description", 
                "Please enter a description before saving."
            )
        
    def cancel(self):
        self.description = None
        self.dialog.destroy()
        
    def force_cancel(self):
        """Force cancel and exit program"""
        self.description = None
        self.dialog.quit()  # Stop mainloop
        self.dialog.destroy() 