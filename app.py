import streamlit as st
from pathlib import Path
import json
from generator import generate_directory_commands, SafetyViolation

st.set_page_config(
    page_title="Directory Tree Generator",
    page_icon="📁",
    initial_sidebar_state="expanded",
)

# Load example structures
def load_examples():
    examples_dir = Path("examples")
    examples = {"Custom": ""}
    if examples_dir.exists():
        for md_file in examples_dir.glob("*.md"):
            with open(md_file, "r") as f:
                examples[md_file.stem] = f.read()
    return examples

EXAMPLES = load_examples()

# Sidebar settings
st.sidebar.header("Settings")
base_dir = st.sidebar.text_input("Base Directory", ".")
max_items = st.sidebar.number_input("Max Items", min_value=1, max_value=500, value=100)
max_depth = st.sidebar.number_input("Max Depth", min_value=1, max_value=20, value=10)

# Main content
st.title("Directory Structure Generator")

example_key = st.selectbox(
    "Load Example Structure",
    list(EXAMPLES.keys())
)

markdown_input = st.text_area(
    "Directory Structure (Markdown)",
    value=EXAMPLES.get(example_key, ""),
    height=300,
    help="Enter your directory structure using markdown format"
)

if st.button("Generate Commands", type="primary"):
    try:
        commands = generate_directory_commands(
            markdown_input,
            base_dir=base_dir,
            max_items=max_items,
            max_depth=max_depth
        )
        
        if commands:
            st.subheader("Generated Commands")
            commands_text = "\n".join(commands)
            st.code(commands_text, language="bash")
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "Download as Shell Script",
                    commands_text,
                    file_name="create_structure.sh",
                    mime="text/plain"
                )
            with col2:
                st.button("Copy to Clipboard", 
                         help="Click to copy commands",
                         on_click=lambda: st.write(
                             f'<script>navigator.clipboard.writeText(`{commands_text}`)</script>',
                             unsafe_allow_html=True
                         ))
        else:
            st.warning("No valid structure found in input")
            
    except SafetyViolation as e:
        st.error(f"Safety check failed: {str(e)}")
    except Exception as e:
        st.error(f"Error generating commands: {str(e)}")

# Help section
with st.expander("Usage Guide"):
    st.markdown("""
    ### Input Format
    - Use indentation (2 spaces) or markdown bullets (-)
    - Add trailing slash (/) for directories
    - Files don't need trailing slash
    
    ### Safety Features
    - Path traversal prevention
    - Maximum file/directory limits
    - Depth restrictions
    - Character validation
    - Base directory containment
    
    ### Limitations
    - Max files/directories: Adjustable (default 100)
    - Max depth: Adjustable (default 10)
    - Allowed characters: A-Z, a-z, 0-9, _, -, ., /
    - No spaces in paths
    - No absolute paths
    """)