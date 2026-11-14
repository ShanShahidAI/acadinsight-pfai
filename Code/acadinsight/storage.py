"""CSV persistence with validation, atomic rewrites and simple CRUD operations."""
import csv
import os
import tempfile
import uuid
from threading import RLock
from .config import DATA

SCHEMA = {
    'students': ['id','name','program','section'],
    'subjects': ['id','student_id','code','name','credits'],
    'assessments': ['id','subject_id','component','obtained','max_marks','weight'],
    'attendance': ['id','subject_id','attended','held'],
    'previous_semesters': ['id','student_id','title','credits','gpa']
}
_LOCK = RLock()

def _check(table):
    if table not in SCHEMA: raise ValueError('Unknown table')
    DATA.mkdir(parents=True, exist_ok=True)
    path = DATA / (table + '.csv')
    if not path.exists():
        with path.open('w', newline='', encoding='utf-8') as f:
            csv.DictWriter(f, SCHEMA[table]).writeheader()
    return path

def all_rows(table):
    with _LOCK:
        with _check(table).open(newline='', encoding='utf-8-sig') as f:
            return list(csv.DictReader(f))

def save_all(table, rows):
    with _LOCK:
        path = _check(table)
        fd, temp = tempfile.mkstemp(suffix='.csv', prefix='_saving_', dir=DATA)
        try:
            with os.fdopen(fd,'w',newline='',encoding='utf-8') as f:
                writer=csv.DictWriter(f, fieldnames=SCHEMA[table], extrasaction='ignore')
                writer.writeheader()
                writer.writerows(rows)
            os.replace(temp, path)
        finally:
            if os.path.exists(temp): os.remove(temp)

def new_id(prefix):
    return f'{prefix}-{uuid.uuid4().hex[:8].upper()}'

def find(table, row_id):
    return next((r for r in all_rows(table) if r['id']==row_id), None)

def create(table, row):
    with _LOCK:
        rows=all_rows(table)
        if any(r['id']==row['id'] for r in rows): raise ValueError('ID already exists')
        rows.append(row)
        save_all(table, rows)
    return row

def upsert(table, row, match='id'):
    with _LOCK:
        rows=all_rows(table)
        for i, old in enumerate(rows):
            if old[match]==row[match]:
                rows[i] = row
                save_all(table,rows)
                return row
        rows.append(row)
        save_all(table,rows)
    return row

def remove(table,row_id):
    with _LOCK:
        rows=all_rows(table)
        updated=[r for r in rows if r['id']!=row_id]
        if len(updated)==len(rows): raise ValueError('Record not found')
        save_all(table,updated)

def delete_subject(subject_id):
    with _LOCK:
        if not find('subjects',subject_id): raise ValueError('Subject not found')
        for t in ('assessments','attendance'):
            save_all(t,[r for r in all_rows(t) if r['subject_id']!=subject_id])
        remove('subjects',subject_id)
