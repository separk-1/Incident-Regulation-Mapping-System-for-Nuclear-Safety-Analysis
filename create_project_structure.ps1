$paths = @(
    ".github/workflows",
    "data/raw/ler",
    "data/raw/regulations",
    "data/processed",
    "data/knowledge_graph",
    "docs/api",
    "docs/guides",
    "notebooks",
    "src/data",
    "src/preprocessing",
    "src/knowledge_graph",
    "src/visualization",
    "tests"
)

$files = @(
    ".github/workflows/tests.yml",
    "src/data/__init__.py",
    "src/data/ler_crawler.py",
    "src/data/regulation_crawler.py",
    "src/preprocessing/__init__.py",
    "src/preprocessing/text_cleaner.py",
    "src/preprocessing/entity_extractor.py",
    "src/knowledge_graph/__init__.py",
    "src/knowledge_graph/graph_builder.py",
    "src/knowledge_graph/relationship_extractor.py",
    "src/visualization/__init__.py",
    "src/visualization/graph_visualizer.py",
    "tests/__init__.py",
    "tests/test_crawlers.py",
    "tests/test_preprocessing.py",
    ".gitignore",
    "LICENSE",
    "requirements.txt",
    "setup.py",
    "notebooks/01_data_exploration.ipynb",
    "notebooks/02_text_preprocessing.ipynb",
    "notebooks/03_relationship_analysis.ipynb"
)

# create all path
foreach ($path in $paths) {
    New-Item -ItemType Directory -Path $path -Force
}

# create all files
foreach ($file in $files) {
    New-Item -ItemType File -Path $file -Force
}

# .gitignore 
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Jupyter Notebook
.ipynb_checkpoints

# Project specific
data/raw/*
data/processed/*
data/knowledge_graph/*
!data/raw/.gitkeep
!data/processed/.gitkeep
!data/knowledge_graph/.gitkeep

# Logs
*.log

# Environment variables
.env
"@

# requirements.txt 
$requirementsContent = @"
pandas==2.0.0
numpy==1.24.3
requests==2.31.0
beautifulsoup4==4.12.0
spacy==3.7.2
py2neo==2021.2.3
python-dotenv==1.0.0
pyyaml==6.0.1
pytest==7.4.3
jupyter==1.0.0
"@

Set-Content -Path ".gitignore" -Value $gitignoreContent
Set-Content -Path "requirements.txt" -Value $requirementsContent

# .gitkeep 
New-Item -ItemType File -Path "data/raw/.gitkeep" -Force
New-Item -ItemType File -Path "data/processed/.gitkeep" -Force
New-Item -ItemType File -Path "data/knowledge_graph/.gitkeep" -Force

Write-Host "Project structure created successfully in current directory!"