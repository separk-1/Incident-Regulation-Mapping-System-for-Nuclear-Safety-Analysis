# Knowledge Graph-based Incident-Regulation Mapping System

## Overview
This project develops an automated system for mapping nuclear power plant incidents to relevant regulations using knowledge graph technology. The system aims to bridge the gap between explicit knowledge (regulations) and empirical knowledge (incident cases) in nuclear safety analysis.

## Project Structure
```
nuclear-safety-kg/
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
│   ├── data/
│   │   ├── __init__.py
│   │   ├── ler_crawler.py
│   │   └── regulation_crawler.py
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
│   ├── test_crawlers.py
│   └── test_preprocessing.py
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── setup.py
```

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/nuclear-safety-kg.git
cd nuclear-safety-kg
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Install Neo4j Community Edition
- Download from [Neo4j Download Center](https://neo4j.com/download/)
- Follow installation instructions for your operating system

## Configuration

1. Create a `.env` file in the project root:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
LER_API_KEY=your_api_key
```

2. Configure logging in `src/config/logging.yaml`

## Usage

1. Data Collection
```bash
python src/data/ler_crawler.py
python src/data/regulation_crawler.py
```

2. Data Preprocessing
```bash
python src/preprocessing/text_cleaner.py
python src/preprocessing/entity_extractor.py
```

3. Knowledge Graph Construction
```bash
python src/knowledge_graph/graph_builder.py
```

## Project Timeline

### Week 1: Data Collection
- Set up project structure
- Implement web crawlers
- Collect initial dataset

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

## Dependencies

Main dependencies include:
- Python 3.8+
- Neo4j 4.4+
- pandas
- requests
- beautifulsoup4
- spacy
- py2neo
- numpy

## Contact
Project maintainer: [Seongeun Park](mailto:seongeup@andrew.cmu.edu)
