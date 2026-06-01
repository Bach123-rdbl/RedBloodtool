from getpass import getpass
import os
import sys
import zlib
import marshal
import base64
import random
import string
import hashlib
import time
import subprocess
import ctypes
import platform
import re
import json
import socket
import urllib.request
import urllib.parse
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

try:
    from colorama import init, Fore, Style
    init(autoreset=False)
except Exception:
    class _Fore:
        RED = WHITE = GREEN = YELLOW = BLUE = CYAN = RESET = ""
    Fore = _Fore()
    class _Style:
        RESET_ALL = ""
    Style = _Style()

LAYERS = 5
JUNK_LINES = 35
ICON_FILENAME = "SAGA.ico"
ICON_APPLIED = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

# =========================================================================
# SYSTEM AUTO-STARTU W NOWYM OKNIE (DLA .EXE)
# =========================================================================
if os.name == 'nt' and "--external" not in sys.argv:
    if sys.argv[0].endswith('.exe'):
        cmd_command = f'start "010000100001000101000010" /d "{SCRIPT_DIR}" "{os.path.abspath(sys.argv[0])}" --external'
    else:
        cmd_command = f'start "010000100001000101000010" /d "{SCRIPT_DIR}" python "{os.path.abspath(sys.argv[0])}" --external'
        
    subprocess.Popen(cmd_command, shell=True)
    sys.exit(0)

THEMES = {
    "red": {"primary": Fore.RED, "secondary": Fore.WHITE, "name": "Blood Red"},
    "green": {"primary": Fore.GREEN, "secondary": Fore.GREEN, "name": "Matrix Green"},
    "blue": {"primary": Fore.BLUE, "secondary": Fore.CYAN, "name": "Cyber Blue"},
    "white": {"primary": Fore.WHITE, "secondary": Fore.YELLOW, "name": "Classic White"}
}

CURRENT_THEME = THEMES["red"]
CURRENT_USER_NAME = None
CURRENT_USER_ROLE = None
CURRENT_USER_PLAN = None
CURRENT_USER_EXPIRE = None

# =========================================================================
# BAZA DANYCH UŻYTKOWNIKÓW (W PAMIĘCI PROGRAMU)
# =========================================================================
USERS_DATABASE = {
    "root": {"password": "slonik2115", "role": "root", "theme": "red", "plan": "GodMode (LFT VIP)", "expires_at": "2099-12-31 23:59:59"},
    "p0datek21": {"password": "changeme", "role": "user", "theme": "red", "plan": "GodMode (LFT VIP)", "expires_at": "2099-12-31 23:59:59"},
    "lowcatopka": {"password": "changeme", "role": "user", "theme": "red", "plan": "GodMode (LFT VIP)", "expires_at": "2099-12-31 23:59:59"}
}

def set_console_title(title_text):
    try:
        if os.name == 'nt':
            ctypes.windll.kernel32.SetConsoleTitleW(title_text)
    except Exception:
        pass

def apply_custom_icon():
    if os.name != 'nt':
        return
    global ICON_APPLIED
    try:
        icon_path = os.path.join(SCRIPT_DIR, ICON_FILENAME)
        if not os.path.exists(icon_path) or ICON_APPLIED:
            return
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            WM_SETICON = 0x0080
            ICON_SMALL, ICON_BIG = 0, 1
            LR_LOADFROMFILE = 0x00000010
            IMAGE_ICON = 1
            h_icon = ctypes.windll.user32.LoadImageW(None, icon_path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE)
            if h_icon:
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h_icon)
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, h_icon)
                ICON_APPLIED = True
    except Exception:
        pass

set_console_title("")
apply_custom_icon()

