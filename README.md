# AcadInsight — Smart Student Performance Analyzer

**Programming for AI semester project (2026)**  
**BS Artificial Intelligence | AI/3-1 | Riphah International University**

AcadInsight is the full Python + HTML/CSS/JavaScript coursework project included in the supplied ZIP. The application supports academic record entry, assessment and attendance analysis, example GPA/CGPA calculations, local visualization and rule-based improvement guidance.

> **Academic prototype:** Demo data and grading policies are illustrative. Results are not official university records. Test and demo evidence in the archive is historical; this packaging process did not independently certify the application.

## Project structure

```text
Code/
  acadinsight/            # analysis, data models, charts, storage, demo config
  static/                 # HTML/CSS/JavaScript frontend
  data/                   # demonstrative sample records, configuration
  tests/                  # project test source
  app.py                  # local Python app/server entry point
  requirements.txt
  README.md               # detailed instructions and features
  TEST_RESULTS.md         # supplied test notes
Documents/
  AcadInsight_Project_Proposal.*
  AcadInsight_Final_Project_Report.*
  AcadInsight_Viva_and_Demo_Guide.*
Presentation/
  AcadInsight_PFAI_Presentation.pptx
README_START_HERE.txt
```

## Run locally

In a terminal:

```powershell
cd Code
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:8765` (as documented in the project's detailed README). The browser frontend requires the Python server; opening the HTML file directly is not sufficient.

## Documents

Read `Code/README.md` for instructions, data caveats and feature details; `Documents/` contains the supplied proposal, report and viva materials. No original project files were removed or rewritten in this packaging step.

**Status:** Original source and deliverables packaged; no new functional testing claimed.
