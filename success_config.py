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

# Header شبیه مرورگر
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

stop_testing = False

def signal_handler(sig, frame):
    global stop_testing
    stop_testing = True
    print("\n")
    print(Fore.YELLOW + "[!] Ctrl+C detected. Stopping tests and saving current working configs...")

signal.signal(signal.SIGINT, signal_handler)

def color_print(text, color=Fore.WHITE, style=Style.NORMAL):
    print(f"{style}{color}{text}{Style.RESET_ALL}")

def save_config_immediately(config, output_file='success_config.txt'):
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(config + '\n')

def test_v2ray_config(config_line, timeout=2):
    if stop_testing:
        return None, False
    try:
        if not config_line.strip():
            return None, False
        # استخراج host و port از پروتکل‌های مختلف
        host, port = None, None
        if config_line.startswith('vless://'):
            from urllib.parse import urlparse
            parsed = urlparse(config_line)
            if '@' in parsed.netloc:
                host_port = parsed.netloc.split('@')[1]
                if ':' in host_port:
                    host, port = host_port.split(':')
        elif config_line.startswith('vmess://'):
            import base64
            encoded = config_line.replace('vmess://', '')
            decoded = base64.b64decode(encoded).decode('utf-8')
            config = json.loads(decoded)
            host, port = config.get('add'), str(config.get('port'))
        elif config_line.startswith('trojan://') or config_line.startswith('ss://'):
            from urllib.parse import urlparse
            parsed = urlparse(config_line)
            host, port = parsed.hostname, parsed.port
        if host and port:
            # تست واقعی‌تر: درخواست به یک آدرس معتبر اینترنتی
            test_url = f"http://{host}:{port}/"
            # استفاده از timeout کوتاه و Header
            response = requests.get(test_url, timeout=timeout, headers=HEADERS, verify=False)
            if response.status_code < 500:
                # تأخیر تصادفی قبل از تست بعدی برای طبیعی‌تر جلوه کردن
                time.sleep(random.uniform(0.1, 0.5))
                return config_line, True
        return config_line, False
    except:
        return config_line, False

def read_configs(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        color_print(f"Error: {filename} not found!", Fore.RED)
        return []

def init_output_file(output_file='success_config.txt'):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('')

def main():
    color_print("=" * 60, Fore.CYAN)
    color_print("V2RAY CONFIGURATION TESTER (REALISTIC MODE)", Fore.YELLOW, Style.BRIGHT)
    color_print("=" * 60, Fore.CYAN)

    input_file = 'cleaned_configs.txt'
    output_file = 'success_config.txt'

    configs = read_configs(input_file)
    if not configs:
        color_print("No configurations found or file is empty!", Fore.RED)
        sys.exit(1)

    color_print(f"\n[*] Found {len(configs)} unique configs to test", Fore.GREEN)
    init_output_file(output_file)

    color_print(f"[*] Testing with {5} parallel workers (to avoid blocking)...\n", Fore.CYAN)

    working_count = 0
    total = len(configs)
    completed = 0
    global stop_testing
    stop_testing = False

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_config = {executor.submit(test_v2ray_config, config): config for config in configs}
        for future in as_completed(future_to_config):
            if stop_testing:
                executor.shutdown(wait=False, cancel_futures=True)
                break
            config, is_working = future.result()
            completed += 1
            if is_working:
                working_count += 1
                save_config_immediately(config, output_file)
                status = "✓"
                color_status = Fore.GREEN
            else:
                status = "✗"
                color_status = Fore.RED
            percent = (working_count / completed * 100) if completed > 0 else 0
            print(f"\r[{completed}/{total} ({percent:.1f}%)] Working: {working_count}  {color_status}{status}{Style.RESET_ALL}", end='', flush=True)

    print()
    color_print(f"\n[✓] Testing completed. Working configs: {working_count}/{total}", Fore.GREEN)
    if working_count > 0:
        color_print(f"[✓] Saved to {output_file}", Fore.GREEN)
    else:
        color_print("[!] No working configs found", Fore.RED)
    color_print("=" * 60, Fore.CYAN)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        color_print("\n[!] Interrupted. Already saved working configs.", Fore.YELLOW)
    except Exception as e:
        color_print(f"\n[ERROR] {e}", Fore.RED)
