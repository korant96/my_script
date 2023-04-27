#!/usr/bin/env python3
import os
import shutil
import subprocess
import re
import threading
from queue import Queue
from colorama import init, Fore, Style


init(autoreset=True)  # 初始化 colorama
num_threads = 32  # 设置同时处理的线程数量

def search_commit(patch_path, start_tag=None, end_tag=None):
    # 读取 patch 文件中的标题
    with open(patch_path) as f:
        content = f.read()
        title_index = content.find('Subject: [PATCH ')
        title_end_index = content.find(']', title_index) + 1
        title = content[title_end_index:].split('\n')[0].strip().replace("[", "").replace("]", "")

    # 构建 git log 命令
    git_log_cmd = ['git', 'log', '--grep', title, '--pretty=format:%H']

    # 添加起始和结束标签（如果提供）
    if start_tag and end_tag:
        git_log_cmd.append(f'{start_tag}..{end_tag}')
    elif start_tag:
        git_log_cmd.append(f'{start_tag}..HEAD')
    elif end_tag:
        git_log_cmd.append(f'HEAD..{end_tag}')

    # 在当前仓库中查找对应的 commit
    result = subprocess.run(git_log_cmd, stdout=subprocess.PIPE)
    commits = result.stdout.decode().strip().split('\n')
    commit = commits[-1] if commits else None

    return commit

def remove_port_or_backport_lines(content_lines):
    new_content_lines = []
    skip_next_line = False
    for i, line in enumerate(content_lines):
        if skip_next_line:
            skip_next_line = False
            if line.strip() == "":
                continue
        if re.search(r"(Port|Backport|port|backport) from [\da-fA-F]+", line):
            skip_next_line = True
        else:
            new_content_lines.append(line)
    return new_content_lines

def parse_patch(patch_path, output_path):
    with open(patch_path) as f:
        content = f.read()

    commit_upstream_pattern1 = re.compile(r"commit [\da-fA-F]+ upstream", re.IGNORECASE | re.MULTILINE)
    commit_upstream_pattern2 = re.compile(r"Upstream commit [\da-fA-F]+", re.IGNORECASE | re.MULTILINE)

    if commit_upstream_pattern1.search(content) or commit_upstream_pattern2.search(content):
        shutil.copy(patch_path, output_path)
    else:
        commit = search_commit(patch_path, start_tag='v5.0', end_tag='v6.2')
        if commit:
            content_lines = content.split('\n')
            for i, line in enumerate(content_lines):
                if line.startswith('Subject:'):
                    break
            i += 1
            while content_lines[i].startswith(' '):
                i += 1
            content_lines.insert(i, f"\ncommit {commit} upstream.")
            content_lines = remove_port_or_backport_lines(content_lines)
            content = '\n'.join(content_lines)

        with open(output_path, 'w') as f:
            f.write(content)

def worker(queue, data_path, output_path, progress):
    while True:
        file_name = queue.get()
        if file_name is None:
            break
        file_path = os.path.join(data_path, file_name)
        new_file_path = os.path.join(output_path, file_name)
        parse_patch(file_path, new_file_path)
        with progress_lock:
            progress[0] += 1
            show_progress(progress[0], progress[1])
        queue.task_done()

def show_progress(completed, total):
    progress = float(completed) / total
    percent = int(progress * 100)
    progress_bar_len = 50
    filled_len = int(progress_bar_len * progress)
    progress_bar = f"{Fore.GREEN}{'=' * filled_len}{Fore.RESET}{Style.RESET_ALL}{Fore.RED}{'-' * (progress_bar_len - filled_len)}{Fore.RESET}{Style.RESET_ALL}"
    print(f'\rProcessing: [{progress_bar}] {percent}%', end='')

def handle_patch_files(data_path, output_path):
    print(f"正在处理位于 {data_path} 的 patch 文件...")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    patch_files = [f for f in os.listdir(data_path) if f.endswith('.patch')]
    work_queue = Queue()

    for file_name in patch_files:
        work_queue.put(file_name)

    threads = []
    progress = [0, len(patch_files)]
    global progress_lock
    progress_lock = threading.Lock()

    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(work_queue, data_path, output_path, progress))
        t.start()
        threads.append(t)

    work_queue.join()

    for _ in range(num_threads):
        work_queue.put(None)

    for t in threads:
        t.join()

    print('\n处理完毕，输出文件位于 {output_path}')

handle_patch_files('/data/path', '/data/output')