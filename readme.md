# Knowledge Graph-based Incident-Regulation Mapping System 🏭

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-4.4+-green.svg)](https://neo4j.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview
This project develops an automated system for mapping nuclear power plant incidents to relevant regulations using knowledge graph technology. The system aims to bridge the gap between explicit knowledge (regulations) and empirical knowledge (incident cases) in nuclear safety analysis.

## 🗂️ Project Structure
```
├── .github/
│   └── workflows/
│       └── tests.yml
├── data/
│   ├── raw/               # Original data from sources
│   │   ├── ler/           # Licensee Event Reports
│   │   └── regulations/   # NRC regulations
│   ├── processed/         # Cleaned and processed data
│   └── knowledge_graph/   # Generated knowledge graph data
├── docs/
│   ├── api/              # API documentation
│   └── guides/           # Usage guides and tutorials
├── notebooks/            # Jupyter notebooks for analysis
│   ├── 01_data_exploration.ipynb
│   ├── 02_text_preprocessing.ipynb
│   └── 03_relationship_analysis.ipynb
├── src/
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── text_cleaner.py
│   │   └── entity_extractor.py
│   ├── knowledge_graph/
│   │   ├── __init__.py
│   │   ├── graph_builder.py
│   │   └── relationship_extractor.py
│   └── visualization/
│       ├── __init__.py
│       └── graph_visualizer.py
├── tests/
│   ├── __init__.py
│   └── test_preprocessing.py
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── setup.py
```

## 🚀 Installation

1. Clone the repository
```bash
git clone https://github.com/separk-1/Knowledge-Graph-based-Incident-Regulation-Mapping-System-for-Nuclear-Safety-Analysis.git
cd Knowledge-Graph-based-Incident-Regulation-Mapping-System-for-Nuclear-Safety-Analysis
```

2. Create and activate conda environment
```bash
conda create -n kg-irm python=3.10
conda activate kg-irm
```

3. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

4. Install Neo4j Community Edition
- Download from [Neo4j Download Center](https://neo4j.com/download/)
- Follow installation instructions for your operating system

## ⚙️ Configuration

1. Create a `.env` file in the project root:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
LER_API_KEY=your_api_key
```

2. Configure logging in `src/config/logging.yaml`

## 📚 Usage

1. Data Collection
LER: https://lersearch.inl.gov/LERSearchCriteria.aspx
Guideline: https://www.nrc.gov/reading-rm/doc-collections/cfr/index.html


2. Data Preprocessing
```bash
python src/preprocessing/text_cleaner.py
python src/preprocessing/entity_extractor.py
```

3. Knowledge Graph Construction
```bash
python src/knowledge_graph/graph_builder.py
```

## 📅 Project Timeline

### Week 1: Data Collection
- ✅ Set up project structure
- 🔄 Implement web crawlers
- 🔄 Collect initial dataset

### Week 2: Data Preprocessing
- Text cleaning
- Entity extraction
- Basic relationship definition

### Weeks 3-4: Knowledge Graph Development
- Graph database setup
- Entity classification
- Relationship mapping

### Weeks 5-6: Analysis and Validation
- Pattern analysis
- Accuracy validation
- Documentation

## 🛠️ Dependencies

Main dependencies include:
- Python 3.10
- Neo4j 4.4+
- pandas 2.0.0
- requests 2.31.0
- beautifulsoup4 4.12.0
- spacy 3.7.2
- py2neo 2021.2.3
- numpy 1.24.3

## 📞 Contact
Project maintainer: [Seongeun Park](mailto:seongeup@andrew.cmu.edu)

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.