import subprocess
import sys
import os
import json
import time
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

stop_testing = False

def signal_handler(sig, frame):
    global stop_testing
    stop_testing = True
    print("\n")
    color_print("[!] Ctrl+C detected. Stopping tests and saving current working configs...", Fore.YELLOW, Style.BRIGHT)

signal.signal(signal.SIGINT, signal_handler)

def color_print(text, color=Fore.WHITE, style=Style.NORMAL):
    print(f"{style}{color}{text}{Style.RESET_ALL}")

def save_config_immediately(config, output_file='success_config.txt'):
    try:
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(config + '\n')
        return True
    except Exception as e:
        return False

def test_v2ray_config(config_line, timeout=1):
    if stop_testing:
        return None, False
    try:
        if not config_line.strip():
            return None, False
        if config_line.startswith('vless://'):
            return test_vless_config(config_line, timeout)
        elif config_line.startswith('vmess://'):
            return test_vmess_config(config_line, timeout)
        elif config_line.startswith('trojan://'):
            return test_trojan_config(config_line, timeout)
        elif config_line.startswith('ss://'):
            return test_shadowsocks_config(config_line, timeout)
        else:
            return config_line, False
    except:
        return config_line, False

def test_vless_config(config_line, timeout):
    try:
        from urllib.parse import urlparse
        parsed = urlparse(config_line)
        if parsed.netloc:
            host_port = parsed.netloc.split('@')
            if len(host_port) > 1:
                server_parts = host_port[1].split(':')
                if len(server_parts) == 2:
                    host, port = server_parts
                    test_url = f"http://{host}:{port}/"
                    response = requests.get(test_url, timeout=timeout, verify=False)
                    if response.status_code < 500:
                        return config_line, True
        return config_line, False
    except:
        return config_line, False

def test_vmess_config(config_line, timeout):
    try:
        import base64
        encoded = config_line.replace('vmess://', '')
        decoded = base64.b64decode(encoded).decode('utf-8')
        config = json.loads(decoded)
        if 'add' in config and 'port' in config:
            test_url = f"http://{config['add']}:{config['port']}/"
            response = requests.get(test_url, timeout=timeout, verify=False)
            if response.status_code < 500:
                return config_line, True
        return config_line, False
    except:
        return config_line, False

def test_trojan_config(config_line, timeout):
    try:
        from urllib.parse import urlparse
        parsed = urlparse(config_line)
        if parsed.hostname and parsed.port:
            test_url = f"http://{parsed.hostname}:{parsed.port}/"
            response = requests.get(test_url, timeout=timeout, verify=False)
            if response.status_code < 500:
                return config_line, True
        return config_line, False
    except:
        return config_line, False

def test_shadowsocks_config(config_line, timeout):
    try:
        from urllib.parse import urlparse
        parsed = urlparse(config_line)
        if parsed.hostname and parsed.port:
            test_url = f"http://{parsed.hostname}:{parsed.port}/"
            response = requests.get(test_url, timeout=timeout, verify=False)
            if response.status_code < 500:
                return config_line, True
        return config_line, False
    except:
        return config_line, False

def read_configs(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            configs = [line.strip() for line in f if line.strip()]
        return configs
    except FileNotFoundError:
        color_print(f"Error: {filename} not found!", Fore.RED)
        return []
    except Exception as e:
        color_print(f"Error reading {filename}: {e}", Fore.RED)
        return []

def init_output_file(output_file='success_config.txt'):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('')
        return True
    except Exception as e:
        color_print(f"Error initializing {output_file}: {e}", Fore.RED)
        return False

def main():
    color_print("=" * 60, Fore.CYAN)
    color_print("V2RAY CONFIGURATION TESTER", Fore.YELLOW, Style.BRIGHT)
    color_print("=" * 60, Fore.CYAN)

    input_file = 'cleaned_configs.txt'
    output_file = 'success_config.txt'

    color_print(f"\n[1] Reading configurations from {input_file}...", Fore.GREEN)
    configs = read_configs(input_file)

    if not configs:
        color_print("No configurations found or file is empty!", Fore.RED)
        sys.exit(1)

    color_print(f"[2] Found {len(configs)} configurations", Fore.GREEN)
    color_print(f"[3] Initializing output file {output_file}...", Fore.GREEN)
    init_output_file(output_file)

    color_print(f"[4] Testing configurations (press Ctrl+C to stop and save)...\n", Fore.GREEN)

    vip_configs_count = 0
    total = len(configs)
    completed = 0
    global stop_testing
    stop_testing = False

    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_config = {executor.submit(test_v2ray_config, config): config for config in configs}
        for future in as_completed(future_to_config):
            if stop_testing:
                executor.shutdown(wait=False, cancel_futures=True)
                break
            config, is_working = future.result()
            completed += 1
            if is_working:
                vip_configs_count += 1
                save_config_immediately(config, output_file)
                status = "✓"
                color_status = Fore.GREEN
            else:
                status = "✗"
                color_status = Fore.RED
            percentage = (vip_configs_count / completed * 100) if completed > 0 else 0
            print(f"\r[{completed}/{total} ({percentage:.1f}%)] Testing configs... {vip_configs_count} working     {color_status}{status}{Style.RESET_ALL}", end='', flush=True)

    print()
    color_print(f"\n[5] Testing complete!", Fore.CYAN)
    color_print(f"[6] Working configurations found and saved: {vip_configs_count}/{completed}", Fore.YELLOW)

    if vip_configs_count > 0:
        color_print(f"\n[✓] SUCCESS! {vip_configs_count} working configs saved to {output_file}", Fore.GREEN, Style.BRIGHT)
    else:
        color_print(f"\n[!] No working configurations found!", Fore.RED)

    color_print("\n" + "=" * 60, Fore.CYAN)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        color_print(f"\n\nProgram interrupted by user! Working configs already saved.", Fore.YELLOW)
    except Exception as e:
        color_print(f"\nUnexpected error: {e}", Fore.RED)