logo = r"""
        ██▀███  ▓█████  ▓█████▄  ▄▄▄▄   ██▓     ▒█████   ▒█████  ▓█████▄ 
        ▓██ ▒ ██▒▓█   ▀ ▒██▀ ██▌▓█████▄ ▓██▒    ▒██▒  ██▒▒██▒  ██▒▒██▀ ██▌
        ▓██ ░▄█ ▒▒███   ░██   █▌▒██▒ ▄██▒██░    ▒██░  ██▒▒██░  ██▒░██   █▌
        ▒██▀▀█▄  ▒▓█  ▄ ░▓█▄   ▌▒██░█▀   ▒██░    ▒██   ██░▒██   ██░░▓█▄   ▌
        ░██▓ ▒██▒░▒████▒░▒████▓ ░▓█  ▀█▓░██████▒░ ████▓▒░░ ████▓▒░░▒████▓ 
        ░ ▒▓ ░▒▓░░░ ▒░ ░ ▒▒▓  ▒ ░▒▓███▀▒░ ▒░▓  ░░ ▒░▒░▒░ ░ ▒░▒░▒░ ░▒▒▓  ▒ 
          ░▒ ░ ▒░ ░ ░  ░ ░ ▒  ▒ ▒░▒   ░ ░ ░ ▒  ░  ░ ▒ ▒░   ░ ▒ ▒░   ░ ▒  ▒ 
          ░░   ░    ░    ░ ░  ░  ░    ░   ░ ░    ░ ░ ░ ▒    ░ ░ ░ ▒  ░ ░ ░ ░ 
           ░        ░  ░   ░     ░            ░  ░      ░ ░        ░ ░   ░    
                    ░            ░
    [?] 1.1 Changelog        [!] Discord: https://discord.gg/dD3gVVChcH  /  dsc.gg/RedBlood                                                       
"""

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def get_masked_password(prompt="Password: "):
    try:
        return getpass(prompt)
    except Exception:
        try:
            return input(prompt)
        except Exception:
            print("\n[!] Console input unavailable.")
            return ""

