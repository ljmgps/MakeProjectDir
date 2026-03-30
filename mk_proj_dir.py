#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from typing import List, Tuple, Optional
from collections import deque


# 颜色主题
COLORS = {
    'bg': '#f0f2f5',
    'card_bg': '#ffffff',
    'primary': '#4a90d9',
    'primary_hover': '#3a7bc8',
    'text': '#333333',
    'text_light': '#666666',
    'border': '#dde2e8',
    'success': '#52c41a',
    'warning': '#faad14',
    'error': '#ff4d4f',
}


class Node:
    def __init__(self, name: str, level: int):
        self.name = name.replace('\n', '')  # 节点名字
        self.level = level  # 节点层级
        self.children: List['Node'] = []  # 节点子节点列表
        self.full_path: Path = Path()  # 节点的完整路径

    def __repr__(self) -> str:
        return str(self.full_path)


class Tree:
    def __init__(self):
        self.tree: List[Tuple[Path, List[str]]] = []  # 类似os.walk返回的结构的树结构
        self.nodes: List[Node] = []  # 所有节点的完整路径
        self.root: Path = Path()

    def mk_tree_from_txt(self, path: str, root: Optional[str] = None) -> List[Tuple[Path, List[str]]]:
        '''
        把缩进结构关系转化为类似[(root1,[dir1.1, dir1.2]), (root2,dir2)]结构
        '''
        try:
            self.root = Path(root) if root else self.root
            root_node = Node(str(self.root), -1)  # 根节点
            root_node.full_path = self.root
            dp = [root_node]
            
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    self._process_line(line, dp)
            
            self._build_tree_structure(root_node)
            return self.tree
        except Exception as e:
            print(f"Error building tree: {e}")
            return []

    def _process_line(self, line: str, dp: List[Node]) -> None:
        # 统一处理 Tab 为空格（假设 Tab = 4 空格）
        line = line.replace('\t', '    ')
        name = line.lstrip()
        # 跳过空行
        if not name:
            return
        level = len(line) - len(name)
        node = Node(name, level)
        self.nodes.append(node)

        while dp and node.level <= dp[0].level:
            dp.pop(0)

        if dp:
            node.full_path = dp[0].full_path / node.name
            dp[0].children.append(node)

        dp.insert(0, node)

    def _build_tree_structure(self, root_node: Node) -> None:
        """使用队列遍历树结构，避免重复添加节点"""
        queue = deque([root_node])
        while queue:
            node = queue.popleft()
            if node.children:
                self.tree.append((node.full_path, [child.name for child in node.children]))
                queue.extend(node.children)

    def mk_dir_from_tree(self, root: str, tree: Optional[List[Tuple[Path, List[str]]]] = None) -> None:
        try:
            tree = tree or self.tree
            root_path = Path(root)

            for parent, dirs in tree:
                # parent 已经是完整路径，直接基于它创建
                for dir_name in dirs:
                    (parent / dir_name).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creating directories: {e}")


class ProjectDirCreatorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("项目目录创建工具")
        self.root.geometry("800x600")
        self.root.configure(bg=COLORS['bg'])
        self.root.resizable(True, True)

        # 计算并设置窗口居中
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2
        self.root.geometry(f"800x600+{x}+{y}")

        self._create_widgets()
        self._load_default_tree()

    def _create_widgets(self):
        # 标题栏
        header = tk.Frame(self.root, bg=COLORS['primary'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        title_label = tk.Label(
            header, text="📁 项目目录创建工具",
            bg=COLORS['primary'], fg='white',
            font=("Microsoft YaHei UI", 18, "bold")
        )
        title_label.pack(side='left', padx=20, pady=12)

        help_btn = tk.Button(
            header, text="❓ 使用指南",
            bg=COLORS['primary_hover'], fg='white',
            font=("Microsoft YaHei UI", 10),
            relief='flat', cursor='hand2',
            command=self._show_help
        )
        help_btn.pack(side='right', padx=20, pady=12)

        # 主内容区 - 使用 PanedWindow 实现可调节宽度比例
        content = tk.PanedWindow(self.root, bg=COLORS['bg'], sashrelief='flat', sashwidth=8, bd=0)
        content.pack(fill='both', expand=True, padx=20, pady=20)

        # 左侧配置面板（主要内容）- 默认占据 65% 宽度
        left_panel = tk.Frame(content, bg=COLORS['card_bg'], relief='solid', bd=1, width=520)
        left_panel.pack_propagate(False)  # 保持固定宽度
        content.add(left_panel, width=520)

        # 配置标题
        config_title = tk.Label(
            left_panel, text="⚙️ 配置",
            bg=COLORS['card_bg'], fg=COLORS['text'],
            font=("Microsoft YaHei UI", 12, "bold")
        )
        config_title.pack(anchor='w', pady=(0, 15))

        # 树文件路径
        tree_frame = tk.Frame(left_panel, bg=COLORS['card_bg'])
        tree_frame.pack(fill='x', pady=5)

        tk.Label(
            tree_frame, text="树文件:",
            bg=COLORS['card_bg'], fg=COLORS['text'],
            font=("Microsoft YaHei UI", 10), width=10, anchor='w'
        ).pack(side='left')

        self.entry_tree_path = tk.Entry(tree_frame, width=35, font=("Microsoft YaHei UI", 10))
        self.entry_tree_path.pack(side='left', fill='x', expand=True, padx=(5, 0))

        self.btn_select_tree = tk.Button(
            tree_frame, text="浏览",
            bg=COLORS['primary'], fg='white',
            font=("Microsoft YaHei UI", 9),
            relief='flat', cursor='hand2',
            command=self._select_file
        )
        self.btn_select_tree.pack(side='right', padx=(5, 0))

        # 根目录路径
        root_frame = tk.Frame(left_panel, bg=COLORS['card_bg'])
        root_frame.pack(fill='x', pady=5)

        tk.Label(
            root_frame, text="根目录:",
            bg=COLORS['card_bg'], fg=COLORS['text'],
            font=("Microsoft YaHei UI", 10), width=10, anchor='w'
        ).pack(side='left')

        self.entry_root_path = tk.Entry(root_frame, width=35, font=("Microsoft YaHei UI", 10))
        self.entry_root_path.pack(side='left', fill='x', expand=True, padx=(5, 0))

        self.btn_select_root = tk.Button(
            root_frame, text="浏览",
            bg=COLORS['primary'], fg='white',
            font=("Microsoft YaHei UI", 9),
            relief='flat', cursor='hand2',
            command=self._select_directory
        )
        self.btn_select_root.pack(side='right', padx=(5, 0))

        # 创建按钮
        self.btn_create = tk.Button(
            left_panel, text="🚀 创建目录结构",
            bg=COLORS['success'], fg='white',
            font=("Microsoft YaHei UI", 12, "bold"),
            relief='flat', cursor='hand2',
            command=self._create_directories,
            height=2
        )
        self.btn_create.pack(fill='x', pady=(20, 5))

        # 状态标签
        self.status_label = tk.Label(
            left_panel, text="",
            bg=COLORS['card_bg'], fg=COLORS['text_light'],
            font=("Microsoft YaHei UI", 9)
        )
        self.status_label.pack(pady=(5, 0))

        # 右侧预览面板（次要内容）- 占据剩余空间
        right_panel = tk.Frame(content, bg=COLORS['card_bg'], relief='solid', bd=1)
        content.add(right_panel)

        # 预览标题
        preview_header = tk.Frame(right_panel, bg=COLORS['card_bg'])
        preview_header.pack(fill='x', padx=15, pady=(10, 5))

        tk.Label(
            preview_header, text="👁️ 目录预览",
            bg=COLORS['card_bg'], fg=COLORS['text'],
            font=("Microsoft YaHei UI", 12, "bold")
        ).pack(side='left')

        self.btn_refresh = tk.Button(
            preview_header, text="🔄 刷新",
            bg=COLORS['bg'], fg=COLORS['text'],
            font=("Microsoft YaHei UI", 9),
            relief='flat', cursor='hand2',
            command=self._preview_tree
        )
        self.btn_refresh.pack(side='right')

        # 预览树视图
        tree_scroll_y = tk.Scrollbar(right_panel, orient='vertical')
        tree_scroll_x = tk.Scrollbar(right_panel, orient='horizontal')

        self.preview_tree = ttk.Treeview(
            right_panel,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            show='tree'
        )
        tree_scroll_y.config(command=self.preview_tree.yview)
        tree_scroll_x.config(command=self.preview_tree.xview)

        self.preview_tree.pack(fill='both', expand=True, side='left', padx=(15, 0), pady=(0, 10))
        tree_scroll_y.pack(fill='y', side='right', pady=(0, 10), padx=(0, 15))
        tree_scroll_x.pack(fill='x', side='bottom', padx=(15, 0), pady=(0, 10))

    def _show_help(self):
        """显示使用指南对话框"""
        help_window = tk.Toplevel(self.root)
        help_window.title("使用指南")
        help_window.geometry("500x400")
        help_window.configure(bg=COLORS['bg'])
        help_window.resizable(False, False)

        # 居中显示
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() - 500) // 2
        y = (help_window.winfo_screenheight() - 400) // 2
        help_window.geometry(f"500x400+{x}+{y}")

        # 设置为模态窗口
        help_window.transient(self.root)
        help_window.grab_set()

        # 标题
        tk.Label(
            help_window, text="📖 使用指南",
            bg=COLORS['bg'], fg=COLORS['text'],
            font=("Microsoft YaHei UI", 16, "bold")
        ).pack(pady=(20, 15))

        # 指南内容
        guide_text = """
【树文件格式】
  使用缩进表示目录层级，支持空格或 Tab

  示例：
  项目根目录
      文件夹1
          子文件夹1
          子文件夹2
      文件夹2

【操作步骤】
  1. 点击"浏览"选择树文件（定义目录结构）
  2. 点击"浏览"选择根目录（创建位置）
  3. 点击"创建目录结构"生成目录

【注意事项】
  • 树文件默认查找同目录下的 tree.txt
  • 空行会被自动忽略
  • Tab 会自动转换为 4 个空格
  • 目录已存在时不会重复创建
        """

        text_widget = tk.Text(
            help_window, bg=COLORS['card_bg'],
            fg=COLORS['text'], font=("Microsoft YaHei UI", 10),
            relief='solid', bd=1, padx=15, pady=15,
            wrap='word'
        )
        text_widget.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        text_widget.insert('1.0', guide_text.strip())
        text_widget.config(state='disabled')

        # 关闭按钮
        tk.Button(
            help_window, text="关闭",
            bg=COLORS['primary'], fg='white',
            font=("Microsoft YaHei UI", 10),
            relief='flat', cursor='hand2',
            command=help_window.destroy
        ).pack(pady=(0, 20))

    def _load_default_tree(self):
        default_tree_file = Path(__file__).parent / "tree.txt"
        if default_tree_file.exists():
            self.entry_tree_path.insert(0, str(default_tree_file))
            self.root.after(100, self._preview_tree)

    def _select_file(self):
        file_path = filedialog.askopenfilename(
            title="选择树文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            self.entry_tree_path.delete(0, tk.END)
            self.entry_tree_path.insert(0, file_path)
            self._preview_tree()

    def _select_directory(self):
        dir_path = filedialog.askdirectory(title="选择根目录")
        if dir_path:
            self.entry_root_path.delete(0, tk.END)
            self.entry_root_path.insert(0, dir_path)

    def _preview_tree(self):
        # 清空现有预览
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)

        tree_path = self.entry_tree_path.get()
        if not tree_path or not Path(tree_path).exists():
            self.preview_tree.insert('', 'end', text='← 请先选择有效的树文件')
            return

        try:
            with open(tree_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 解析行，构建父子关系
            items = []  # (name, level, index)
            for line in lines:
                line = line.replace('\t', '    ')
                name = line.rstrip('\n')
                if not name.strip():
                    continue
                level = len(line) - len(line.lstrip())
                items.append((name.strip(), level))

            # 使用栈维护父节点关系
            stack = []  # [(level, iid), ...]
            for name, level in items:
                # 弹出比当前层级深的节点
                while stack and stack[-1][0] >= level:
                    stack.pop()

                # 确定父节点
                parent = '' if not stack else stack[-1][1]

                # 插入树节点
                iid = self.preview_tree.insert(parent, 'end', text=name)
                stack.append((level, iid))

        except Exception as e:
            self.preview_tree.insert('', 'end', text=f'读取文件出错: {e}')

    def _create_directories(self):
        tree_path = self.entry_tree_path.get()
        root_path = self.entry_root_path.get()

        if not tree_path:
            self.status_label.config(text="⚠️ 请选择树文件", fg=COLORS['warning'])
            return
        if not root_path:
            self.status_label.config(text="⚠️ 请选择根目录", fg=COLORS['warning'])
            return

        self.status_label.config(text="⏳ 正在创建目录...", fg=COLORS['primary'])
        self.root.update()

        try:
            tree = Tree()
            tree.mk_tree_from_txt(tree_path, root_path)
            tree.mk_dir_from_tree(root_path)
            self.status_label.config(text="✅ 目录创建成功！", fg=COLORS['success'])
            messagebox.showinfo("成功", "目录创建成功！")
        except Exception as e:
            self.status_label.config(text=f"❌ 创建失败: {e}", fg=COLORS['error'])
            messagebox.showerror("错误", f"创建目录时出错:\n{e}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ProjectDirCreatorGUI()
    app.run()