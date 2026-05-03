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
    for pkg in ['colorama', 'requests', 'urllib3']:
        try:
            __import__(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])

install_packages()

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
stop_testing = False

def signal_handler(sig, frame):
    global stop_testing
    stop_testing = True
    print("\n" + Fore.YELLOW + "[!] Stopping...")

signal.signal(signal.SIGINT, signal_handler)

def color_print(text, color=Fore.WHITE, style=Style.NORMAL):
    print(f"{style}{color}{text}{Style.RESET_ALL}")

def test_single_config(line, timeout=1):
    if stop_testing or not line.strip():
        return line, False
    try:
        host, port = None, None
        if line.startswith('vless://'):
            from urllib.parse import urlparse
            parsed = urlparse(line)
            if '@' in parsed.netloc:
                hp = parsed.netloc.split('@')[1]
                if ':' in hp:
                    host, port = hp.split(':')
        elif line.startswith('vmess://'):
            import base64
            enc = line.replace('vmess://', '')
            try:
                dec = base64.b64decode(enc).decode('utf-8')
                cfg = json.loads(dec)
                host = cfg.get('add')
                port = str(cfg.get('port'))
            except:
                pass
        elif line.startswith('trojan://') or line.startswith('ss://'):
            from urllib.parse import urlparse
            parsed = urlparse(line)
            host = parsed.hostname
            port = parsed.port
        if host and port:
            url = f"http://{host}:{port}/"
            with requests.Session() as sess:
                sess.headers.update(HEADERS)
                sess.verify = False
                r = sess.get(url, timeout=timeout)
                if r.status_code < 500:
                    time.sleep(random.uniform(0.05, 0.2))
                    return line, True
        return line, False
    except:
        return line, False

def read_configs(fname):
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            return [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        color_print(f"Error: {fname} not found!", Fore.RED)
        return []

def append_working(cfg, outfile):
    with open(outfile, 'a', encoding='utf-8') as f:
        f.write(cfg + '\n')

def git_commit_push():
    try:
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=False, capture_output=True)
        subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], check=False, capture_output=True)
        subprocess.run(["git", "add", "cleaned_configs.txt", "success_config.txt", "link_stats.json", "README.md"], check=True, capture_output=True)
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if result.returncode != 0:
            commit_msg = f"Auto-update after batch - {time.strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True)
            push_result = subprocess.run(["git", "push"], capture_output=True)
            if push_result.returncode != 0:
                color_print(f"[!] Push failed: {push_result.stderr.decode()}", Fore.YELLOW)
            else:
                color_print("[✓] Committed and pushed.", Fore.GREEN)
        else:
            color_print("[*] No changes to commit.", Fore.CYAN)
    except subprocess.CalledProcessError as e:
        color_print(f"[!] Git error: {e}", Fore.RED)

def main():
    color_print("="*60, Fore.CYAN)
    color_print("V2RAY TESTER (BATCH 7000, AUTO-COMMIT)", Fore.YELLOW, Style.BRIGHT)
    color_print("="*60, Fore.CYAN)

    input_file = 'cleaned_configs.txt'
    out_file = 'success_config.txt'
    if os.path.exists(out_file):
        os.remove(out_file)

    configs = read_configs(input_file)
    if not configs:
        color_print("No configs to test!", Fore.RED)
        sys.exit(1)

    total = len(configs)
    color_print(f"[*] Total unique configs: {total}", Fore.GREEN)

    BATCH = 7000
    WORKERS = 10
    TIMEOUT = 1

    working_total = 0
    processed = 0
    batch_num = 1

    for start in range(0, total, BATCH):
        if stop_testing:
            break
        end = min(start+BATCH, total)
        batch_configs = configs[start:end]
        batch_working = 0
        color_print(f"\n[Batch {batch_num}] Testing {start+1}-{end} ({len(batch_configs)} items)...", Fore.CYAN)

        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futures = {ex.submit(test_single_config, cfg, TIMEOUT): cfg for cfg in batch_configs}
            for fut in as_completed(futures):
                if stop_testing:
                    ex.shutdown(wait=False)
                    break
                try:
                    cfg, ok = fut.result(timeout=TIMEOUT+0.5)
                except:
                    cfg = futures[fut]
                    ok = False
                processed += 1
                if ok:
                    working_total += 1
                    batch_working += 1
                    append_working(cfg, out_file)
                pct = (working_total / processed * 100) if processed else 0
                mark = "✓" if ok else "✗"
                col = Fore.GREEN if ok else Fore.RED
                print(f"\r[{processed}/{total} ({pct:.1f}%)] Working: {working_total}  {col}{mark}{Style.RESET_ALL}", end='', flush=True)

        color_print(f"\n[Batch {batch_num}] Working in batch: {batch_working}/{len(batch_configs)}", Fore.MAGENTA)
        batch_num += 1

        color_print("[*] Updating README and committing...", Fore.CYAN)
        subprocess.run([sys.executable, "update_readme.py"], check=False)
        git_commit_push()

        if end < total:
            slp = random.uniform(1.0, 2.0)
            color_print(f"[*] Sleeping {slp:.1f}s...", Fore.CYAN)
            time.sleep(slp)

    print()
    color_print(f"\n[✓] Done. Working configs: {working_total}/{total}", Fore.GREEN)
    color_print("="*60, Fore.CYAN)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        color_print("\n[!] Interrupted, saved partial results.", Fore.YELLOW)
        git_commit_push()
    except Exception as e:
        color_print(f"\n[ERROR] {e}", Fore.RED)
        sys.exit(1)