def login_screen():
    global CURRENT_USER_ROLE, CURRENT_USER_NAME, CURRENT_THEME, CURRENT_USER_PLAN, CURRENT_USER_EXPIRE
    while True:
        clear()
        username = input(Fore.WHITE + "Login: ").strip()
        password = get_masked_password(Fore.WHITE + "Password: ")

        if username in USERS_DATABASE and USERS_DATABASE[username]["password"] == password:
            expire_str = USERS_DATABASE[username].get("expires_at", "2099-12-31 23:59:59")
            user_plan = USERS_DATABASE[username].get("plan", "Ghost (7d non VIP)")
            
            if "LFT" in user_plan or expire_str == "2099-12-31 23:59:59":
                CURRENT_USER_EXPIRE = "PERMANENT ACCESS (LIFETIME)"
            else:
                try:
                    expire_date = datetime.strptime(expire_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    expire_date = datetime.now() + timedelta(days=1)
                    
                if datetime.now() > expire_date:
                    print(Fore.RED + f"\n[!] Access Denied: Your license subscription ({user_plan}) expired on {expire_str}!")
                    time.sleep(5)
                    continue
                
            CURRENT_USER_EXPIRE = expire_str
            CURRENT_USER_NAME = username
            CURRENT_USER_ROLE = USERS_DATABASE[username]["role"]
            CURRENT_USER_PLAN = user_plan
            
            user_theme_key = USERS_DATABASE[username].get("theme", "red")
            CURRENT_THEME = THEMES.get(user_theme_key, THEMES["red"])
            set_console_title(f"RedBlood | @{CURRENT_USER_NAME}")
            time.sleep(1.5)
            break
        else:
            print(Fore.RED + "\n[!] Invalid username or password. Try again.")
            time.sleep(2)

# =========================================================================
# IMPLEMENTACJA NARZĘDZI SEKCJA: OSINT
# =========================================================================
def utility_ip_lookup():
    clear()
    print(CURRENT_THEME["primary"] + logo)
    ip = input(Fore.WHITE + "Enter target IP: ").strip()
    print(Fore.YELLOW + "\n[*] Fetching network intelligence data...")
    try:
        url = f"http://ip-api.com/json/{ip}"
        response = urllib.request.urlopen(url, timeout=3)
        data = json.loads(response.read().decode())
        
        if data.get("status") == "success":
            print(Fore.GREEN + f"[+] IP Address:   {Fore.WHITE}{data.get('query')}")
            print(Fore.GREEN + f"[+] Country:      {Fore.WHITE}{data.get('country')} ({data.get('countryCode')})")
            print(Fore.GREEN + f"[+] Region/City:  {Fore.WHITE}{data.get('regionName')} / {data.get('city')}")
            print(Fore.GREEN + f"[+] ISP Provider: {Fore.WHITE}{data.get('isp')}")
        else:
            print(Fore.RED + "[!] Invalid IP address or private network range.")
    except Exception as e:
        print(Fore.RED + f"[!] Connection error: {e}")
    input(Fore.WHITE + "\nPress ENTER to continue...")

def osint_username_tracker():
    clear()
    print(CURRENT_THEME["primary"] + logo)
    print(CURRENT_THEME["secondary"] + "=== USERNAME TRACKER ===")
    username = input(Fore.WHITE + "Enter target username: ").strip()
    if not username: return
    
    targets = {
        "GitHub": f"https://api.github.com/users/{username}",
        "Instagram": f"https://www.instagram.com/{username}/",
        "X (Twitter)": f"https://x.com/{username}",
        "Minecraft": f"https://api.mojang.com/users/profiles/minecraft/{username}"
    }
    
    print(Fore.YELLOW + f"\n[*] Searching profiles for: {username}...\n")
    for platform, url in targets.items():
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status == 200:
                    print(Fore.GREEN + f"[+] Found on {platform:<12} -> {url}")
        except urllib.request.HTTPError as e:
            if e.code == 404:
                print(Fore.RED + f"[-] Not Found on {platform:<12}")
            else:
                print(Fore.YELLOW + f"[?] Blocked/Error on {platform:<12}")
        except Exception:
            print(Fore.RED + f"[!] Timeout on {platform:<12}")
            
    input(Fore.WHITE + "\nPress ENTER to continue...")

# =========================================================================
# IMPLEMENTACJA NARZĘDZI SEKCJA: UTILITIES
# =========================================================================
def utility_password_generator():
    clear()
    print(CURRENT_THEME["primary"] + logo)
    print(CURRENT_THEME["secondary"] + "=== PASSWORD GENERATOR ===")
    try:
        length = int(input(Fore.WHITE + "Enter password length (e.g. 16): ").strip())
        if length < 4: length = 4
        characters = string.ascii_letters + string.digits + string.punctuation
        generated = "".join(random.choice(characters) for _ in range(length))
        print(CURRENT_THEME["primary"] + f"\n[+] Generated Password: {Fore.WHITE}{generated}")
    except ValueError:
        print(Fore.RED + "\n[!] Invalid number formatting.")
    input(Fore.WHITE + "\nPress ENTER to continue...")

def utility_system_information():
    clear()
    print(CURRENT_THEME["primary"] + logo)
    print(CURRENT_THEME["secondary"] + "=== SYSTEM INFORMATION ===")
    print(Fore.WHITE + f"OS Type:         {platform.system()}")
    print(Fore.WHITE + f"OS Release:      {platform.release()}")
    print(Fore.WHITE + f"Architecture:    {platform.architecture()[0]}")
    print(Fore.WHITE + f"Processor:       {platform.processor()}")
    print(Fore.WHITE + f"Python Version:  {platform.python_version()}")
    input(Fore.WHITE + "\nPress ENTER to continue...")

def utility_hash_identifier():
    clear()
    print(CURRENT_THEME["primary"] + logo)
    print(CURRENT_THEME["secondary"] + "=== HASH IDENTIFIER ===")
    user_hash = input(Fore.WHITE + "Enter hash string: ").strip()
    if not user_hash: return
    
    length = len(user_hash)
    is_hex = all(c in string.hexdigits for c in user_hash)
    print(Fore.YELLOW + "\n[*] Analyzing cryptographic structure...")
    
    if not is_hex:
        print(Fore.RED + "[!] Error: Hash contains non-hexadecimal characters.")
    elif length == 32:
        print(Fore.GREEN + "[+] Possible Algorithm: MD5")
    elif length == 40:
        print(Fore.GREEN + "[+] Possible Algorithm: SHA-1")
    elif length == 64:
        print(Fore.GREEN + "[+] Possible Algorithm: SHA-256")
    elif length == 128:
        print(Fore.GREEN + "[+] Possible Algorithm: SHA-512")
    else:
        print(Fore.RED + "[!] Unknown format. Check length or padding.")
        
    input(Fore.WHITE + "\nPress ENTER to continue...")

def utility_file_hasher():
    clear()
    print(CURRENT_THEME["primary"] + logo)
    print(CURRENT_THEME["secondary"] + "=== FILE HASHER (SHA-256) ===")
    file_path = input(Fore.WHITE + "Enter path to file: ").strip()
    if not os.path.exists(file_path):
        print(Fore.RED + "\n[!] File not found.")
    else:
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            print(CURRENT_THEME["primary"] + f"\n[+] SHA-256: {Fore.WHITE}{sha256_hash.hexdigest()}")
        except Exception as e:
            print(Fore.RED + f"\n[!] Error reading file stream: {e}")
    input(Fore.WHITE + "\nPress ENTER to continue...")

def utility_base64_tool():
    clear()
    print(CURRENT_THEME["primary"] + logo)
    print(CURRENT_THEME["secondary"] + "=== BASE64 CIPHER TOOL ===")
    print(Fore.YELLOW + "[1] Encode text string to Base64")
    print(Fore.YELLOW + "[2] Decode Base64 string to plaintext")
    choice = input(CURRENT_THEME["primary"] + "\nSelect mode [1-2]: " + Fore.WHITE).strip()
    
    if choice == "1":
        plain_text = input(Fore.WHITE + "Enter plaintext text: ")
        encoded = base64.b64encode(plain_text.encode('utf-8', errors='ignore')).decode('utf-8')
        print(Fore.GREEN + f"\n[+] Base64 Result: {Fore.WHITE}{encoded}")
    elif choice == "2":
        b64_text = input(Fore.WHITE + "Enter Base64 string: ")
        try:
            decoded = base64.b64decode(b64_text.encode('utf-8')).decode('utf-8', errors='ignore')
            print(Fore.GREEN + f"\n[+] Plaintext Result: {Fore.WHITE}{decoded}")
        except Exception:
            print(Fore.RED + "\n[!] Cryptographic decoding error: Invalid Base64 payload architecture.")
    input(Fore.WHITE + "\nPress ENTER to continue...")

def utility_qr_generator():
    clear()
    print(CURRENT_THEME["primary"] + logo)
    print(CURRENT_THEME["secondary"] + "=== QR CODE GENERATOR ===")
    data = input(Fore.WHITE + "Enter text or URL to encode: ").strip()
    if not data: return
    
    filename = "generated_qr.png"
    print(Fore.YELLOW + "\n[*] Compiling QR vector matrix...")
    try:
        encoded_data = urllib.parse.quote(data)
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_data}"
        urllib.request.urlretrieve(url, filename)
        print(Fore.GREEN + f"[+] Success! QR code saved as: {Fore.WHITE}{os.path.abspath(filename)}")
    except Exception as e:
        print(Fore.RED + f"[!] Failed to generate QR: {e}")
        
    input(Fore.WHITE + "\nPress ENTER to continue...")

