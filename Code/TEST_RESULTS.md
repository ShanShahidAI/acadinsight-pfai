# AcadInsight test results

**Tested:** 13 November 2026  
**Environment:** Local Python 3.13 with NumPy, Pandas, Matplotlib  
**Purpose:** Academic prototype QA; fictional student records only.

## Automated unit checks: 9 passed / 9 run

- Weighted subject percentage and demo grade selection — PASS
- Incomplete assessment totals excluded from final GPA — PASS
- Attendance shortage threshold and advice — PASS
- Zero classes held handled safely — PASS
- Invalid marks and assessment weights rejected — PASS
- Fictional ST-001 GPA = 3.58, attendance alerts = 1 — PASS
- Pandas summary and all three PNG Matplotlib charts — PASS
- API input validators reject bad student or subject links — PASS
- CSV record loading and example grade bands — PASS

Run the checks yourself:

```bash
python -m unittest discover -s tests -v
```

## End-to-end local HTTP API: PASS

With `python app.py` running, the following local requests were tested successfully:

1. Read example students.
2. Create a new fictional student and subject.
3. Add partial marks and verify that final grade is unavailable.
4. Complete assessment weight to 100% and verify subject percentage.
5. Update attendance and verify shortage alert.
6. Generate a chart as PNG and download students CSV.
7. Delete the test subject and verify linked records are removed.
8. Restore the original fictional demo dataset.

## Visual checks

The local dashboard HTML/CSS/JavaScript was rendered using actual CSV-derived JSON and Matplotlib-generated chart images in a headless-browser preview. The PowerPoint and Word/PDF outputs were also rendered and inspected. The application should still be demonstrated on the group's own laptop with their installed Python environment before submission.

## Not tested / outside scope

- Official Riphah University grade bands or assessment policies (not supplied in the source proposal).
- Multiuser security, public internet deployment, login/authorization, backup/disaster recovery.
- Machine Learning classification/prediction, accuracy or F1-score (not part of the core PFAI scope).
