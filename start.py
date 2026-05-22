import subprocess
import sys
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_requirements():
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            for line in f:
                pkg = line.strip()
                if pkg and not pkg.startswith('#'):
                    pkg_name = pkg.split('>=')[0].split('<=')[0].split('==')[0].strip()
                    pkg_name = pkg_name.replace('-', '_')
                    __import__(pkg_name)
        return True
    except ImportError as e:
        pkg_name = e.name if hasattr(e, 'name') else str(e)
        print(f"缺少依赖: {pkg_name}")
        return False
    except Exception as e:
        print(f"检查依赖时出错: {e}")
        return False

def install_requirements():
    print(f"正在使用 Python {sys.executable} 安装依赖...")
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("依赖安装完成！")
            return True
        else:
            print(f"安装依赖失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"安装依赖时出错: {e}")
        return False

def start_app():
    print("正在启动 AIChat...")
    subprocess.run([sys.executable, 'aichat.py'])

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("=== AIChat 一键启动器 ===")
    print(f"当前 Python: {sys.executable}")
    print()
    
    needs_install = not check_requirements()
    if needs_install:
        print("检测到缺少依赖，正在尝试安装...")
        print()
        if not install_requirements():
            print("无法安装依赖，请手动安装后重试")
            input("按任意键退出...")
            return
        print()
        print("正在准备启动程序...")
        clear_screen()
    
    print("依赖检查通过，正在启动程序...")
    print()
    start_app()

if __name__ == "__main__":
    main()
