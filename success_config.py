import subprocess
import sys
import os
import json
import time
import random
import signal
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style

warnings.filterwarnings('ignore')
init(autoreset=True)

def install_packages():
    packages = ['colorama', 'requests', 'urllib3']
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

install_packages()

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

stop_testing = False

def signal_handler(sig, frame):
    global stop_testing
    stop_testing = True
    print("\n" + Fore.YELLOW + "[!] Ctrl+C detected. Saving current results...")

signal.signal(signal.SIGINT, signal_handler)

def color_print(text, color=Fore.WHITE, style=Style.NORMAL):
    print(f"{style}{color}{text}{Style.RESET_ALL}")

def test_single_config(config_line, timeout=1):
    if stop_testing:
        return config_line, False
    try:
        if not config_line.strip():
            return config_line, False
        if config_line.startswith('vless://'):
            from urllib.parse import urlparse
            parsed = urlparse(config_line)
            if parsed.netloc:
                host_port = parsed.netloc.split('@')
                if len(host_port) > 1:
                    server_parts = host_port[1].split(':')
                    if len(server_parts) == 2:
                        host, port = server_parts
                        test_url = f"http://{host}:{port}/"
                        resp = requests.get(test_url, timeout=timeout, headers=HEADERS, verify=False)
                        if resp.status_code < 500:
                            return config_line, True
        elif config_line.startswith('vmess://'):
            import base64
            encoded = config_line.replace('vmess://', '')
            try:
                decoded = base64.b64decode(encoded).decode('utf-8')
                config = json.loads(decoded)
                if 'add' in config and 'port' in config:
                    test_url = f"http://{config['add']}:{config['port']}/"
                    resp = requests.get(test_url, timeout=timeout, headers=HEADERS, verify=False)
                    if resp.status_code < 500:
                        return config_line, True
            except:
                pass
        elif config_line.startswith('trojan://') or config_line.startswith('ss://'):
            from urllib.parse import urlparse
            parsed = urlparse(config_line)
            if parsed.hostname and parsed.port:
                test_url = f"http://{parsed.hostname}:{parsed.port}/"
                resp = requests.get(test_url, timeout=timeout, headers=HEADERS, verify=False)
                if resp.status_code < 500:
                    return config_line, True
        return config_line, False
    except Exception:
        return config_line, False

def read_configs(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        color_print(f"Error: {filename} not found!", Fore.RED)
        return []

def append_working_config(config, output_file):
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(config + '\n')

def git_commit_and_push():
    """انجام commit و push فقط در صورت وجود تغییر واقعی"""
    try:
        # تنظیم identity git
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], capture_output=True, check=False)
        subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], capture_output=True, check=False)
        
        # افزودن فایل‌ها
        subprocess.run(["git", "add", "cleaned_configs.txt", "success_config.txt", "link_stats.json", "README.md"], check=True, capture_output=True)
        
        # بررسی تغییر در staging area
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if result.returncode != 0:
            commit_msg = f"Auto-update after batch - {time.strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True)
            subprocess.run(["git", "push"], check=True, capture_output=True)
            color_print("[✓] Changes committed and pushed to GitHub.", Fore.GREEN)
        else:
            color_print("[*] No changes to commit (files are identical).", Fore.CYAN)
    except subprocess.CalledProcessError as e:
        color_print(f"[!] Git operation failed: {e}", Fore.RED)
        if e.stderr:
            color_print(f"Error details: {e.stderr.decode()}", Fore.RED)

def main():
    color_print("=" * 60, Fore.CYAN)
    color_print("V2RAY CONFIGURATION TESTER (FAST BATCH WITH AUTO-COMMIT)", Fore.YELLOW, Style.BRIGHT)
    color_print("=" * 60, Fore.CYAN)

    input_file = 'cleaned_configs.txt'
    output_file = 'success_config.txt'
    
    if os.path.exists(output_file):
        os.remove(output_file)
    
    configs = read_configs(input_file)
    if not configs:
        color_print("No configurations found!", Fore.RED)
        sys.exit(1)

    total = len(configs)
    color_print(f"[*] Total unique configs to test: {total}", Fore.GREEN)
    
    BATCH_SIZE = 7000
    MAX_WORKERS = 10
    WORKER_TIMEOUT = 1
    
    working_total = 0
    processed = 0
    batch_num = 1
    
    for start in range(0, total, BATCH_SIZE):
        if stop_testing:
            break
        end = min(start + BATCH_SIZE, total)
        batch_configs = configs[start:end]
        batch_working = 0
        
        color_print(f"\n[Batch {batch_num}] Testing configs {start+1} to {end} ({len(batch_configs)} items) with {MAX_WORKERS} workers...", Fore.CYAN)
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_config = {executor.submit(test_single_config, cfg, WORKER_TIMEOUT): cfg for cfg in batch_configs}
            for future in as_completed(future_to_config):
                if stop_testing:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                try:
                    cfg, is_working = future.result(timeout=WORKER_TIMEOUT+0.5)
                except Exception:
                    cfg = future_to_config[future]
                    is_working = False
                
                processed += 1
                if is_working:
                    working_total += 1
                    batch_working += 1
                    append_working_config(cfg, output_file)
                
                percent = (working_total / processed * 100) if processed > 0 else 0
                status = "✓" if is_working else "✗"
                color = Fore.GREEN if is_working else Fore.RED
                print(f"\r[{processed}/{total} ({percent:.1f}%)] Working: {working_total}  {color}{status}{Style.RESET_ALL}", end='', flush=True)
        
        color_print(f"\n[Batch {batch_num}] Completed. Working in this batch: {batch_working}/{len(batch_configs)}", Fore.MAGENTA)
        batch_num += 1
        
        # به‌روزرسانی README و commit
        color_print("[*] Updating README.md and committing changes...", Fore.CYAN)
        subprocess.run([sys.executable, "update_readme.py"], check=False)
        git_commit_and_push()
        
        if end < total:
            sleep_time = random.uniform(1.0, 2.0)
            color_print(f"[*] Sleeping for {sleep_time:.1f} seconds to avoid blocking...", Fore.CYAN)
            time.sleep(sleep_time)
    
    print()
    color_print(f"\n[✓] Testing completed. Total working configs: {working_total}/{total}", Fore.GREEN)
    if working_total > 0:
        color_print(f"[✓] Saved to {output_file}", Fore.GREEN)
    else:
        color_print("[!] No working configs found", Fore.RED)
    color_print("=" * 60, Fore.CYAN)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        color_print("\n[!] Interrupted. Already saved working configs.", Fore.YELLOW)
        git_commit_and_push()
    except Exception as e:
        color_print(f"\n[ERROR] {e}", Fore.RED)
        sys.exit(1)
