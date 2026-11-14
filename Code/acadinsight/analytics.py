"""Transparent numerical and rule-based analysis; no ML model is claimed."""
from collections import Counter
from dataclasses import asdict
from .models import Student, Subject, Assessment, Attendance, PreviousSemester
import numpy as np
import pandas as pd
from .storage import all_rows
from .config import get_settings


def finite_float(v, label, minimum=None, maximum=None):
    try: n=float(v)
    except (TypeError,ValueError): raise ValueError(f'{label} must be a number')
    if not np.isfinite(n): raise ValueError(f'{label} must be finite')
    if minimum is not None and n<minimum: raise ValueError(f'{label} must be >= {minimum}')
    if maximum is not None and n>maximum: raise ValueError(f'{label} must be <= {maximum}')
    return n

def whole(v,label,minimum=0):
    n=finite_float(v,label,minimum)
    if not n.is_integer(): raise ValueError(f'{label} must be a whole number')
    return int(n)

def grade(percent,settings=None):
    if settings is None: settings=get_settings()
    p=finite_float(percent,'Percentage',0,100)
    for b in sorted(settings['grade_scale'], key=lambda b:float(b['minimum']),reverse=True):
        if p+1e-10 >=float(b['minimum']):
            return {'letter':b['letter'],'point':float(b['point'])}
    raise ValueError('Grade scale is not configured correctly')

def calculate_subject(subject, assessments, attendance=None, settings=None):
    settings = settings or get_settings()
    total_weight, earned, assessment_out = 0.,0.,[]
    for row in assessments:
        obtained=finite_float(row['obtained'],'Obtained marks',0)
        maximum=finite_float(row['max_marks'],'Maximum marks',0.001)
        weight=finite_float(row['weight'],'Weight',0,100)
        if obtained>maximum: raise ValueError('Obtained marks cannot exceed maximum')
        total_weight += weight
        earned += obtained/maximum*weight
        assessment_out.append({**row,'score_percent':round(obtained/maximum*100,2)})
    if total_weight>100.000001: raise ValueError('Total assessment weight exceeds 100%')
    complete=bool(assessments) and abs(total_weight-100)<=1e-6
    current_estimate=(earned/total_weight*100) if total_weight>0 else None
    final_percent=earned if complete else None
    g=grade(final_percent,settings) if complete else None
    att=None
    if attendance:
        attended=whole(attendance['attended'],'Attended classes')
        held=whole(attendance['held'],'Held classes')
        if attended>held: raise ValueError('Attended classes cannot exceed held classes')
        pct=attended/held*100 if held else None
        att={'attended':attended,'held':held,'percentage':round(pct,2) if pct is not None else None,
             'shortage':pct is not None and pct<settings['attendance_threshold']}
    return {**subject,'credits':float(subject['credits']), 'assessment_weight':round(total_weight,2),
            'assessments':assessment_out,'complete':complete,
            'current_estimate':round(current_estimate,2) if current_estimate is not None else None,
            'percent':round(final_percent,2) if final_percent is not None else None,
            'grade':g,'attendance':att}

def advice_for(result, threshold=75):
    suggestions=[]
    if result['attendance'] and result['attendance']['shortage']:
        suggestions.append(f"Attendance is below {threshold:g}%. Attend more classes and ask about the course attendance policy.")
    if result['percent'] is not None:
        p=result['percent']
        if p<50: suggestions.append('Priority: revise fundamentals and meet your instructor for help.')
        elif p<70: suggestions.append('Practice weak topics and schedule two short revision sessions weekly.')
        elif p<85: suggestions.append('Good progress. Review mistakes and practise past questions.')
        else: suggestions.append('Strong result. Keep a consistent revision routine.')
    elif result['current_estimate'] is not None:
        suggestions.append('Marks are incomplete. The current score is an estimate, not a final subject grade.')
    else:
        suggestions.append('Add assessment marks to view performance insights.')
    return suggestions

def student_dashboard(student_id):
    students=all_rows('students')
    raw_student=next((s for s in students if s['id']==student_id),None)
    if not raw_student: raise ValueError('Student not found')
    # Instantiate our PFAI OOP dataclasses, then turn them into serializable records.
    # This keeps the teaching example easy to inspect and the browser API simple.
    student=asdict(Student(**raw_student))
    settings=get_settings()
    subs=[asdict(Subject(s['id'],s['student_id'],s['code'],s['name'],float(s['credits'])))
          for s in all_rows('subjects') if s['student_id']==student_id]
    ass=[asdict(Assessment(a['id'],a['subject_id'],a['component'],float(a['obtained']),
                       float(a['max_marks']),float(a['weight']))) for a in all_rows('assessments')]
    atts=[asdict(Attendance(a['id'],a['subject_id'],int(a['attended']),int(a['held'])))
          for a in all_rows('attendance')]
    previous=[asdict(PreviousSemester(p['id'],p['student_id'],p['title'],float(p['credits']),float(p['gpa'])))
              for p in all_rows('previous_semesters') if p['student_id']==student_id]
    results=[]
    for s in subs:
        r=calculate_subject(s,[a for a in ass if a['subject_id']==s['id']],next((a for a in atts if a['subject_id']==s['id']),None),settings)
        r['advice']=advice_for(r,settings['attendance_threshold'])
        results.append(r)
    complete=[r for r in results if r['complete']]
    credits=float(sum(r['credits'] for r in complete))
    points=float(sum(r['credits']*r['grade']['point'] for r in complete))
    gpa=points/credits if credits else None
    old_credits=float(sum(float(p['credits']) for p in previous))
    old_points=float(sum(float(p['credits'])*float(p['gpa']) for p in previous))
    combined_credits=credits+old_credits
    cgpa=(points+old_points)/combined_credits if combined_credits else None
    completed_percents=np.array([r['percent'] for r in complete],dtype=float)
    avg=float(np.mean(completed_percents)) if len(completed_percents) else None
    values=[r['attendance']['percentage'] for r in results if r['attendance'] and r['attendance']['percentage'] is not None]
    att_avg=float(np.mean(values)) if values else None
    trend=[]
    for r in results:
        for a in r['assessments']:
            trend.append({'subject':r['code'],'component':a['component'],'score_percent':a['score_percent']})
    return {'student':student,'subjects':results,'previous_semesters':previous,
            'stats':{'subjects':len(results),'completed_subjects':len(complete),
                     'semester_gpa':round(gpa,2) if gpa is not None else None,
                     'estimated_cgpa':round(cgpa,2) if cgpa is not None else None,
                     'mean_percentage':round(avg,2) if avg is not None else None,
                     'mean_attendance':round(att_avg,2) if att_avg is not None else None,
                     'count_below_threshold':sum(bool(r['attendance'] and r['attendance']['shortage']) for r in results),
                     'graded_credits':credits, 'all_subjects_complete':len(complete)==len(results) and bool(results)},
            'grade_counts':dict(Counter(r['grade']['letter'] for r in complete)),
            'trend':trend,
            'settings':settings,
            'messages':['This is a demonstration grading scale, not an official university grading policy.',
                        'Semester GPA includes only subjects with 100% total assessment weights.',
                        'Estimated CGPA uses entered previous credit hours and GPAs.']}

def dataframe_summary(student_id):
    """Demonstrates Pandas data frames / group summaries in an inspectable form."""
    d=student_dashboard(student_id)
    rows=[]
    for r in d['subjects']:
        rows.append({'Subject':r['name'],'Credits':r['credits'],'Percent':r['percent'],
                     'Attendance':r['attendance']['percentage'] if r['attendance'] else None})
    return pd.DataFrame(rows)
