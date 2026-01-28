import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# --- 环境与架构自检测 ---
def get_exe():
    os_arch = os.environ.get('PROCESSOR_ARCHITECTURE', '').upper()
    os_arch64 = os.environ.get('PROCESSOR_ARCHITEW6432', '').upper()
    # 针对 Win10 x64 + 32位 Python 环境的内核锁定逻辑
    return "rclone-win7-64.exe" if '64' in os_arch or '64' in os_arch64 else "rclone-win7-32.exe"

EXE_NAME = get_exe()

class RcloneUltimateGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rclone 全能助手")
        self.root.geometry("1000x920")
        self.root.configure(bg="#f0f0f0")
        
        self.exe = EXE_NAME
        self.current_process = None
        self.setup_ui()

    def setup_ui(self):
        # 顶栏状态
        tk.Label(self.root, text=f"内核: {self.exe} ", 
                 bg="#2c3e50", fg="white", pady=10, font=("微软雅黑", 10, "bold")).pack(fill="x")

        # --- 路径配置区 ---
        c_frame = tk.Frame(self.root, pady=15, bg="#f0f0f0")
        c_frame.pack(fill="x", padx=25)
        
        for i, (label, var_name, default) in enumerate([
            ("源 (Source):", "src_e", "remote:/"),
            ("目 (Dest):", "dst_e", "D:\\Backup")
        ]):
            tk.Label(c_frame, text=label, bg="#f0f0f0").grid(row=i, column=0, sticky="w")
            setattr(self, var_name, tk.Entry(c_frame, width=82))
            e = getattr(self, var_name)
            e.insert(0, default)
            e.grid(row=i, column=1, padx=8, pady=5)
            tk.Button(c_frame, text=" 浏览本地 ", command=lambda x=e: self.pick(x)).grid(row=i, column=2)

        # --- 参数配置区 ---
        f_frame = tk.Frame(self.root, bg="#f0f0f0", padx=25)
        f_frame.pack(fill="x")
        tk.Label(f_frame, text="全局参数 (Flags):", bg="#f0f0f0").pack(side="left")
        self.flags_e = tk.Entry(f_frame)
        self.flags_e.pack(side="left", fill="x", expand=True, padx=8)
        self.flags_e.insert(0, "-P --transfers 4 --vfs-cache-mode full")
        
        self.stop_btn = tk.Button(f_frame, text=" ⚡ 强制终止 ", bg="#c0392b", fg="white", 
                                  command=self.stop_task, state="disabled")
        self.stop_btn.pack(side="right")

        # --- 功能矩阵 (分类布局) ---
        m_frame = tk.LabelFrame(self.root, text=" 智能控制矩阵 ", bg="#f0f0f0", padx=15, pady=15, font=("微软雅黑", 9, "bold"))
        m_frame.pack(fill="x", padx=25, pady=10)

        # 定义按钮组: [名称, 命令, 颜色, 是否危险]
        btn_configs = [
            # 基础传输
            ("增量同步 (Sync)", "sync", "#e74c3c", False), 
            ("文件复制 (Copy)", "copy", "#2ecc71", False), 
            ("移动文件 (Move)", "move", "#34495e", True), 
            ("双向同步 (Bisync)", "bisync", "#9b59b6", False),
            # 查询统计
            ("列表预览 (Lsf)", "lsf", "#3498db", False), 
            ("树状结构 (Tree)", "tree", "#3498db", False),
            ("容量查询 (About)", "about", "#3498db", False), 
            ("计算大小 (Size)", "size", "#3498db", False),
            # 维护与安全
            ("完整校验 (Check)", "check", "#95a5a6", False),
            ("清理删重 (Dedupe)", "dedupe", "#95a5a6", True),
            ("粉碎目录 (Purge)", "purge", "#e67e22", True),
            ("删除文件 (Delete)", "delete", "#e67e22", True),
            # 挂载与服务
            ("挂载为Z盘 (Mount)", "mount", "#f1c40f", False), 
            ("WebDav 服务", "webdav", "#d35400", False),
            ("HTTP 服务", "http", "#d35400", False),
            ("交互配置 (Config)", "config", "#16a085", False)
        ]

        for i, (name, cmd, color, is_danger) in enumerate(btn_configs):
            fg = "black" if color == "#f1c40f" else "white"
            # 如果是危险命令，按钮加个标识
            display_name = f"⚠️ {name}" if is_danger else name
            tk.Button(m_frame, text=display_name, width=20, bg=color, fg=fg, relief="flat",
                      font=("微软雅黑", 9),
                      command=lambda c=cmd, d=is_danger: self.dispatch(c, d)).grid(row=i//4, column=i%4, padx=6, pady=6)

        # --- 日志区域 ---
        self.log_box = tk.Text(self.root, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10), padx=10, pady=10)
        self.log_box.pack(fill="both", expand=True, padx=25, pady=15)

    def pick(self, entry):
        p = filedialog.askdirectory()
        if p: entry.delete(0, tk.END); entry.insert(0, p.replace("/", "\\"))

    def log(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)

    def stop_task(self):
        if self.current_process:
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.current_process.pid)])
            self.log("\n[!!!] 用户终止了任务进程")

    # --- 参数智能过滤逻辑 (处理互斥) ---
    def filter_flags(self, cmd, raw_flags):
        flags_list = raw_flags.split()
        # VFS/Mount 专属参数黑名单
        mount_only = ["--vfs", "--cache-dir", "--dir-cache", "--attr-timeout"]
        
        if cmd not in ["mount", "webdav", "http"]:
            # 如果不是挂载类命令，自动剔除黑名单中的互斥参数
            filtered = [f for f in flags_list if not any(m in f.lower() for m in mount_only)]
            return filtered
        return flags_list

    def dispatch(self, cmd, is_danger):
        # 1. 安全确认
        if is_danger:
            warn_msg = f"确定要执行【{cmd}】操作吗？\n该操作涉及数据删除或移动，具有不可逆性！"
            if not messagebox.askyesno("危险操作确认", warn_msg):
                return

        s, d = self.src_e.get(), self.dst_e.get()
        raw_flags = self.flags_e.get()

        # 2. 持久化窗口任务 (Mount / Config / Serve)
        if cmd in ["config", "mount", "webdav", "http"]:
            args = f" {cmd} {s}"
            if cmd == "mount": args += f" Z: {raw_flags}"
            elif cmd in ["webdav", "http"]: args += f" {raw_flags}"
            
            os.system(f"start \"Rclone-{cmd}\" {self.exe} {args}")
            self.log(f"> 已开启独立窗口运行: {cmd}")
        else:
            # 3. 实时日志任务 (带参数过滤)
            safe_flags = self.filter_flags(cmd, raw_flags)
            threading.Thread(target=self.worker, args=(cmd, safe_flags), daemon=True).start()

    def worker(self, cmd, flags):
        self.stop_btn.config(state="normal")
        s, d = self.src_e.get(), self.dst_e.get()
        args = [self.exe, cmd, s]
        
        # 定义需要两个路径参数的命令
        if cmd in ["sync", "copy", "move", "bisync", "check"]:
            args.append(d)
        
        args += flags
        
        self.log(f"\n[任务启动]: {' '.join(args)}")
        try:
            # creationflags=0x08000000 用于隐藏子进程产生的黑框，直接将输出捕获到 Text 框
            self.current_process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                                    text=True, shell=True, creationflags=0x08000000)
            for line in self.current_process.stdout:
                self.log(line.strip())
            self.current_process.wait()
            self.log("[任务结束]")
        except Exception as e:
            self.log(f"运行时错误: {e}")
        finally:
            self.stop_btn.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    # 彻底解决 32位环境下的兼容性问题，只使用原生组件
    app = RcloneUltimateGUI(root)
    root.mainloop()