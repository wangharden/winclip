import os
import re
from pathlib import Path

def parse_log_file(file_path):
    """
    解析单个日志文件，提取所需的指标。
    """
    metrics = {}
    key_map = {
        'i-auroc': 'i_roc',
        'p-auroc': 'p_roc',
        'i-max-f1': 'i_f1',
        'p-max-f1': 'p_f1'
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

    for col_name, log_key in key_map.items():
        pattern = re.compile(rf"{log_key}:\s*([\d\.]+)")
        match = pattern.search(content)

        if match:
            metrics[col_name] = float(match.group(1))
        else:
            metrics[col_name] = 0.0
            print(f"Warning: Metric '{log_key}' not found in {file_path}. Defaulting to 0.0.")
            
    return metrics

def main():
    """
    主函数，执行所有操作。
    """
    # 路径现在是正确的，无需修改
    logger_root_dir = Path('./result_winclip/mvtec-k-0/logger')

    if not logger_root_dir.exists():
        print(f"Error: Directory not found at '{logger_root_dir}'")
        return

    all_results = []
    
    class_dirs = sorted([d for d in logger_root_dir.iterdir() if d.is_dir()])

    for class_dir in class_dirs:
        class_name = class_dir.name
        
        # --- 这是关键的修改 ---
        # 原来的代码: log_file = next(class_dir.glob('*.txt'))
        # 修改后的代码: 寻找以 "log" 开头的文件，不再关心扩展名
        try:
            # 使用 'log*' 匹配所有以 'log' 开头的文件/文件夹
            # 然后用 next() 和一个生成器表达式找到第一个是文件的项
            log_file = next(item for item in class_dir.glob('log*') if item.is_file())
        except StopIteration:
            print(f"Warning: No log file starting with 'log' found in '{class_dir}'. Skipping.")
            continue
            
        metrics = parse_log_file(log_file)
        if metrics:
            metrics['Class'] = class_name
            all_results.append(metrics)

    if not all_results:
        print("No results were parsed. Exiting.")
        return

    # --- 计算和打印部分保持不变 ---
    num_classes = len(all_results)
    avg_results = {
        'Class': 'Average',
        'i-auroc': sum(res['i-auroc'] for res in all_results) / num_classes,
        'p-auroc': sum(res['p-auroc'] for res in all_results) / num_classes,
        'i-max-f1': sum(res['i-max-f1'] for res in all_results) / num_classes,
        'p-max-f1': sum(res['p-max-f1'] for res in all_results) / num_classes,
    }

    headers = ['Class', 'i-auroc', 'p-auroc', 'i-max-f1', 'p-max-f1']
    
    print(f"\n| {' | '.join(headers)} |")
    print(f"|{'|'.join(['-' * (len(h) + 2) for h in headers])}|")

    for res in all_results:
        print(f"| {res['Class']:<11} | {res['i-auroc']:>7.2f} | {res['p-auroc']:>7.2f} | {res['i-max-f1']:>8.2f} | {res['p-max-f1']:>8.2f} |")

    print(f"| {avg_results['Class']:<11} | {avg_results['i-auroc']:>7.2f} | {avg_results['p-auroc']:>7.2f} | {avg_results['i-max-f1']:>8.2f} | {avg_results['p-max-f1']:>8.2f} |")


if __name__ == "__main__":
    main()