import os
import sys
import subprocess

def install_dependencies():
    """Automatically installs required packages if not present."""
    required_packages = ["requests", "colorama"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"[!] {package} not found. Installing now...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Run installation before importing colorama/requests
install_dependencies()

import requests
from colorama import init, Fore, Style

# Initialize Colorama for Windows terminal colors
init(autoreset=True)

def process_v2ray_links():
    input_file = "pool_address.txt"
    output_file = "cleaned_configs.txt"

    # 1. Check if input file exists
    if not os.path.exists(input_file):
        print(Fore.RED + f"[ERROR] '{input_file}' not found! Please create it.")
        return

    print(Fore.CYAN + "="*50)
    print(Fore.CYAN + "       V2RAY CONFIG CLEANER PRO")
    print(Fore.CYAN + "="*50 + "\n")

    # 2. Read and deduplicate URLs
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_urls = [line.strip() for line in f if line.strip()]
        
        unique_urls = list(set(raw_urls))
        print(Fore.YELLOW + f"[*] Found {len(raw_urls)} URLs in file.")
        print(Fore.GREEN + f"[*] Removed duplicates. Working with {len(unique_urls)} unique subscription links.\n")
    except Exception as e:
        print(Fore.RED + f"[ERROR] Failed to read input file: {e}")
        return

    all_configs_raw = []
    total_configs_found = 0

    # 3. Fetch and extract configs
    for index, url in enumerate(unique_urls, 1):
        print(Fore.BLUE + f"[{index}/{len(unique_urls)}] Fetching: {url[:50]}...")
        
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            # V2Ray links are often base64 encoded or plain text
            # We treat the content as text lines
            content = response.text.strip().splitlines()
            
            current_link_count = len(content)
            total_configs_found += current_link_count
            all_configs_raw.extend(content)
            
            print(Fore.MAGENTA + f"    -> Found {current_link_count} configs in this link.")
            
        except Exception as e:
            print(Fore.RED + f"    -> [FAILED] Could not fetch this link. Error: {e}")

    print(Fore.CYAN + "\n" + "-"*50)
    print(Fore.YELLOW + f"Total raw configs collected: {total_configs_found}")

    # 4. Deduplicate Configs
    unique_configs = list(set(all_configs_raw))
    unique_count = len(unique_configs)
    
    print(Fore.YELLOW + f"Total unique configs found:  {unique_count}")
    print(Fore.GREEN + f"Configs removed (duplicates): {total_configs_found - unique_count}")
    print(Fore.CYAN + "-"*50)

    # 5. Save to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for config in unique_configs:
                f.write(config + "\n")
        print(Fore.GREEN + f"\n[SUCCESS] All unique configs saved to: {Fore.WHITE}{output_file}")
    except Exception as e:
        print(Fore.RED + f"\n[ERROR] Failed to save output file: {e}")

    print(Fore.CYAN + "\n" + "="*50)

if __name__ == "__main__":
    try:
        process_v2ray_links()
    except Exception as e:
        print(Fore.RED + f"\n[CRITICAL ERROR] {e}")
    finally:
        # This prevents the window from closing immediately on Windows
        print(Fore.WHITE + "\n" + "="*50)
        input(Fore.YELLOW + "Press ENTER to exit...")
