import streamlit as st
from pathlib import Path
from generator import generate_directory_commands, generate_tree_representation, SafetyViolation

# Configure the page
st.set_page_config(
    page_title="Directory Tree Generator",
    page_icon="🌳",
    initial_sidebar_state="expanded",
)

# Example tree structures
EXAMPLES = {
    "Python Package": """python_package/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── main.py        # Core functionality
│   └── utils/
│       ├── __init__.py
│       └── helpers.py     # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_core.py      # Core tests
│   └── test_utils.py     # Utility tests
├── docs/
│   ├── guide.md          # User guide
│   └── api.md            # API documentation
└── README.md             # Project documentation""",

    "ML Project": """ml_project/
├── data/
│   ├── raw/              # Original data
│   │   └── dataset.csv
│   └── processed/        # Cleaned data
│       └── clean_data.csv
├── models/
│   ├── __init__.py
│   ├── training.py       # Model training code
│   └── evaluation.py     # Model evaluation
├── notebooks/
│   ├── EDA.ipynb        # Exploratory analysis
│   └── Training.ipynb    # Training notebook
└── requirements.txt      # Project dependencies""",

    "Backend Service": """backend_service/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py     # API endpoints
│   │   └── models.py     # Data models
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py        # Database connection
│   └── services/
│       ├── __init__.py
│       └── auth.py      # Authentication service
├── config/
│   └── settings.py      # Configuration
└── main.py              # Application entry point"""
}

def handle_example_button(example_name: str):
    """Handle example button click event"""
    if example_name in EXAMPLES:
        st.session_state["tree_input_value"] = EXAMPLES[example_name]

def render_sidebar():
    """Render sidebar settings"""
    st.sidebar.header("Settings")
    settings = {
        "base_dir": st.sidebar.text_input("Base Directory", "."),
        "max_items": st.sidebar.number_input("Max Items", min_value=1, max_value=500, value=100),
        "max_depth": st.sidebar.number_input("Max Depth", min_value=1, max_value=20, value=10),
        "include_comments": st.sidebar.checkbox("Include Comments", value=True)
    }
    return settings

def render_example_buttons():
    """Render example buttons in columns"""
    st.subheader("📚 Load Example Structure")
    cols = st.columns(len(EXAMPLES))
    for col, (name, _) in zip(cols, EXAMPLES.items()):
        if col.button(name, help=f"Load {name} structure example"):
            handle_example_button(name)

def render_usage_guide():
    """Render the usage guide section"""
    with st.expander("ℹ️ Usage Guide"):
        st.markdown("""
        ### How to Use
        1. Either click one of the example buttons above or create your own structure
        2. Use the tree-command format with box drawing characters (├, │, └)
        3. Click "Preview" to see how it looks
        4. Click "Generate Commands" to get the shell commands
        
        ### Input Format Example
        ```
        my_project/
        ├── src/
        │   ├── main.py    # Main file
        │   └── utils.py   # Utilities
        └── tests/
            └── test_main.py
        ```
        
        ### Box Drawing Characters
        Copy and paste these characters: `├ │ └ ─`
        
        Or use keyboard shortcuts:
        - Windows: Alt + 195, Alt + 179, Alt + 192
        - Mac: Option + shift + L, Option + shift + B, Option + shift + M
        
        ### Tips
        - Add trailing slash (/) for directories
        - Add optional comments after #
        - Keep consistent indentation
        - Avoid special characters in names
        """)

def handle_preview(tree_input: str, include_comments: bool):
    """Handle preview button click"""
    try:
        if tree_input:
            tree_output = generate_tree_representation(
                tree_input,
                include_comments=include_comments
            )
            st.subheader("Preview")
            st.code(tree_output, language="")
        else:
            st.warning("Please enter a directory structure or use an example")
    except Exception as e:
        st.error(f"Error generating preview: {str(e)}")

def handle_generate_commands(tree_input: str):
    """Handle generate commands button click"""
    try:
        if tree_input:
            commands = generate_directory_commands(tree_input)
            
            if commands:
                st.subheader("Generated Commands")
                commands_text = "\n".join(commands)
                st.code(commands_text, language="bash")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📥 Download Shell Script",
                        commands_text,
                        file_name="create_structure.sh",
                        mime="text/plain"
                    )
                with col2:
                    st.button(
                        "📋 Copy to Clipboard",
                        help="Click to copy commands",
                        on_click=lambda: st.write(
                            f'<script>navigator.clipboard.writeText(`{commands_text}`)</script>',
                            unsafe_allow_html=True
                        )
                    )
            else:
                st.warning("No valid structure found in input")
        else:
            st.warning("Please enter a directory structure or use an example")
                
    except SafetyViolation as e:
        st.error(f"Safety check failed: {str(e)}")
    except Exception as e:
        st.error(f"Error generating commands: {str(e)}")

def main():
    # Initialize session state
    if "tree_input_value" not in st.session_state:
        st.session_state["tree_input_value"] = ""

    # Render main interface
    st.title("Directory Tree Generator 🌳")
    st.markdown("""
    Create directory structures using a tree-like format. Use the example buttons below to see different project structures,
    or create your own using the box drawing characters (├, │, └).
    """)

    # Render components
    settings = render_sidebar()
    render_example_buttons()

    # Text area for input
    st.markdown("### Directory Structure:")
    tree_input = st.text_area(
        label="",
        value=st.session_state["tree_input_value"],
        height=300,
        help="Enter your directory structure using tree-command format with ├, │, └ characters",
        key="tree_input_area"
    )

    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👀 Preview Structure", type="secondary"):
            handle_preview(tree_input, settings["include_comments"])
    
    with col2:
        if st.button("⚡ Generate Commands", type="primary"):
            handle_generate_commands(tree_input)

    # Usage guide
    render_usage_guide()

if __name__ == "__main__":
    main()