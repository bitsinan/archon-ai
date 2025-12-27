import tkinter as tk
import threading
import keyboard
import google.generativeai as genai
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompts import SYSTEM_PROMPT
from plugins import check_plugin, run_plugin

class ArchonOverlay:
    def __init__(self, model):
        self.model = model
        self.root = None
        self.is_visible = False
        
    def create_window(self):
        self.root = tk.Tk()
        self.root.title("ARCHON AI")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)
        self.root.overrideredirect(True)
        
        screen_width = self.root.winfo_screenwidth()
        
        window_width = 600
        window_height = 50
        x = (screen_width - window_width) // 2
        y = 10
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg='#1a1a2e')
        
        frame = tk.Frame(self.root, bg='#1a1a2e', padx=10, pady=10)
        frame.pack(fill='both', expand=True)
        
        self.label = tk.Label(frame, text="ARCHON >", fg='#00ff88', bg='#1a1a2e', font=('Consolas', 12, 'bold'))
        self.label.pack(side='left')
        
        self.entry = tk.Entry(frame, bg='#16213e', fg='#ffffff', font=('Consolas', 12), 
                              insertbackground='#00ff88', relief='flat', width=50)
        self.entry.pack(side='left', fill='x', expand=True, padx=(10, 0))
        self.entry.bind('<Return>', self.on_submit)
        self.entry.bind('<Escape>', self.hide_window)
        
        self.root.withdraw()
        
    def show_window(self):
        if self.root and not self.is_visible:
            self.root.deiconify()
            self.entry.delete(0, tk.END)
            self.entry.focus_force()
            self.is_visible = True
            
    def hide_window(self, event=None):
        if self.root and self.is_visible:
            self.root.withdraw()
            self.is_visible = False
            
    def toggle_window(self):
        if self.is_visible:
            self.hide_window()
        else:
            self.show_window()
            
    def on_submit(self, event=None):
        command = self.entry.get().strip()
        if not command:
            return
            
        self.hide_window()
        
        thread = threading.Thread(target=self.execute_command, args=(command,))
        thread.start()
        
    def execute_command(self, command):
        plugin_code = check_plugin(command)
        if plugin_code:
            run_plugin(plugin_code)
            return
            
        try:
            response = self.model.generate_content(f"{SYSTEM_PROMPT}\n\nTask: {command}")
            code = response.text.replace("```python", "").replace("```", "").strip()
            self.root.after(0, lambda: self.show_confirmation(code))
        except Exception as e:
            print(f"Error: {e}")
            
    def show_confirmation(self, code):
        confirm_window = tk.Toplevel(self.root)
        confirm_window.title("ARCHON")
        confirm_window.attributes('-topmost', True)
        confirm_window.overrideredirect(True)
        confirm_window.configure(bg='#1a1a2e')
        
        screen_width = self.root.winfo_screenwidth()
        window_width = 400
        window_height = 50
        x = (screen_width - window_width) // 2
        y = 10
        confirm_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        main_frame = tk.Frame(confirm_window, bg='#1a1a2e', padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)
        
        label = tk.Label(main_frame, text="Execute?", fg='#00ff88', bg='#1a1a2e', font=('Consolas', 11, 'bold'))
        label.pack(side='left')
        
        code_visible = [False]
        code_frame = None
        
        def on_yes():
            confirm_window.destroy()
            try:
                exec(code)
            except Exception as e:
                print(f"Runtime Error: {e}")
        
        def on_no():
            confirm_window.destroy()
            
        def toggle_code():
            nonlocal code_frame
            if code_visible[0]:
                if code_frame:
                    code_frame.destroy()
                confirm_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
                code_visible[0] = False
            else:
                code_frame = tk.Frame(confirm_window, bg='#16213e')
                code_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
                code_text = tk.Text(code_frame, bg='#16213e', fg='#ffffff', font=('Consolas', 9), relief='flat', wrap='word', height=15)
                code_text.insert('1.0', code)
                code_text.config(state='disabled')
                code_text.pack(fill='both', expand=True, padx=5, pady=5)
                confirm_window.geometry(f"{window_width}x350+{x}+{y}")
                code_visible[0] = True
        
        code_btn = tk.Button(main_frame, text="</>", command=toggle_code, bg='#444466', fg='#ffffff', font=('Consolas', 9), width=3, relief='flat')
        code_btn.pack(side='left', padx=(15, 5))
        
        yes_btn = tk.Button(main_frame, text="Y", command=on_yes, bg='#00ff88', fg='#000000', font=('Consolas', 10, 'bold'), width=3, relief='flat')
        yes_btn.pack(side='left', padx=5)
        
        no_btn = tk.Button(main_frame, text="N", command=on_no, bg='#ff4444', fg='#ffffff', font=('Consolas', 10, 'bold'), width=3, relief='flat')
        no_btn.pack(side='left', padx=5)
        
        confirm_window.bind('y', lambda e: on_yes())
        confirm_window.bind('Y', lambda e: on_yes())
        confirm_window.bind('n', lambda e: on_no())
        confirm_window.bind('N', lambda e: on_no())
        confirm_window.bind('<Escape>', lambda e: on_no())
        confirm_window.bind('c', lambda e: toggle_code())
        confirm_window.focus_force()
            
    def run(self):
        self.create_window()
        keyboard.add_hotkey('ctrl+shift+k', lambda: self.root.after(0, self.toggle_window))
        print("[ARCHON] Background mode active. Press Ctrl+Shift+K to open overlay.")
        print("[ARCHON] Press Ctrl+C to exit.")
        self.root.mainloop()

def get_model(api_key):
    genai.configure(api_key=api_key)
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            if 'flash' in m.name:
                return genai.GenerativeModel(m.name)
    return None

def main():
    print("=== ARCHON AI - Background Mode ===\n")
    api_key = input("Enter API Key: ").strip()
    
    model = get_model(api_key)
    if not model:
        print("Error: Could not connect to AI model.")
        return
        
    print("[ARCHON] Connected to AI model.")
    
    overlay = ArchonOverlay(model)
    overlay.run()

if __name__ == "__main__":
    main()
