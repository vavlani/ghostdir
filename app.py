import streamlit as st
from pathlib import Path
from generator import generate_directory_commands, generate_tree_representation, SafetyViolation

st.set_page_config(
    page_title="Directory Tree Generator",
    page_icon="🌳",
    initial_sidebar_state="expanded",
)

# Example tree structures
PYTHON_PROJECT_EXAMPLE = """python_package/
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
└── README.md             # Project documentation"""

ML_PROJECT_EXAMPLE = """ml_project/
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
└── requirements.txt      # Project dependencies"""

BACKEND_SERVICE_EXAMPLE = """backend_service/
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

def main():
    # Sidebar settings
    st.sidebar.header("Settings")
    base_dir = st.sidebar.text_input("Base Directory", ".")
    max_items = st.sidebar.number_input("Max Items", min_value=1, max_value=500, value=100)
    max_depth = st.sidebar.number_input("Max Depth", min_value=1, max_value=20, value=10)
    include_comments = st.sidebar.checkbox("Include Comments", value=True)

    # Main content
    st.title("Directory Tree Generator 🌳")
    st.markdown("""
    Create directory structures using a tree-like format. Use the example buttons below to see different project structures,
    or create your own using the box drawing characters (├, │, └).
    """)

    # Example buttons in columns
    st.subheader("📚 Load Example Structure")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        python_btn = st.button("Python Package", 
                              help="Basic Python package structure with tests and documentation")
    with col2:
        ml_btn = st.button("ML Project", 
                          help="Machine learning project with data, models, and notebooks")
    with col3:
        backend_btn = st.button("Backend Service", 
                               help="Python backend service with API and database")

    # Text area for input
    tree_input = st.text_area(
        "Directory Structure",
        height=300,
        help="Enter your directory structure using tree-command format with ├, │, └ characters",
        font="monospace"
    )

    # Update text area based on example buttons
    if python_btn:
        tree_input = PYTHON_PROJECT_EXAMPLE
    elif ml_btn:
        tree_input = ML_PROJECT_EXAMPLE
    elif backend_btn:
        tree_input = BACKEND_SERVICE_EXAMPLE

    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👀 Preview Structure", type="secondary"):
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

    with col2:
        if st.button("⚡ Generate Commands", type="primary"):
            try:
                if tree_input:
                    commands = generate_directory_commands(tree_input)
                    
                    if commands:
                        st.subheader("Generated Commands")
                        commands_text = "\n".join(commands)
                        st.code(commands_text, language="bash")
                        
                        col3, col4 = st.columns(2)
                        with col3:
                            st.download_button(
                                "📥 Download Shell Script",
                                commands_text,
                                file_name="create_structure.sh",
                                mime="text/plain"
                            )
                        with col4:
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

    # Help section
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

if __name__ == "__main__":
    main()