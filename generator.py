from pathlib import Path
import re
from typing import List, Tuple, Dict, Optional

class SafetyViolation(Exception):
    """Exception raised when a safety check fails."""
    pass

class TreeNode:
    def __init__(self, name: str, is_dir: bool = False, comment: str = ""):
        self.name = name
        self.is_dir = is_dir
        self.comment = comment
        self.children = []
        self.parent = None

    def add_child(self, child: 'TreeNode') -> None:
        child.parent = self
        self.children.append(child)

def parse_tree_input(tree_content: str) -> TreeNode:
    """Parse tree-command style input into a tree structure."""
    lines = [line.rstrip() for line in tree_content.splitlines() if line.strip()]
    
    # Initialize root node from the first line
    root_line = lines[0].rstrip('/')
    root = TreeNode(root_line, is_dir=True)
    
    current_node = root
    depth_map: Dict[int, TreeNode] = {0: root}
    previous_depth = 0
    
    for line in lines[1:]:
        # Skip empty lines
        if not line.strip():
            continue
            
        # Calculate depth based on leading characters
        leading_space = len(line) - len(line.lstrip('│ ├└'))
        depth = leading_space // 2  # Each level adds '│   ' (4 chars)
        
        # Extract name and comment
        clean_line = line.lstrip('│ ├└─ ')
        name_comment = clean_line.split('#', 1)
        name = name_comment[0].strip().rstrip('/')
        comment = name_comment[1].strip() if len(name_comment) > 2 else ""
        
        # Determine if it's a directory
        is_dir = '/' in line or '__init__.py' in name or (
            '.' not in name and not name.endswith(('.py', '.txt', '.md', '.json'))
        )
        
        # Create new node
        new_node = TreeNode(name, is_dir=is_dir, comment=comment)
        
        # Find parent node
        if depth > previous_depth:
            parent_node = current_node
        else:
            parent_node = depth_map[depth - 1]
        
        # Add node to parent
        parent_node.add_child(new_node)
        
        # Update tracking variables
        depth_map[depth] = new_node
        current_node = new_node
        previous_depth = depth
        
    return root

def generate_tree_output(node: TreeNode, prefix: str = "", is_last: bool = True, 
                        include_comments: bool = True) -> List[str]:
    """Generate tree-style output for directory structure."""
    output = []
    
    if node.name != ".":  # Don't print root node
        marker = "└── " if is_last else "├── "
        line = prefix + marker + node.name
        if include_comments and node.comment:
            line += f"  # {node.comment}"
        output.append(line)
        
        new_prefix = prefix + ("    " if is_last else "│   ")
    else:
        new_prefix = ""
    
    # Sort children: directories first, then files, both alphabetically
    sorted_children = sorted(
        node.children,
        key=lambda x: (not x.is_dir, x.name.lower())
    )
    
    for i, child in enumerate(sorted_children):
        is_last_child = i == len(sorted_children) - 1
        output.extend(generate_tree_output(child, new_prefix, is_last_child, include_comments))
    
    return output

def generate_commands(root: TreeNode, base_path: str = '.') -> List[str]:
    """Generate shell commands to create the directory structure."""
    commands = []
    base = Path(base_path)
    
    def traverse(node: TreeNode, current_path: Path):
        if node.name != ".":
            path = current_path / node.name
            if node.is_dir:
                commands.append(f"mkdir -p {path}")
            else:
                if path.parent != current_path:
                    commands.append(f"mkdir -p {path.parent}")
                commands.append(f"touch {path}")
        
        for child in node.children:
            traverse(child, current_path / node.name if node.name != "." else current_path)
    
    traverse(root, base)
    return commands

def generate_tree_representation(tree_content: str, include_comments: bool = True) -> str:
    """Generate a tree command style representation of the directory structure."""
    try:
        root = parse_tree_input(tree_content)
        
        # Count directories and files
        def count_nodes(node: TreeNode) -> Tuple[int, int]:
            dirs = 1 if node.is_dir and node.name != "." else 0
            files = 1 if not node.is_dir else 0
            for child in node.children:
                d, f = count_nodes(child)
                dirs += d
                files += f
            return dirs, files
        
        dir_count, file_count = count_nodes(root)
        if root.name != ".":
            dir_count -= 1  # Don't count root directory
        
        # Generate tree lines
        tree_lines = [root.name]
        tree_lines.extend(generate_tree_output(root, include_comments=include_comments))
        tree_lines.append(f"\n{dir_count} directories, {file_count} files")
        
        return "\n".join(tree_lines)
    except Exception as e:
        raise SafetyViolation(str(e))

def generate_directory_commands(tree_content: str) -> List[str]:
    """Generate shell commands to create the directory structure."""
    try:
        root = parse_tree_input(tree_content)
        return generate_commands(root)
    except Exception as e:
        raise SafetyViolation(str(e))