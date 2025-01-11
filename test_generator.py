import pytest
from pathlib import Path
from generator import (
    parse_markdown_tree,
    generate_commands,
    validate_path_safety,
    generate_directory_commands,
    SafetyViolation
)

@pytest.fixture
def basic_md_content():
    return """project/
  src/
    - main.py
    - utils.py
  docs/
    - README.md"""

@pytest.fixture
def basic_structure():
    return [
        ("project/", 0),
        ("src/", 1),
        ("main.py", 2),
        ("utils.py", 2),
        ("docs/", 1),
        ("README.md", 2)
    ]

def test_parse_markdown_tree(basic_md_content, basic_structure):
    """Test markdown parsing with different formats"""
    parsed = parse_markdown_tree(basic_md_content)
    assert parsed == basic_structure

    # Test with different bullet points
    content_with_bullets = basic_md_content.replace("-", "*")
    assert parse_markdown_tree(content_with_bullets) == basic_structure

    content_with_plus = basic_md_content.replace("-", "+")
    assert parse_markdown_tree(content_with_plus) == basic_structure

def test_parse_markdown_tree_edge_cases():
    """Test parsing edge cases"""
    # Empty content
    assert parse_markdown_tree("") == []
    
    # Only whitespace
    assert parse_markdown_tree("   \n  \n") == []
    
    # Mixed indentation
    content = """dir/
    file1.txt
  file2.txt"""
    parsed = parse_markdown_tree(content)
    assert len(parsed) == 3
    assert parsed[0] == ("dir/", 0)

def test_validate_path_safety():
    """Test path safety validation"""
    base_path = Path("/test/base")
    
    # Valid paths
    validate_path_safety(Path("normal/path"), base_path)
    validate_path_safety(Path("deep/nested/path"), base_path)
    
    # Invalid paths
    with pytest.raises(SafetyViolation):
        validate_path_safety(Path("../outside"), base_path)
    
    with pytest.raises(SafetyViolation):
        validate_path_safety(Path("/absolute/path"), base_path)
    
    with pytest.raises(SafetyViolation):
        validate_path_safety(Path("path/with spaces"), base_path)
    
    with pytest.raises(SafetyViolation):
        validate_path_safety(Path(".git/config"), base_path)
    
    with pytest.raises(SafetyViolation):
        validate_path_safety(Path("path/with/~/tilde"), base_path)

def test_generate_commands(basic_structure):
    """Test command generation"""
    commands = generate_commands(basic_structure, "test_dir")
    
    # Check basic command structure
    assert any("mkdir -p test_dir/project" in cmd for cmd in commands)
    assert any("touch test_dir/project/src/main.py" in cmd for cmd in commands)
    
    # Check command order (directories before files)
    dir_indices = [i for i, cmd in enumerate(commands) if cmd.startswith("mkdir")]
    file_indices = [i for i, cmd in enumerate(commands) if cmd.startswith("touch")]
    
    for dir_idx in dir_indices:
        for file_idx in file_indices:
            if commands[file_idx].startswith("touch") and commands[file_idx].endswith(commands[dir_idx].split()[-1]):
                assert dir_idx < file_idx

def test_generate_commands_limits():
    """Test command generation limits"""
    # Test max items
    large_structure = [("file{}.txt".format(i), 0) for i in range(101)]
    with pytest.raises(SafetyViolation):
        generate_commands(large_structure, max_items=100)
    
    # Test max depth
    deep_structure = [("deep/folder/path", 11)]
    with pytest.raises(SafetyViolation):
        generate_commands(deep_structure, max_depth=10)

def test_generate_directory_commands_integration(basic_md_content):
    """Integration test for the main function"""
    commands = generate_directory_commands(
        basic_md_content,
        base_dir="test_project",
        max_items=10,
        max_depth=5
    )
    
    assert len(commands) > 0
    assert all(cmd.startswith(("mkdir", "touch")) for cmd in commands)
    assert all("test_project" in cmd for cmd in commands)

def test_directory_command_safety():
    """Test safety features of command generation"""
    dangerous_content = """project/
  ../outside/
    - hack.py"""
    
    with pytest.raises(SafetyViolation):
        generate_directory_commands(dangerous_content)
    
    absolute_path_content = """project/
  /etc/
    - config.txt"""
    
    with pytest.raises(SafetyViolation):
        generate_directory_commands(absolute_path_content)

def test_empty_and_invalid_input():
    """Test handling of empty and invalid input"""
    # Empty input
    assert generate_directory_commands("") == []
    
    # Only whitespace
    assert generate_directory_commands("   \n  \n") == []
    
    # Invalid characters
    with pytest.raises(SafetyViolation):
        generate_directory_commands("project/\n  file*.txt")

def test_duplicate_directory_handling(tmp_path):
    """Test handling of duplicate directory creation"""
    content = """project/
  src/
    - file1.py
  src/
    - file2.py"""
    
    commands = generate_directory_commands(content)
    mkdir_commands = [cmd for cmd in commands if cmd.startswith("mkdir")]
    
    # Check that "src" directory is only created once
    src_commands = [cmd for cmd in mkdir_commands if cmd.endswith("/src")]
    assert len(src_commands) == 1