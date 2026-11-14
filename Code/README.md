# AcadInsight — Smart Student Performance Analyzer

**Programming for AI (PFAI) | BS Artificial Intelligence, Semester 3 | AI/3-1**  
**Submitted to:** Musharraf | **University:** Riphah International University

A free, locally running Python application to record students, subjects, assessment marks and attendance; calculate GPA/CGPA; visualize performance with Matplotlib; and generate rule-based study suggestions. It follows the uploaded project proposal. No internet connection, paid service, ML model or external database is needed for the application.

> **Academic integrity and grading warning:** The shipped grading scale, assessment weights, fictional students and attendance threshold are DEMO examples, not confirmed institutional rules or real student data. Update the policy through **Grading Settings** and enter approved assessment weights before presenting any official GPA/CGPA as valid. The app is for educational analysis, not an official academic record system.

## 1. Install once

Install **Python 3.10+** and open the `Code` folder in VS Code.

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If activation is blocked, run directly with `.venv\Scripts\python.exe app.py` or use a Command Prompt. macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`.

Libraries: `numpy`, `pandas`, `matplotlib`. The website server uses Python's built-in `http.server` — **Flask is not needed**.

## 2. Run website

```powershell
python app.py
```

Open **http://127.0.0.1:8765** in Chrome/Edge. Stop by pressing `Ctrl+C` in the terminal. Do not double-click `index.html`; the Python server is necessary.

## 3. Demo workflow (5–7 minutes)

1. **Overview:** select “Ayesha Khan (Demo)” and explain sample academic metrics and charts.
2. **Students & Subjects:** create a new fictional student, then select them and add a subject.
3. **Assessment Marks:** enter each component (quiz, assignment, midterm, final). Set the maximum marks and a weight; weights must total **100%** before a final grade is calculated.
4. **Attendance:** enter attended and held classes and observe configurable shortage alerts.
5. **GPA / CGPA:** enter prior semesters' GPA and graded credit hours to calculate an indicative CGPA.
6. **Visual Reports:** show three local Matplotlib charts and export CSV files.
7. **Grading Settings:** explain that demo thresholds and grade bands are editable, not official.

## 4. Folder structure

```text
Code/
  app.py                         # Local JSON API + website server
  acadinsight/
    models.py                    # OOP dataclasses: Student, Subject, Assessment, ...
    storage.py                   # CSV create/read/update/save and validation
    analytics.py                 # NumPy, Pandas, GPA, CGPA, attendance, insights
    charts.py                    # Matplotlib PNG graphs
    config.py                    # Editable demonstration grade bands
    demo_data.py                 # Fictional reproducible records
  static/
    index.html                   # Seven interactive website sections
    app.css                      # Responsive offline visual design
    app.js                       # Forms, requests and live page rendering
  data/                          # CSV records + settings.json
  tests/test_core.py             # Automated functional tests
  requirements.txt
  README.md
```

## 5. Formula examples

- **Assessment contribution** = `(obtained / maximum) × weight`. Example: 18/20 at 20% weight contributes 18 points.
- **Final subject percentage** = sum of contributions when weights total 100%.
- **Semester GPA** = `Σ (grade_point × subject_credit_hours) / Σ subject_credit_hours` for **fully graded subjects only**.
- **Estimated CGPA** = `(Σ previous_GPA × previous_credits + current_grade_points) / (Σ previous_credits + currently graded credits)`.
- **Attendance** = `attended / held × 100`. Zero held classes = not yet available, not zero percent.

Previous semester entries should use credits included in that semester GPA, not double count transferred credits. Grades are rounded for display only after the weighted calculations.

## 6. Team responsibilities (from original proposal)

| Team member | SAP | Primary responsibilities |
|---|---|---|
| Muhammad Salman | 72373 | Student/subject records, OOP, marks, GPA/CGPA logic |
| Shan | 72387 | NumPy/Pandas processing, statistics, Matplotlib reports |
| Shaheryar Khan | 72775 | User interaction, recommendations, integration, testing |

These are the **planned roles** stated in the proposal; the generated code and documentation do not verify who personally authored each file. All three students should understand the whole workflow before the viva.

## 7. Tests

```powershell
python -m unittest discover -s tests -v
```

The tests check weighted assessment calculations, incomplete marks handling, GPA example values, input errors, attendance thresholds, and rendered chart bytes. The demo data is fictional and reproducible. To reset via code: `python -m acadinsight.demo_data` (this **overwrites** CSV records). In the website, Settings → Reset demo does the same after confirmation. **Export CSV files first** if you have edits to preserve.

## 8. Important limitations

- Not a trained Machine Learning model: recommendations are human-readable **IF–THEN style rules**, as the proposal describes. Future ML prediction is optional, NOT implemented.
- Grade scale, grade letters, attendance policy, and assessment weights are examples; actual approved policy must be supplied by the instructor.
- Website binds to localhost `127.0.0.1` only and is not multiuser production software. No login/authentication, backup service or encryption.
- CSV changes persist locally; one user at a time is recommended.
- Incomplete subjects are excluded from semester GPA, and CGPA estimates based on incomplete semesters must not be called official.
- Accuracy/precision/F1-score are **not** applicable because the core application performs deterministic calculations rather than supervised learning.

## 9. Common problems

- `ModuleNotFoundError`: ensure you installed using the same Python environment as you use to run `app.py`.
- Port already in use: close the other AcadInsight terminal or change `PORT=8765` in `app.py`.
- A graph is blank: enter assessments/attendance for the selected student. Final grade graphs need weights totaling 100%.
- GPA shows “—”: there are no fully graded subjects. Complete the assessment weight and marks.

**Local web address:** http://127.0.0.1:8765
