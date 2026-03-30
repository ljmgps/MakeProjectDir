# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A tkinter GUI desktop tool that creates project directory structures from indented text files. Users define a tree structure using indentation (spaces or tabs), and the tool generates the corresponding folder hierarchy.

## Architecture

- **`mk_proj_dir.py`** - Main application with three core classes:
  - `Node` - Represents a directory node with name, level, children, and full path
  - `Tree` - Parses indented text into tree structure, builds directory hierarchy
  - `ProjectDirCreatorGUI` - Modern tkinter GUI with ttk Treeview preview, color theme, and status feedback

- **`mk_proj_dir.spec`** - PyInstaller spec file for building standalone Windows executable

## Commands

### Run the application
```bash
python mk_proj_dir.py
```

### Build executable (from ProjectDirCreator directory)
```bash
pyinstaller mk_proj_dir.spec
```

The built executable is placed in `dist/mk_proj_dir.exe`.

## Tree File Format

Uses indentation to represent directory hierarchy. Tab characters are automatically converted to 4 spaces. Empty lines are skipped.

```
ProjectRoot
    Folder1
        SubFolder1
        SubFolder2
    Folder2
```

## Key Implementation Details

- `Tree.mk_tree_from_txt()` parses the indented text and returns structure as `List[Tuple[Path, List[str]]]` (parent path, child names)
- `Tree.mk_dir_from_tree()` creates directories using `Path.mkdir(parents=True, exist_ok=True)`
- GUI default tree file path is `tree.txt` in the same directory as the script
