# Khmer Question Answering for Cambodian Education Policy

Group 01 · Advanced Programming for Data Science

The project answers Khmer questions about Cambodian education policies and strategic plans. Each answer should cite the document and PDF page that support it. When the retrieved passages provide insufficient evidence, the system should say so in Khmer.

See the [project proposal](Group01_proposal.pdf) for the full scope. The [source list](data/sources.json) and [dataset builder](src/prepare.py) are already in the project. Steps 4–8 describe the implementation work that follows dataset preparation.

## Project structure

```text
project/
├── README.md
├── Group01_proposal.pdf
├── data/
│   ├── sources.json                        # Document IDs, titles, and source links
│   ├── pdfs/                               # Downloaded Khmer policy PDFs
│   └── processed/
│       ├── education-strategic-plan.jsonl   # Generated pilot passages
│       └── passages.jsonl                  # Generated passages from all sources
├── src/
│   ├── prepare.py                          # Extract passages and record PDF pages
│   ├── retrieve.py                         # Embed, search, fuse, and rerank passages
│   └── answer.py                           # Generate Khmer answers and resolve citations
├── evaluation/
│   ├── questions.jsonl                     # Questions, reference answers, and evidence
│   ├── run.py                              # Compare retrieval and answer configurations
│   └── results/                             # Metrics and reviewed answers
└── app.py                                  # Streamlit demo
```

The README, proposal, source list, and `src/prepare.py` are already present. Create `data/pdfs/` for the downloads. The dataset builder creates `data/processed/` when it writes its output. Add the evaluation files, retrieval and answer modules, and demo as you reach those steps below.

## Inputs and outputs

| Stage | Input | Output |
| --- | --- | --- |
| Dataset preparation | Khmer policy PDFs and their source records | UTF-8 JSONL with one candidate passage per line and its document and page metadata |
| Retrieval | A Khmer question and the indexed passages | Ranked passages with their source metadata |
| Answer generation | The question and the top-ranked passages | A Khmer answer with citations, or an insufficient-evidence message |
| Evaluation | Khmer questions with verified answers and excerpts, plus unanswerable questions | Retrieval and answer-quality scores for each configuration |

## 1. Set up Python

Open the project folder in VS Code and run these commands in its PowerShell terminal. Install Python first if `python --version` fails. If your Windows installation uses the Python launcher, use `py -m venv .venv` to create the environment.

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pymupdf
New-Item -ItemType Directory -Force data\pdfs
```

## 2. Download the first Khmer PDF

Open the Khmer resource, click **Download**, and save it in `data\pdfs` with the exact filename shown.

| Source | Filename |
| --- | --- |
| [Education Strategic Plan 2024–2028](https://data.opendevelopmentcambodia.net/library_record/education-strategic-plan-2024-2028/resource/233203a2-58ca-433f-9d37-2e0a2d0c1dfa) | `education-strategic-plan.pdf` |
| [Teacher Policy Action Plan 2024–2030](https://data.opendevelopmentcambodia.net/en/laws_record/teacher-policy-action-plan-2024-2030/resource/75d0ddbe-3b1b-406f-9577-51abc30cdd50) | `teacher-policy-action-plan.pdf` |
| [Action Plan on Inclusive Education 2024–2028](https://data.opendevelopmentcambodia.net/library_record/action-plan-on-inclusive-education-2024-2028/resource/11eabefa-df05-405b-a62d-e9d842b8bc58) | `inclusive-education-action-plan.pdf` |

Start with the Education Strategic Plan. Open it and try copying a Khmer paragraph into VS Code. If the copied text is unreadable, try another listed PDF with selectable Khmer text. Scanned pages may need OCR.

## 3. Generate and review the pilot dataset

```powershell
.\.venv\Scripts\python.exe src\prepare.py --source education-strategic-plan
```

Open `data/processed/education-strategic-plan.jsonl`. Each record has `passage_id`, `document_id`, `document_title`, `source_url`, `pdf_page`, and `text`. The page number starts at 1 and follows the PDF viewer's page position. It can differ from the number printed on the page.

The script normalizes Unicode and whitespace and keeps text blocks with at least 30 Khmer letters. Compare several output passages with their cited pages. Look for broken Khmer characters, incorrect reading order, repeated headers, and split tables. Treat the printed total as a count of candidate passages.

When the pilot looks usable, download the other two PDFs and run:

```powershell
.\.venv\Scripts\python.exe src\prepare.py
```

This writes `data/processed/passages.jsonl`. If a PDF is missing, check the filename against the table. If the script finds no usable text, check the PDF's text layer. To add another policy document, give it a unique ID in `data/sources.json` and save the PDF as `data/pdfs/<id>.pdf`. Expand toward 2,000 usable passages after reviewing extraction quality.

## 4. Write five pilot questions

Create `evaluation/questions.jsonl`. Write four questions in Khmer that the pilot PDF can answer and one that it cannot. For each record, save a question ID, the question, whether it is answerable, and, where applicable, the reference answer, document ID, PDF page, and exact supporting excerpt. Page and excerpt labels let you reuse the same questions when you change how passages are split.

## 5. Build vector search and generate the first answer

1. Create `src/retrieve.py`. Embed the passage text and each question with BGE-M3. Use cosine similarity to return the top five passages with their IDs and metadata. NumPy is enough for the pilot.
2. Print the results for the four answerable questions. Check whether each verified excerpt appears among the retrieved passages.
3. Create `src/answer.py`. Send the question and retrieved passages to one multilingual LLM. Label each passage by ID. Ask for a Khmer answer grounded in those passages and instruct the model to say when the evidence is insufficient.
4. Resolve cited IDs against the retrieved passages. Display the document title, source link, PDF page, and supporting excerpt. Reject citation IDs outside the retrieved set.
5. Run the five pilot questions. Verify the cited pages directly and check that the unanswerable question produces an insufficient-evidence response.

## 6. Add hybrid retrieval

1. Store the vectors and passage IDs in Milvus.
2. Apply the same Khmer word segmentation to passages and queries. Index the segmented text in PostgreSQL and return ranked passage IDs from keyword search.
3. Combine the vector and keyword rankings with Reciprocal Rank Fusion using the shared passage IDs.
4. Run the BGE reranker on the strongest candidates. Record results before and after reranking so you can measure its effect.

## 7. Run the final evaluation

Compare paragraph-based and fixed-length character chunking using the same labeled excerpts. Keep chunks tied to their original PDF pages. Use a held-out set of questions to compare LLM-only, vector RAG, and hybrid RAG with the same LLM. Report Hit@5, Recall@5, MRR, and nDCG@5 for retrieval configurations. Review answer correctness, faithfulness to the evidence, citation accuracy, unsupported claims, and abstention on unanswerable questions.

## 8. Build the demo

Create a simple Streamlit page with a Khmer question box, a Khmer answer, and an expandable list of cited passages. A reviewer should be able to ask a question, open the cited PDF, and find the supporting excerpt. Show an insufficient-evidence message when appropriate.

**First milestone:** Run the dataset builder on one PDF, verify several passages, and write five pilot questions. Use those five questions to test the pipeline before setting up Milvus, PostgreSQL, or the demo.
