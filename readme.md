# Knowledge Graph-based Incident-Regulation Mapping System 🏠

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview
This project develops an automated system for mapping nuclear power plant incidents to relevant regulations using knowledge graph and large language models(LLMs).

## 🔊 Project Structure
```
├── .github/
│   └── workflows/
│       └── tests.yml
├── data/
│   ├── raw/               # Original data from sources
│   │   ├── ler/           # Licensee Event Reports
│   │   └── cfr/           # NRC regulations
│   ├── processed/         # Cleaned and processed data
│       ├── bin/
│       ├── ler_filtered/
│       ├── ler_text/
│       └── files (e.g., cfr.csv, ler_df.csv)
│   └── knowledge_graph/   # Generated knowledge graph data
├── src/
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── 1_ler_to_text.py
│   │   ├── 2_text_to_df.py
│   │   ├── 3_df_cleaner.py
│   │   ├── 4_ler_to_cfr.py
│   │   ├── 5_cfr_data.py
│   │   └── 6_extract_entity.py
│   ├── knowledge_graph/
│   │   ├── __init__.py
│   │   └── 7_knowledge_graph.py
│   └── run/
│       ├── __init__.py
│       └── main.py
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── setup.py
```

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/separk-1/Incident-Regulation-Mapping-System-for-Nuclear-Safety-Analysis.git
cd Incident-Regulation-Mapping-System-for-Nuclear-Safety-Analysis
```

### 2. Create and activate conda environment
```bash
conda create -n kg-irm python=3.10
conda activate kg-irm
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## ⚙️ Configuration

### 1. Create a .env file in the project root:
```env
LER_API_KEY=your_api_key
```

## 📗 Usage

### 1. Data Extraction: Process Licensee Event Reports (LERs)
To process all LER PDFs and map their content to relevant fields (e.g., Facility Name, Title, LER Number, Event Date, Abstract, Narrative, and CFR), use the `1_ler_to_text.py` script:

```bash
python src/preprocessing/1_ler_to_text.py
```

#### Input:
- Place all LER PDF files in the `data/raw/ler/` directory.

#### Output:
- The processed data will be saved as text files in `data/processed/ler_text/`.

### 2. Data Cleaning and Transformation
Run scripts to clean text data and extract required fields:
```bash
python src/preprocessing/2_text_to_df.py
python src/preprocessing/3_df_cleaner.py
```

### 3. CFR Matching
Match processed LER data to CFR regulations:
```bash
python src/preprocessing/4_ler_to_cfr.py
python src/preprocessing/5_cfr_data.py
```

### 4. Knowledge Graph Construction
Build the knowledge graph from processed data:
```bash
python src/knowledge_graph/6_extract_entity.py
```
#### Input:
- CSV files generated from the previous step.

#### Output:
- The script creates and visualizes a knowledge graph (using NetworkX) and saves it as a `.pkl` file.

### 5. Retrieval and Inference
Use `main.py` to input new data, retrieve the closest CFR matches, and identify similar incidents:
```bash
python src/run/main.py
```

## 🛠️ Dependencies

Main dependencies include:
- Python 3.10
- SpaCy
- Pandas
- pdfplumber
- NetworkX

## ✅ License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

