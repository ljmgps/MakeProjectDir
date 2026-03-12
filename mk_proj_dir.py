#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import List, Tuple, Optional
from collections import deque

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
        self.root.title("Project Directory Creator")
        self._create_widgets()

    def _create_widgets(self):
        # 树文件路径
        label_tree_path = tk.Label(self.root, text="树文件路径:")
        label_tree_path.grid(row=0, column=0, padx=10, pady=10)

        self.entry_tree_path = tk.Entry(self.root, width=50)
        self.entry_tree_path.grid(row=0, column=1, padx=10, pady=10)

        # 设置默认路径
        default_tree_file = Path(__file__).parent / "tree.txt"
        if default_tree_file.exists():
            self.entry_tree_path.insert(0, str(default_tree_file))

        button_select_tree = tk.Button(self.root, text="选择文件", command=self._select_file)
        button_select_tree.grid(row=0, column=2, padx=10, pady=10)

        # 根目录路径
        label_root_path = tk.Label(self.root, text="根目录路径:")
        label_root_path.grid(row=1, column=0, padx=10, pady=10)

        self.entry_root_path = tk.Entry(self.root, width=50)
        self.entry_root_path.grid(row=1, column=1, padx=10, pady=10)

        button_select_root = tk.Button(self.root, text="选择目录", command=self._select_directory)
        button_select_root.grid(row=1, column=2, padx=10, pady=10)

        button_create = tk.Button(self.root, text="创建目录", command=self._create_directories)
        button_create.grid(row=2, column=1, pady=20)

    def _select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.entry_tree_path.delete(0, tk.END)
            self.entry_tree_path.insert(0, file_path)

    def _select_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.entry_root_path.delete(0, tk.END)
            self.entry_root_path.insert(0, dir_path)

    def _create_directories(self):
        tree_path = self.entry_tree_path.get()
        root_path = self.entry_root_path.get()

        if not tree_path or not root_path:
            messagebox.showwarning("输入错误", "请选择树文件和根目录。")
            return

        tree = Tree()
        tree.mk_tree_from_txt(tree_path, root_path)
        tree.mk_dir_from_tree(root_path)
        messagebox.showinfo("成功", "目录创建成功！")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ProjectDirCreatorGUI()
    app.run()