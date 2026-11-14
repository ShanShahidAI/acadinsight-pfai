"""Configurable, DEMONSTRATION grading policy. NOT an official university policy."""
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / 'data'
SETTINGS = DATA / 'settings.json'
DEFAULT = {
    'attendance_threshold': 75.0,
    'grade_scale': [
        {'minimum': 85, 'letter': 'A', 'point': 4.00},
        {'minimum': 80, 'letter': 'A-', 'point': 3.67},
        {'minimum': 75, 'letter': 'B+', 'point': 3.33},
        {'minimum': 70, 'letter': 'B', 'point': 3.00},
        {'minimum': 65, 'letter': 'B-', 'point': 2.67},
        {'minimum': 60, 'letter': 'C+', 'point': 2.33},
        {'minimum': 55, 'letter': 'C', 'point': 2.00},
        {'minimum': 50, 'letter': 'D', 'point': 1.00},
        {'minimum': 0, 'letter': 'F', 'point': 0.00},
    ],
    'policy_note': 'DEMO SETTINGS ONLY. Replace using the official course grading scale and assessment weights.',
}

def get_settings():
    DATA.mkdir(parents=True, exist_ok=True)
    if not SETTINGS.exists():
        SETTINGS.write_text(json.dumps(DEFAULT, indent=2), encoding='utf-8')
    return json.loads(SETTINGS.read_text(encoding='utf-8'))

def set_settings(new):
    if not isinstance(new, dict):
        raise ValueError('Settings must be a JSON object')
    threshold = float(new.get('attendance_threshold', 75))
    if not 0 <= threshold <= 100:
        raise ValueError('Attendance threshold must be between 0 and 100')
    bands = new.get('grade_scale')
    if not isinstance(bands, list) or not bands:
        raise ValueError('Grade scale must contain at least one band')
    out, seen = [], set()
    for b in bands:
        minimum, point, letter = float(b['minimum']), float(b['point']), str(b['letter']).strip()
        if not 0 <= minimum <= 100 or not 0 <= point <= 4 or not letter:
            raise ValueError('Invalid grade-scale entry')
        if minimum in seen:
            raise ValueError('Duplicate grade-scale minimum')
        out.append({'minimum': minimum, 'point': point, 'letter': letter[:12]})
        seen.add(minimum)
    out.sort(key=lambda r:r['minimum'], reverse=True)
    if out[-1]['minimum'] != 0:
        raise ValueError('Grade scale must have a band with minimum 0')
    clean = {'attendance_threshold': threshold, 'grade_scale': out,
             'policy_note': 'DEMO SETTINGS ONLY. Verify against the official grading policy.'}
    SETTINGS.write_text(json.dumps(clean, indent=2), encoding='utf-8')
    return clean
