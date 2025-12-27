import os
import subprocess
import sys

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=== ARCHON AI LAUNCHER ===\n")
    print("Select mode:")
    print("  [1] Terminal Mode - Classic CLI interface")
    print("  [2] Background Mode - Hotkey overlay (Ctrl+Shift+K)")
    print()
    
    choice = input("Enter choice (1/2): ").strip()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if choice == "1":
        subprocess.run([sys.executable, os.path.join(base_dir, "main.py")])
    elif choice == "2":
        subprocess.run([sys.executable, os.path.join(base_dir, "app", "overlay.py")])
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
