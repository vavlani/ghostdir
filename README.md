# ghostdir

Converts markdown-formatted directory structures into shell commands.

## Usage

Input:
```markdown
project/
  src/
    - main.py
  docs/
    - README.md
```

Output:
```bash
mkdir -p project
mkdir -p project/src
touch project/src/main.py
mkdir -p project/docs
touch project/docs/README.md
```

## Setup

```bash
# Install
poetry install

# Run
poetry run streamlit run app.py

# Test
poetry run pytest
```

## Limits

- Max 100 files/directories
- Max depth: 10 levels
- Allowed characters: `A-Z`, `a-z`, `0-9`, `_`, `-`, `.`, `/`
- No absolute paths
- No path traversal
- No spaces in paths

## Input Format

- Use 2-space indentation or markdown bullets (-)
- Add trailing slash (/) for directories
- Files don't need trailing slash