import re
import shutil
from datetime import datetime


def backup_file(file_path):
    # 获取当前时间戳
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    # 构造备份文件路径
    backup_path = f"{file_path}.bak.{timestamp}"
    # 复制文件
    shutil.copy2(file_path, backup_path)
    return backup_path

def replace_value_in_config(file_path, key, new_value):
    # 读取 config.yaml 文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    # 使用正则表达式替换指定键的值
    pattern = re.compile(f'wengine_vpn_ticketwebvpn_beihua_edu_cn=(\S+);')
    # 替换为新的值
    replacement = f'wengine_vpn_ticketwebvpn_beihua_edu_cn={new_value};'
    new_content = pattern.sub(replacement, content)

    # 写回修改后的内容到 config.yaml 文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)