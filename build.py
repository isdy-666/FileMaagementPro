import os
import PyInstaller.__main__

# 配置打包参数
params = [
    'file_explorer.py',  # 主程序文件
    '--name=文件管理器',  # 生成的exe名称
    '--onefile',  # 打包成单个文件
    '--windowed',  # 不显示控制台
    '--clean',  # 清理临时文件
    '--noconfirm',  # 不确认覆盖
]

# 如果图标文件存在，添加图标
if os.path.exists('wjglq.png'):
    params.extend(['--icon=wjglq.png'])

# 添加实际存在的数据文件
data_files = []
if os.path.exists('users.json'):
    data_files.append(('users.json', '.'))
if os.path.exists('wjglq.png'):
    data_files.append(('wjglq.png', '.'))

# 添加所有数据文件
for src, dst in data_files:
    params.extend(['--add-data', f'{src};{dst}'])

# 执行打包
PyInstaller.__main__.run(params)

print('打包完成！exe文件在 dist 目录中。') 