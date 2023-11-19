import subprocess
import sys

def install_dependencies(requirements_file):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("Установка зависимостей завершена успешно.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при установке зависимостей: {e}")
        sys.exit(1)

if __name__ == "__main__":
    requirements_file = "./requirements.txt"
    install_dependencies(requirements_file)
