PLUGINS = {
    "lock computer": "import subprocess; subprocess.run('rundll32.exe user32.dll,LockWorkStation')",
}

def check_plugin(user_input: str) -> str | None:
    user_input_lower = user_input.lower().strip()
    for trigger, code in PLUGINS.items():
        if trigger in user_input_lower or user_input_lower in trigger:
            return code
    return None

def run_plugin(code: str) -> bool:
    try:
        exec(code)
        return True
    except Exception as e:
        print(f"Plugin Error: {e}")
        return False
