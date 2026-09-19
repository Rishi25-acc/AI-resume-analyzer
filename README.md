# AI Resume Analyzer and Job Recommendation System

An NLP-based Streamlit application that helps students understand how well their resume matches selected job roles. Upload a PDF or DOCX resume and the app extracts your skills, scores the resume against multiple job roles, recommends the best-fit roles, highlights missing skills, and generates a simple learning roadmap.

> **Note:** Match scores are estimates for guidance only. They are not recruiter decisions, and a missing keyword does not necessarily mean a missing ability.

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Usage](#usage)
- [Example Output](#example-output)
- [Datasets](#datasets)
- [Testing and Evaluation](#testing-and-evaluation)
- [Deployment](#deployment)
- [Responsible AI](#responsible-ai)
- [Limitations](#limitations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- Upload a **PDF or DOCX** resume (file type and size are validated)
- Extract and clean resume text
- Detect **20–30+ job-related skills**, grouped by category (programming, databases, ML, cloud, tools)
- Compare the resume against **5+ job roles** using TF-IDF and cosine similarity
- Calculate a resume-to-role **match score**
- Recommend the **top three** suitable roles
- Identify **missing skills** for a selected target role
- Generate a basic **learning roadmap**
- Interactive **Streamlit dashboard** with a match-score chart
- Downloadable analysis report

## How It Works

```
Upload PDF or DOCX resume
        |
Extract resume text
        |
Clean and normalize the text
        |
Identify skills, education, projects, and experience
        |
Load job-role requirements
        |
Compare resume with each job role
        |
Calculate match scores
        |
Recommend roles
        |
Show missing skills and learning roadmap
```

**Matching approach (beginner):** keyword matching for skill extraction, TF-IDF vectors for the resume and job descriptions, cosine similarity for match scores, and a rule-based learning roadmap.

## Tech Stack

| Project Part | Tool |
|---|---|
| Language | Python |
| PDF extraction | `pypdf` |
| DOCX extraction | `python-docx` |
| Text cleaning | Python and regular expressions |
| NLP processing | spaCy or simple keyword matching |
| Matching | TF-IDF and cosine similarity (`scikit-learn`) |
| Data handling | Pandas and NumPy |
| Charts | Plotly or Matplotlib |
| User interface | Streamlit |
| Version control | Git and GitHub |

Optional / advanced: Sentence Transformers (semantic matching), Groq / Gemini / OpenAI or a local model (AI feedback), FastAPI (backend), SQLite or PostgreSQL (database), Docker.

## Project Structure

```
ai_resume_analyzer/
|-- app.py                  # Streamlit dashboard (entry point)
|-- resume_parser.py        # PDF / DOCX text extraction
|-- text_cleaner.py         # Text cleaning and normalization
|-- skill_extractor.py      # Skill detection and categorization
|-- job_matcher.py          # TF-IDF + cosine similarity, role ranking
|-- roadmap_generator.py    # Skill-gap analysis and learning roadmap
|-- requirements.txt
|-- README.md
|-- .env                    # API keys (optional, never commit)
|-- .gitignore
|
|-- data/
|   |-- job_roles.csv           # Job roles and required skills
|   |-- skill_dictionary.csv    # Controlled list of skills by category
|
|-- sample_resumes/         # Sample resumes (personal info removed)
|-- reports/                # Generated analysis reports
|
|-- tests/
    |-- test_cases.csv      # Evaluation sheet
```

## Setup

### Prerequisites

- Python 3.9 or higher
- `pip`
- Git

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/ai_resume_analyzer.git
cd ai_resume_analyzer
```

### 2. Create and activate a virtual environment

```bash
# macOS / Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

A typical `requirements.txt` for this project:

```
streamlit
pypdf
python-docx
pandas
numpy
scikit-learn
plotly
matplotlib
python-dotenv
# Optional
spacy
sentence-transformers
```

If you use spaCy, also download a language model:

```bash
python -m spacy download en_core_web_sm
```

### 4. (Optional) Configure environment variables

Only needed if you enable optional AI feedback (Groq, Gemini, OpenAI). Create a `.env` file in the project root:

```
GROQ_API_KEY=your_key_here
```

Make sure `.env` is listed in `.gitignore`.

## Usage

### Run the app

```bash
streamlit run app.py
```

Streamlit will open the app in your browser, usually at `http://localhost:8501`.

### Using the dashboard

1. **Upload your resume** as a PDF or DOCX file.
2. **Select a target role** from the dropdown (e.g. Machine Learning Engineer).
3. Review the **extracted skills**, grouped by category.
4. View the **match-score chart** comparing your resume to every job role.
5. Check the **top three recommended roles**.
6. Read the **missing skills** and the **suggested learning roadmap** for your target role.
7. **Download** the analysis report.

Uploaded resumes are processed for the current session only. Temporary files are deleted after processing, and resumes are not stored permanently unless you give permission.

## Example Output

```
Target Role: Machine Learning Engineer
Resume Match Score: 74%

Skills Found:
- Python
- Pandas
- Machine Learning
- scikit-learn
- SQL

Missing Skills:
- FastAPI
- Docker
- MLflow
- Cloud deployment

Recommended Roles:
1. Data Analyst - 86%
2. Junior ML Engineer - 74%
3. Python Developer - 69%

Suggested Roadmap:
Week 1: FastAPI basics
Week 2: Deploy an ML model
Week 3: Docker fundamentals
Week 4: MLflow and cloud deployment
```

## Datasets

### `data/job_roles.csv`

A small, manually verified list of job roles and their expected skills. Starting roles:

| Job Role | Example Required Skills |
|---|---|
| Data Analyst | Python, SQL, Excel, Pandas, Power BI |
| Machine Learning Engineer | Python, ML, scikit-learn, FastAPI, Docker |
| AI Engineer | Python, deep learning, LLM, RAG, APIs |
| NLP Engineer | Python, NLP, transformers, Hugging Face |
| Computer Vision Engineer | Python, OpenCV, CNN, YOLO |

To add a new role, append a row to `job_roles.csv` with the role name and its required skills.

### `data/skill_dictionary.csv`

The controlled list of skills the extractor searches for, grouped into categories such as programming, databases, ML, cloud, and tools. Technical symbols like `C++`, `C#`, and `.NET` are preserved during text cleaning so they can be matched correctly.

## Testing and Evaluation

Test the app with different resume styles and target roles, and record results in `tests/test_cases.csv`.

| Test Resume | Expected Top Role | Actual Top Role | Comments |
|---|---|---|---|
| Resume A | Data Analyst | | |
| Resume B | ML Engineer | | |
| Resume C | NLP Engineer | | |

Evaluation checklist:

- **Extraction quality:** is resume text extracted correctly?
- **Skill precision:** are the listed skills actually present?
- **Skill recall:** are important skills missed?
- **Role ranking:** are the top recommendations reasonable?
- **Score consistency:** does the score change logically when skills are added or removed?
- **Fairness:** does the system ignore protected personal information?
- **Usability:** can a student understand the result easily?

## Deployment

The app can be deployed on **Streamlit Community Cloud**, **Render**, or **Docker**.

**Streamlit Community Cloud**

1. Push the project to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app from your repository.
3. Set the main file to `app.py`.
4. Add any secrets (such as API keys) in the app's Secrets settings instead of committing `.env`.

## Responsible AI

- Use the tool for **guidance**, not automatic hiring or rejection.
- Gender, age, religion, nationality, photograph, marital status, and disability are **not scored**.
- Only job-related skills, education, projects, and relevant experience are evaluated.
- Match scores are estimates, not recruiter decisions.
- Uploaded resumes are protected and temporary files are deleted after processing.
- Missing keywords do not always mean missing ability.

## Limitations

- Keyword matching can miss relevant skills written in different words (for example "ML" vs "machine learning") or implied by projects.
- TF-IDF measures word overlap, not deep meaning. Sentence Transformers can improve semantic matching.
- Results depend on the quality of the skill dictionary and job-role dataset.
- Scanned or image-only PDFs may not yield extractable text.

## Roadmap

Optional advanced features:

- Resume section detection (education, skills, projects, experience)
- Job-description upload instead of only predefined roles
- Resume improvement suggestions
- Downloadable PDF analysis report
- User login and saved reports
- Job-role dashboard with charts
- FastAPI backend and Docker deployment
- Sentence Transformers for semantic matching
- LLM-generated resume feedback using a controlled prompt
- Feedback-based improvement of the skill dictionary

## Contributing

Contributions are welcome. Fork the repository, create a feature branch, and open a pull request. Please keep sample resumes free of personal information.

## License

Add your license here (for example, MIT).
