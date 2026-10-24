#!/usr/bin/env python3
"""Configure and inspect optional Claude Code MCP integrations (Python 3.9+)."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

BASE = Path(__file__).resolve().parent
SERVICES = ('playwright', 'github', 'context7')


def template(name):
    return json.loads((BASE / name / 'claude.mcp.example.json').read_text(encoding='utf-8'))['mcpServers'][name]


def load_config(path):
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (ValueError, UnicodeError):
        raise ValueError('配置不是有效 UTF-8 JSON；原文件未修改') from None
    if not isinstance(data, dict) or not isinstance(data.get('mcpServers', {}), dict):
        raise ValueError('配置及 mcpServers 必须是 JSON 对象；原文件未修改')
    return data


def configure(project, services):
    path = project / '.mcp.json'
    if path.is_symlink():
        raise ValueError('不修改符号链接 .mcp.json')
    data = load_config(path)
    servers = data.setdefault('mcpServers', {})
    # Resolve all conflicts before any write; never print existing credentials.
    for name in services:
        if name in servers and servers[name] != template(name):
            raise ValueError(f'{name}: 已有不同配置，请人工合并；原文件未修改')
    changed = any(name not in servers for name in services)
    if not changed:
        print('配置已存在，无需修改')
        return
    for name in services:
        servers[name] = template(name)
    # Private temporary file + atomic replacement: no partial JSON or credential backup.
    fd, temporary = tempfile.mkstemp(prefix='.mcp-', suffix='.tmp', dir=project)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print('已合并 .mcp.json：' + ', '.join(services) + '（仅环境变量引用，未写入凭据）')


def check(project, services):
    data = load_config(project / '.mcp.json')
    failures = []

    def report(label, ok, hint):
        print(f'{"PASS" if ok else "FAIL"} {label}' + ('' if ok else f'：{hint}'))
        if not ok:
            failures.append(label)

    report('Claude Code 命令', bool(shutil.which('claude')), '在启动客户端的同一环境安装 Claude Code')
    for name in services:
        entry = template(name)
        report(f'{name} 配置', data.get('mcpServers', {}).get(name) == entry,
               '先运行 configure；已有自定义配置请按专项文档人工核对')
        for variable in sorted(set(re.findall(r'\$\{([A-Z_][A-Z_0-9]*)\}', json.dumps(entry)))):
            report(f'{name} {variable}', bool(os.environ.get(variable, '').strip()), '在当前进程环境中设置非空值；不显示凭据内容')
        if name == 'github':
            report('github-mcp-server 命令', bool(shutil.which('github-mcp-server')), '按 GitHub 专项说明安装官方二进制并加入 PATH')
        if name == 'playwright':
            report('npx 命令', bool(shutil.which('npx')), '安装兼容的 Node/npm 并加入 PATH')
            node = shutil.which('node')
            major = 0
            if node:
                try:
                    result = subprocess.run([node, '--version'], capture_output=True, text=True, timeout=5)
                    match = re.fullmatch(r'v(\d+)\.\d+\.\d+\s*', result.stdout)
                    if result.returncode == 0 and match:
                        major = int(match[1])
                except (OSError, subprocess.TimeoutExpired):
                    pass
            report('Node >=18（固定 MCP 包最低要求）', major >= 18, '安装兼容版本；浏览器运行要求另行核对')
            print('MANUAL playwright：浏览器、系统依赖及 npm 下载网络需在实际启动中验证')
        if name == 'context7':
            print('MANUAL context7：网络、API key 有效性与额度需通过客户端查询验证')
        if name == 'github':
            print('MANUAL github：token 有效性、仓库权限与只读工具需通过客户端验证')
    print('本地预检结束；不启动 MCP、不联网验证凭据。请继续完成 /mcp 连接与逐项任务验收。')
    return 1 if failures else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('configure', 'check'))
    parser.add_argument('--project', required=True, type=Path, help='目标项目目录，必须已存在')
    parser.add_argument('--services', nargs='+', required=True, choices=(*SERVICES, 'all'))
    args = parser.parse_args(argv)
    project = args.project.resolve()
    if not project.is_dir():
        parser.error('--project 必须是已存在的目录')
    services = SERVICES if 'all' in args.services else tuple(dict.fromkeys(args.services))
    try:
        if args.action == 'configure':
            configure(project, services)
            return 0
        return check(project, services)
    except (OSError, ValueError):
        # Do not expose raw file/OS exception text: paths or invalid JSON may contain secrets.
        print('ERROR 配置处理失败：检查文件权限、JSON 格式、符号链接及同名服务配置冲突；未覆盖冲突配置。', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