# =========================================================================
# USTAWIENIA KONTA I ZMIANA HASŁA
# =========================================================================
def account_settings_panel():
    global CURRENT_THEME
    while True:
        clear()
        user_theme_key = USERS_DATABASE[CURRENT_USER_NAME].get("theme", "red")
        CURRENT_THEME = THEMES.get(user_theme_key, THEMES["red"])
        
        p = CURRENT_THEME["primary"]
        s = CURRENT_THEME["secondary"]
        w = Fore.WHITE
        
        print(p + logo)
        print(s + "=== ACCOUNT & INTERFACE SETTINGS ===")
        print(p + "[1] " + w + "Theme: " + THEMES["red"]["primary"] + "Blood Red")
        print(p + "[2] " + w + "Theme: " + THEMES["green"]["primary"] + "Matrix Green")
        print(p + "[3] " + w + "Theme: " + THEMES["blue"]["primary"] + "Cyber Blue")
        print(p + "[4] " + w + "Theme: " + THEMES["white"]["primary"] + "Classic White")
        print(p + "[5] " + Fore.YELLOW + "Change Account Password")
        print(p + "[0] " + w + "Back to main menu")
        choice = input(p + f"\n[{CURRENT_USER_NAME}@SETTINGS] -> " + w).strip()
        
        if choice == "1":
            USERS_DATABASE[CURRENT_USER_NAME]["theme"] = "red"
        elif choice == "2":
            USERS_DATABASE[CURRENT_USER_NAME]["theme"] = "green"
        elif choice == "3":
            USERS_DATABASE[CURRENT_USER_NAME]["theme"] = "blue"
        elif choice == "4":
            USERS_DATABASE[CURRENT_USER_NAME]["theme"] = "white"
        elif choice == "5":
            clear()
            print(p + logo)
            print(s + "=== SECURITY VECTOR: CHANGE PASSWORD ===")
            old_pass = get_masked_password(w + "Enter current password: ")
            if old_pass == USERS_DATABASE[CURRENT_USER_NAME]["password"]:
                new_pass = get_masked_password(w + "Enter new password: ")
                if not new_pass.strip():
                    print(Fore.RED + "\n[!] Operation Failed: Password cannot be empty.")
                    time.sleep(2)
                else:
                    USERS_DATABASE[CURRENT_USER_NAME]["password"] = new_pass
                    print(Fore.GREEN + "\n[+] Success: Password synchronized in database storage.")
                    time.sleep(2)
            else:
                print(Fore.RED + "\n[!] Authentication Error: Current password incorrect.")
                time.sleep(2)
        elif choice == "0":
            break

