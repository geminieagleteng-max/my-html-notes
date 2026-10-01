import os
import sys
import re
import glob
import shutil
import subprocess
from datetime import datetime

# 設定 Windows 控制台 UTF-8 輸出，避免 CP950 編碼問題
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 設定搜尋 HTML 筆記的資料夾路徑 ('.' 代表目前資料夾)
NOTES_DIR = "."
INDEX_FILE = "index.html"

# 自動排外檔案與目錄
EXCLUDE_FILES = {INDEX_FILE}
EXCLUDE_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules"}

def safe_print(msg):
    """安全列印訊息，處理 Windows console 編碼例外"""
    try:
        print(msg)
    except UnicodeEncodeError:
        # 去除全域 emoji
        clean_msg = msg.encode("ascii", "ignore").decode("ascii")
        print(clean_msg)

def get_html_title(file_path):
    """嘗試從 HTML 檔案中讀取 <title> 標籤內容，若無則使用檔名"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(4096)  # 讀取前 4KB 解析標籤
            match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
            if match and match.group(1).strip():
                return match.group(1).strip()
    except Exception as e:
        safe_print(f"[!] 解析 {file_path} 標籤時留意: {e}")
    
    # 預設：使用除去檔名副標題的簡潔檔名
    base_name = os.path.basename(file_path)
    return os.path.splitext(base_name)[0].replace("_", " ").replace("-", " ")

def collect_notes():
    """搜集所有 HTML 筆記資訊"""
    notes = []
    for root, dirs, files in os.walk(NOTES_DIR):
        # 排除特定目錄
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        
        for file in files:
            if file.endswith(".html") and file not in EXCLUDE_FILES:
                rel_path = os.path.relpath(os.path.join(root, file), NOTES_DIR).replace("\\", "/")
                abs_path = os.path.join(root, file)
                
                mod_time = os.path.getmtime(abs_path)
                formatted_time = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M")
                
                title = get_html_title(abs_path)
                
                notes.append({
                    "title": title,
                    "path": rel_path,
                    "filename": file,
                    "mtime": mod_time,
                    "date": formatted_time
                })
    
    # 依照最後修改時間倒序排列（最新的在最上面）
    notes.sort(key=lambda x: x["mtime"], reverse=True)
    return notes

def generate_index_html(notes):
    """自動生成質感現代化的 GitHub Pages 總目錄頁面"""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cards_html = ""
    for note in notes:
        cards_html += f"""
        <a href="{note['path']}" class="note-card">
            <div class="note-card-header">
                <div class="note-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                </div>
                <span class="note-date">{note['date']}</span>
            </div>
            <h3 class="note-title">{note['title']}</h3>
            <div class="note-path">📂 {note['path']}</div>
        </a>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📚 我的線上雲端筆記頁面</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.1);
            --card-hover-border: #6366f1;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent: #6366f1;
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            --shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', 'Noto Sans TC', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 2.5rem 1rem;
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.15) 0px, transparent 50%);
            background-attachment: fixed;
        }}

        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            margin-bottom: 2.5rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--card-border);
        }}

        .title {{
            font-size: 2.2rem;
            font-weight: 700;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            display: inline-block;
        }}

        .subtitle {{
            color: var(--text-secondary);
            font-size: 1rem;
        }}

        .stats-bar {{
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            margin-top: 1.2rem;
            font-size: 0.9rem;
        }}

        .stat-badge {{
            background: rgba(255, 255, 255, 0.05);
            padding: 0.4rem 0.9rem;
            border-radius: 20px;
            border: 1px solid var(--card-border);
            color: var(--text-secondary);
        }}

        .stat-badge strong {{
            color: var(--text-primary);
        }}

        .search-box {{
            margin-bottom: 2rem;
            position: relative;
        }}

        .search-input {{
            width: 100%;
            padding: 1rem 1.2rem 1rem 3rem;
            background: var(--bg-secondary);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 1rem;
            outline: none;
            transition: all 0.3s ease;
        }}

        .search-input:focus {{
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);
        }}

        .search-icon {{
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-secondary);
            pointer-events: none;
        }}

        .notes-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1.25rem;
        }}

        .note-card {{
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 1.25rem;
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
        }}

        .note-card:hover {{
            transform: translateY(-4px);
            border-color: var(--card-hover-border);
            box-shadow: 0 15px 35px -10px rgba(99, 102, 241, 0.3);
        }}

        .note-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }}

        .note-icon {{
            width: 36px;
            height: 36px;
            border-radius: 8px;
            background: rgba(99, 102, 241, 0.15);
            color: #818cf8;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .note-date {{
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}

        .note-title {{
            font-size: 1.15rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            line-height: 1.4;
            color: #f1f5f9;
        }}

        .note-path {{
            font-size: 0.8rem;
            color: #64748b;
            word-break: break-all;
            margin-top: auto;
        }}

        .empty-state {{
            text-align: center;
            padding: 4rem 1rem;
            color: var(--text-secondary);
            grid-column: 1 / -1;
        }}

        footer {{
            text-align: center;
            margin-top: 4rem;
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1 class="title">📖 我的線上 HTML 雲端筆記</h1>
            <p class="subtitle">自動同步與發布至 GitHub Pages</p>
            <div class="stats-bar">
                <div class="stat-badge">筆記總數: <strong>{len(notes)}</strong> 篇</div>
                <div class="stat-badge">最後更新: <strong>{now_str}</strong></div>
            </div>
        </header>

        <div class="search-box">
            <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input type="text" id="searchInput" class="search-input" placeholder="搜尋筆記標題或檔名...">
        </div>

        <div class="notes-grid" id="notesGrid">
            {cards_html if cards_html else '<div class="empty-state">📌 目前資料夾中還沒有任何 .html 筆記檔案。</div>'}
        </div>

        <footer>
            <p>Powered by Python Auto-Sync Script & GitHub Pages</p>
        </footer>
    </div>

    <script>
        document.getElementById('searchInput').addEventListener('input', function(e) {{
            const query = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('.note-card');

            cards.forEach(card => {{
                const title = card.querySelector('.note-title').textContent.toLowerCase();
                const path = card.querySelector('.note-path').textContent.toLowerCase();
                if (title.includes(query) || path.includes(query)) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }});
    </script>
</body>
</html>
"""
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    safe_print(f"[+] 已成功生成/更新目錄頁面: {INDEX_FILE}")

def run_cmd(cmd):
    """執行指令並返回結果"""
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True, encoding="utf-8", errors="replace")
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def sync_to_github():
    """將更新自動推送到 GitHub"""
    safe_print("\n[>] 開始 Git 自動同步作業...")
    
    # 檢查是否初始化 Git
    if not os.path.exists(".git"):
        safe_print("[⚙️] 檢測到此資料夾尚未初始化 Git，正在執行 git init...")
        run_cmd("git init")
        run_cmd("git branch -M main")
    
    # Git add
    safe_print("[+] 正在把檔案加入暫存區 (git add .)...")
    run_cmd("git add .")
    
    # Git commit
    commit_msg = f"Auto sync notes: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    safe_print(f"[+] 正在建立提交 (git commit -m '{commit_msg}')...")
    code, out, err = run_cmd(f'git commit -m "{commit_msg}"')
    if "nothing to commit" in out or "nothing to commit" in err:
        safe_print("[i] 沒有新變更需要提交。")
    else:
        first_line = out.splitlines()[0] if out else ""
        safe_print(f"[+] 提交成功: {first_line}")

    # 檢查是否有設定 remote
    code, remote_out, _ = run_cmd("git remote -v")
    if not remote_out:
        safe_print("\n[!] 提示：您尚未連結至 GitHub 遠端倉庫 (remote)。")
        safe_print("請在 GitHub 建立 Repository 後，執行以下指令連結：")
        safe_print("   git remote add origin https://github.com/geminieagleteng-max/my-html-notes.git")
        safe_print("連結完成後，再次執行本腳本即可一鍵推送！")
        return

    # Git push
    safe_print("[^] 正在同步推送至 GitHub (git push origin main)...")
    push_code, push_out, push_err = run_cmd("git push -u origin main")
    if push_code == 0:
        safe_print("\n[🎉] 成功同步上傳至 GitHub！GitHub Pages 將會在數秒內完成部署變更！")
    else:
        safe_print(f"\n[X] Push 失敗，詳細訊息如下:\n{push_err or push_out}")
        safe_print("[!] 請確認遠端倉庫網址正確且已有權限。")

def main():
    safe_print("========================================")
    safe_print("   線上 HTML 筆記自動同步與 GitHub Pages 部署工具")
    safe_print("========================================\n")

    # 嘗試調用整合版的全學科大一統總目錄產生器
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "錄音轉筆記", "audio2report_assistant_v1.0")))
    generated_rich_index = False
    try:
        from audio2report_assistant import generate_master_index
        archive_base_dir = r"G:\我的雲端硬碟\高中學習資料\錄音檔整理筆記"
        if os.path.exists(archive_base_dir):
            safe_print("[*] 正在從雲端硬碟歸檔目錄產生具備 D3 星系心智圖與快閃卡的全功能總目錄...")
            generate_master_index(archive_base_dir)
            master_idx_path = os.path.join(archive_base_dir, "index.html")
            if os.path.exists(master_idx_path):
                shutil.copy2(master_idx_path, INDEX_FILE)
                generated_rich_index = True
                safe_print(f"[+] 已成功匯入全功能導覽總頁面: {INDEX_FILE}")
    except Exception as e:
        safe_print(f"[!] 使用全功能總目錄產生器時留意: {e}")

    if not generated_rich_index:
        notes = collect_notes()
        safe_print(f"[*] 掃描完成，共找到 {len(notes)} 篇 HTML 筆記。")
        for n in notes:
            safe_print(f"   • [{n['date']}] {n['title']} ({n['path']})")
        safe_print("")
        generate_index_html(notes)

    sync_to_github()

if __name__ == "__main__":
    main()
