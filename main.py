import os
import sys
import google.generativeai as genai
from colorama import init, Fore, Style
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style as PromptStyle

from prompts import SYSTEM_PROMPT, COMMAND_LIST
from plugins import check_plugin, run_plugin

init(autoreset=True)

def print_system(text, color=Fore.GREEN):
    print(f"{color}[ARCHON AI] {text}{Style.RESET_ALL}")

def get_ai_model(api_key):
    try:
        genai.configure(api_key=api_key)
        print_system("Scanning available models...", Fore.CYAN)
        
        found_models = []
        target_model = ""

        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                found_models.append(m.name)
                if 'flash' in m.name and '1.5' in m.name:
                    target_model = m.name
        
        if not target_model and found_models:
            target_model = found_models[0]

        if not target_model:
            print_system("Error: No suitable model found.", Fore.RED)
            return None

        print_system(f"Model Selected: {target_model}", Fore.MAGENTA)
        model = genai.GenerativeModel(target_model)
        
        model.generate_content("Ping")
        print_system("System Online.", Fore.GREEN)
        return model

    except Exception as e:
        print_system(f"Connection Error: {e}", Fore.RED)
        return None

def execute_task(model, user_query):
    plugin_code = check_plugin(user_query)
    if plugin_code:
        print_system("Plugin Found! Executing...", Fore.CYAN)
        if run_plugin(plugin_code):
            print_system("Plugin Executed.", Fore.GREEN)
        else:
            print_system("Plugin Failed.", Fore.RED)
        return
    
    try:
        print_system("Processing with AI...", Fore.BLUE)
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\nTask: {user_query}")
        code = response.text.replace("```python", "").replace("```", "").strip()
        
        print(f"{Fore.MAGENTA}--- GENERATED CODE ---")
        print(code)
        print(f"--------------------------{Style.RESET_ALL}")
        
        confirm = input(f"{Fore.YELLOW}Execute? (y/n): {Style.RESET_ALL}")
        if confirm.lower() == 'y':
            try:
                exec(code)
                print_system("Task Completed.", Fore.GREEN)
            except Exception as err:
                print_system(f"Runtime Error: {err}", Fore.RED)
        else:
            print_system("Aborted.", Fore.RED)

    except Exception as e:
        print_system(f"AI Error: {e}", Fore.RED)

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.CYAN}=== ARCHON AI CLI ==={Style.RESET_ALL}\n")
    
    model = None
    while not model:
        key = input(f"{Fore.YELLOW}Enter API Key: {Style.RESET_ALL}").strip()
        if key:
            model = get_ai_model(key)
    
    history = InMemoryHistory()
    for cmd in COMMAND_LIST:
        history.append_string(cmd)

    style = PromptStyle.from_dict({
        'prompt': '#00aa00 bold',
    })

    session = PromptSession(history=history, style=style)

    while True:
        try:
            print("-" * 30)
            user_input = session.prompt("Command: ")
            
            if not user_input: continue
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
                
            execute_task(model, user_input)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print_system(f"Input Error: {e}", Fore.RED)

if __name__ == "__main__":
    main()