def root_panel():
    while True:
        clear()
        print(CURRENT_THEME["primary"] + logo)
        print(Fore.YELLOW + "[1]" + Fore.WHITE + " List all database users & licenses")
        print(Fore.YELLOW + "[2]" + Fore.WHITE + " Add or update user license")
        print(Fore.YELLOW + "[3]" + Fore.WHITE + " Delete existing user")
        print(Fore.YELLOW + "[0]" + Fore.WHITE + " Back to main menu")
        adm_choice = input(Fore.GREEN + f"\n[root@] -> " + Fore.WHITE).strip()
        
        if adm_choice == "1":
            print("\n--- Current Registered Accounts & Licenses ---")
            for u, data in USERS_DATABASE.items():
                p_plan = data.get("plan", "Trial").ljust(25)
                p_exp = data.get("expires_at", "Expired").ljust(21)
                print(f"User: {u.ljust(12)} | Role: {data['role'].ljust(6)} | Plan: {p_plan} | Expires: {p_exp} | Pass: {data['password']}")
            input("\nPress ENTER to continue...")
            
        elif adm_choice == "2":
            new_user = input("\nEnter username to add/change: ").strip()
            if not new_user: continue
            new_pass = input("Enter new password: ").strip()
            new_role = input("Enter role (user/root) [default: user]: ").strip().lower()
            if new_role not in ["user", "root"]: new_role = "user"
            
            print(Fore.YELLOW + "\n Price-List 31d:")
            print(Fore.RED + "[1]" + Fore.WHITE + " Ghost 7d non VIP")
            print(Fore.RED + "[2]" + Fore.WHITE + " Phreaker 31d non VIP")
            print(Fore.RED + "[3]" + Fore.WHITE + " Netrunner 31d VIP")
            print(Fore.YELLOW + "\n Price-List Lifetime:")
            print(Fore.RED + "[4]" + Fore.WHITE + " Mainframe LFT non VIP")
            print(Fore.RED + "[5]" + Fore.WHITE + " Spectre LFT VIP")
            print(Fore.RED + "[6]" + Fore.WHITE + " GodMode LFT VIP")
            
            plan_choice = input(Fore.GREEN + "\nSelect tier [1-6]: ").strip()
            
            if plan_choice == "1":
                new_plan = "Ghost (7d non VIP)"
                calculated_expire = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
            elif plan_choice == "2":
                new_plan = "Phreaker (31d non VIP)"
                calculated_expire = (datetime.now() + timedelta(days=31)).strftime("%Y-%m-%d %H:%M:%S")
            elif plan_choice == "3":
                new_plan = "Netrunner (31d VIP)"
                calculated_expire = (datetime.now() + timedelta(days=31)).strftime("%Y-%m-%d %H:%M:%S")
            elif plan_choice == "4":
                new_plan = "Mainframe (LFT non VIP)"
                calculated_expire = "2099-12-31 23:59:59"
            elif plan_choice == "5":
                new_plan = "Spectre (LFT VIP)"
                calculated_expire = "2099-12-31 23:59:59"
            elif plan_choice == "6":
                new_plan = "GodMode (LFT VIP)"
                calculated_expire = "2099-12-31 23:59:59"
            else:
                new_plan = "Ghost (7d non VIP)"
                calculated_expire = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")

            existing_theme = USERS_DATABASE[new_user].get("theme", "red") if new_user in USERS_DATABASE else "red"
            USERS_DATABASE[new_user] = {
                "password": new_pass, 
                "role": new_role, 
                "theme": existing_theme,
                "plan": new_plan,
                "expires_at": calculated_expire
            }
            print(Fore.GREEN + f"[+] Profile updated successfully!")
            time.sleep(2)
            
        elif adm_choice == "3":
            del_user = input("\nEnter username to delete: ").strip()
            if del_user == "root":
                print(Fore.RED + "[!] Security Lockout: Cannot delete root administrator!")
                time.sleep(1.5)
            elif del_user in USERS_DATABASE:
                del USERS_DATABASE[del_user]
                print(Fore.GREEN + f"[+] User removed.")
                time.sleep(1.5)
            else:
                print(Fore.RED + "[!] User not found.")
                time.sleep(1.5)
        elif adm_choice == "0":
            break

