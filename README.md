# Generate-doc-from-source
A Python tool that analyzes project folders to generate two files:
- `tree.txt`: A structured view of the project's directory layout
- `source.txt`: A consolidated file containing all project's source code

These files are formatted specifically for querying Large Language Models (LLMs) about your codebase, enabling code analysis, architecture understanding, and documentation generation.

## Requirements

- **Python 3.12.9** (or higher)
- **pip**

## Virtual Environment Setup
It is recommended to use a virtual environment to manage project dependencies.

### Creating the virtual environment
From the terminal, in the project root, run:

```bash
python -m venv generate-doc-env
```

### Activating the virtual environment
On Windows:

```bash
generate-doc-env\Scripts\activate
```

On macOS/Linux:

```bash
source generate-doc-env/bin/activate
```

### Installing Dependencies
With the virtual environment activated, install the dependencies:

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python .\src\source_tree_generator.py
```