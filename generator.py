from pathlib import Path
import re

class SafetyViolation(Exception):
    """Exception raised when a safety check fails."""
    pass

def parse_markdown_tree(md_content: str) -> list:
    """Parse markdown content to extract directory structure."""
    structure = []
    for line in md_content.splitlines():
        if not line.strip():
            continue
        
        leading_spaces = len(line) - len(line.lstrip())
        depth = leading_spaces // 2  # Assuming 2 spaces per level
        
        # Remove markdown bullets and spaces
        cleaned_line = re.sub(r'^[\s]*[-*+]\s*', '', line.strip())
        
        if cleaned_line:
            structure.append((cleaned_line, depth))
            
    return structure

def validate_path_safety(path: Path, base_path: Path) -> None:
    """Validate that a path is safe to create."""
    try:
        full_path = (base_path / path).resolve()
        base_resolved = base_path.resolve()
        
        if not str(full_path).startswith(str(base_resolved)):
            raise SafetyViolation(f"Path '{path}' would be outside base directory")
            
        if any(pattern in str(path) for pattern in ['..', '~', '//', '.git']):
            raise SafetyViolation(f"Path '{path}' contains suspicious pattern")
            
        if str(path).startswith('/'):
            raise SafetyViolation(f"Absolute paths not allowed: '{path}'")
            
        if len(str(full_path)) > 255:
            raise SafetyViolation(f"Path too long: '{path}'")
            
        if not re.match(r'^[\w./\-]+$', str(path)):
            raise SafetyViolation(f"Path contains invalid characters: '{path}'")
            
    except Exception as e:
        if not isinstance(e, SafetyViolation):
            raise SafetyViolation(f"Path validation error: {e}")
        raise

def generate_commands(structure: list, base_path: str = '.', max_items: int = 100, max_depth: int = 10) -> list:
    """Generate mkdir and touch commands for the directory structure."""
    if len(structure) > max_items:
        raise SafetyViolation(f"Too many items: {len(structure)} (max: {max_items})")
    
    commands = []
    current_path = Path(base_path)
    path_stack = [current_path]
    created_dirs = set()
    
    for item, depth in structure:
        if depth > max_depth:
            raise SafetyViolation(f"Directory depth {depth} exceeds maximum {max_depth}")
        
        while len(path_stack) > depth + 1:
            path_stack.pop()
        
        current_path = path_stack[depth]
        new_path = current_path / item
        
        validate_path_safety(new_path, Path(base_path))
        
        if item.endswith(('/')) or '.' not in item:
            dir_path = str(new_path).rstrip('/')
            if dir_path not in created_dirs:
                commands.append(f"mkdir -p {dir_path}")
                created_dirs.add(dir_path)
            path_stack.append(Path(dir_path))
        else:
            if new_path.parent != current_path and str(new_path.parent) not in created_dirs:
                commands.append(f"mkdir -p {new_path.parent}")
                created_dirs.add(str(new_path.parent))
            commands.append(f"touch {new_path}")
    
    return commands

def generate_directory_commands(markdown_content: str, base_dir: str = ".", max_items: int = 100, max_depth: int = 10) -> list:
    """Main function to generate commands from markdown content."""
    try:
        structure = parse_markdown_tree(markdown_content)
        commands = generate_commands(structure, base_dir, max_items, max_depth)
        return commands
    except Exception as e:
        raise SafetyViolation(str(e))