def rand_name(length=25):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def loading():
    bars = ["#", "##", "###", "####", "#####", "######", "#######", "########", "#########", "##########"]
    for bar in bars:
        print(CURRENT_THEME["primary"] + "\rBUILDING SOURCE LAYER ENVIRONMENT " + bar, end="")
        time.sleep(0.05)
    print("\n")

def add_junk():
    junk = []
    for _ in range(JUNK_LINES):
        a = rand_name()
        b = rand_name()
        num = random.randint(10000, 99999)
        junk.append(f"{a} = {num}")
        junk.append(f"{b} = '{hashlib.md5(str(num).encode()).hexdigest()}'")
    return "\n".join(junk)

def one_line(encoded):
    return f"import marshal,zlib,base64;exec(marshal.loads(zlib.decompress(base64.b64decode('{encoded}'))))"

def obfuscate(code):
    current = code
    for _ in range(LAYERS):
        compiled = compile(current, "<BEAM>", "exec")
        marshaled = marshal.dumps(compiled)
        compressed = zlib.compress(marshaled)
        encoded = base64.b64encode(compressed).decode()
        v1 = rand_name()
        v2 = rand_name()
        current = f'\nimport marshal,zlib,base64\n\n{add_junk()}\n\n{v1}="{encoded}"\n\n{v2}=marshal.loads(\nzlib.decompress(\nbase64.b64decode({v1})\n)\n)\n\nexec({v2})\n'
    return current

def protect_file():
    clear()
    print(CURRENT_THEME["primary"] + logo)
    file_path = input(Fore.WHITE + "Enter Python file path target: ").strip()
    if not os.path.exists(file_path):
        print(Fore.RED + "\n[!] Operation Failed: Specified target path missing.")
        return
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
        print(CURRENT_THEME["primary"] + "\n[*] Compiling encryption matrix...")
        loading()
        protected = obfuscate(code)
        compiled = compile(protected, "<FINAL>", "exec")
        marshaled = marshal.dumps(compiled)
        compressed = zlib.compress(marshaled)
        encoded = base64.b64encode(compressed).decode()
        final = one_line(encoded)
        output = os.path.join(os.path.dirname(file_path), "protected_" + os.path.basename(file_path))
        with open(output, "w", encoding="utf-8") as f:
            f.write(final)
        print(Fore.GREEN + f"[+] Obfuscated package successfully created -> {output}")
    except Exception as e:
        print(Fore.RED + f"\n[!] Compilation exception error: {e}")
    input(Fore.WHITE + "\nPress ENTER to continue...")

# =========================================================================
# SYSTEM DYNAMICZNEGO WYRÓWNYWANIA SIATKI KONSOLI (3 KOLUMNY po 30 ZNAKÓW)
# =========================================================================
def format_menu_line(num1, text1, num2, text2, num3, text3, primary_color):
    w = Fore.WHITE
    
    def format_cell(num, text):
        if num:
            clean = f" [{num}] {text}"
            colored = f" {primary_color}[{num}]{w} {text}"
        else:
            clean = f" {text}"
            colored = f" {w}{text}"
        return colored + " " * (30 - len(clean))
        
    c1 = format_cell(num1, text1)
    c2 = format_cell(num2, text2)
    c3 = format_cell(num3, text3)
    
    return f"{primary_color}│{c1}{primary_color}│{c2}{primary_color}│{c3}{primary_color}│"

