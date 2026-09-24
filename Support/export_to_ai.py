import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# Thêm 'cache' vào danh sách loại trừ để AI không đọc dữ liệu khách hàng
IGNORE_DIRS = {'.git', '__pycache__', 'venv', 'cache', '.streamlit'}
ALLOWED_EXTENSIONS = {'.py', '.bat', '.md'}
OUTPUT_FILE = os.path.join(CURRENT_DIR, 'ai_context.md')

def generate_context():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# TÓM TẮT DỰ ÁN\n> [DÁN NỘI DUNG TỪ CONTEXT HANDOVER]\n\n---\n")
        
        # Phần cấu trúc thư mục
        f.write("# CẤU TRÚC THƯ MỤC\n```text\n")
        for root, dirs, files in os.walk(PROJECT_ROOT):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            level = root.replace(PROJECT_ROOT, '').count(os.sep)
            indent = ' ' * 4 * level
            f.write(f"{indent}|-- {os.path.basename(root)}/\n")
            for file in files:
                if os.path.splitext(file)[1] in ALLOWED_EXTENSIONS:
                    f.write(f"{indent}    |-- {file}\n")
        f.write("```\n\n---\n")

        # Phần nội dung code
        f.write("# CHI TIẾT MÃ NGUỒN\n\n")
        for root, dirs, files in os.walk(PROJECT_ROOT):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file in files:
                if os.path.splitext(file)[1] in ALLOWED_EXTENSIONS and file != 'ai_context.md':
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, PROJECT_ROOT)
                    f.write(f"## File: `{rel_path}`\n```python\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as cf:
                            f.write(cf.read())
                    except: pass
                    f.write("\n```\n\n")
    print(f"✅ Đã gộp code xong tại: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_context()