# =========================================================================
# INICJALIZACJA PROCESU
# =========================================================================
login_screen()

# =========================================================================
# GŁÓWNA PĘTLA INTERFEJSU
# =========================================================================
while True:
    clear()
    
    user_theme_key = USERS_DATABASE[CURRENT_USER_NAME].get("theme", "red")
    CURRENT_THEME = THEMES.get(user_theme_key, THEMES["red"])
    
    p = CURRENT_THEME["primary"]
    w = Fore.WHITE
    
    print(p + logo)
    
    # ZMODYFIKOWANY NAGŁÓWEK (Tylko 1.1 Changelog oraz Discord: asi)

    print(p + "├" + "─" * 30 + "┼" + "─" * 30 + "┼" + "─" * 30 + "┤")
    t1 = "       System & Account"
    colored_t1 = f"{w}{t1}" + " " * (30 - len(t1))
    t2 = "             Osint"
    colored_t2 = f"{w}{t2}" + " " * (30 - len(t2))
    t3 = "           Utilities"
    colored_t3 = f"{w}{t3}" + " " * (30 - len(t3))
    print(p + "│" + colored_t1 + p + "│" + colored_t2 + p + "│" + colored_t3 + p + "│")
    
    print(p + "├" + "─" * 30 + "┼" + "─" * 30 + "┼" + "─" * 30 + "┤")
    
    root_str = "Root Control Panel" if CURRENT_USER_ROLE == "root" else "Root Panel"
    root_num = "03"
    
    print(format_menu_line("01", "Settings & Account",   "11", "Ip Lookup",        "21", "Password Generator", p))
    print(format_menu_line("02", "Current User Info",    "12", "Username Tracker", "22", "System Information", p))
    print(format_menu_line(root_num, root_str,           "",   "",                 "23", "Hash Identifier",    p)) 
    print(format_menu_line("99", "Logout / Switch User", "",   "",                 "24", "File Hasher",        p))
    print(format_menu_line("00", "Exit Dashboard",       "",   "",                 "25", "Text Encoder/Decoder",p))
    print(format_menu_line("",   "",                     "",   "",                 "26", "Qr Code Generator",  p))
    print(format_menu_line("",   "",                     "",   "",                 "27", "Python Obfuscator",  p))
    
    print(p + "└" + "─" * 30 + "┴" + "─" * 30 + "┴" + "─" * 30 + "┘")

    choice = input(p + f"\n[{CURRENT_USER_NAME}@] ──> " + w).strip().lower()

    if choice in ["01", "1"]: account_settings_panel()
    elif choice in ["02", "2"]:
        clear()
        print(p + logo)
        print(CURRENT_THEME["secondary"] + "=== METRIC MONITOR ===")
        print(w + f"Active Account Profile:  @{CURRENT_USER_NAME}")
        print(w + f"Account Privilege Rank:  {CURRENT_USER_ROLE.upper()}")
        print(w + f"License Tier Plan:       {CURRENT_USER_PLAN.upper()}")
        print(w + f"License Expiration Date: {CURRENT_USER_EXPIRE}")
        input(w + "\nPress ENTER to safely close session view...")
    elif choice in ["03", "3"]:
        if CURRENT_USER_ROLE == "root": root_panel()
        else:
            print(Fore.RED + "\n[!] You don't have permission to access this section.")
            time.sleep(1.5)
    elif choice == "99":
        CURRENT_USER_NAME = CURRENT_USER_ROLE = CURRENT_USER_PLAN = CURRENT_USER_EXPIRE = None
        login_screen()
    elif choice in ["00", "0", "exit"]:
        print(Fore.GREEN + "\nTerminating application dashboard thread...")
        sys.exit(0)
        
    elif choice == "11": utility_ip_lookup()
    elif choice == "12": osint_username_tracker()
    
    elif choice == "21": utility_password_generator()
    elif choice == "22": utility_system_information()
    elif choice == "23": utility_hash_identifier()
    elif choice == "24": utility_file_hasher()
    elif choice == "25": utility_base64_tool()
    elif choice == "26": utility_qr_generator()
    elif choice == "27": protect_file()
    else:
        if choice:
            print(w + f"\nSyntax Error: Parameter command value '{choice}' not found.")
            time.sleep(1.5)