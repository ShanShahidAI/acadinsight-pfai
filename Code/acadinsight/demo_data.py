"""Fictional, reproducible demo data. NOT real student records."""
import itertools
from .storage import save_all
from .config import DEFAULT, SETTINGS, DATA
import json

STUDENTS=[
    {'id':'ST-001','name':'Ayesha Khan (Demo)','program':'BS Artificial Intelligence','section':'AI/3-1'},
    {'id':'ST-002','name':'Bilal Ahmed (Demo)','program':'BS Artificial Intelligence','section':'AI/3-1'},
]
COURSES=[('PFAI101','Programming for AI',3),('DSA201','Data Structures',3),
         ('AI201','Artificial Intelligence',3),('CAL201','Multivariable Calculus',3)]
COMP=[('Quiz',20,20),('Assignment',20,20),('Midterm',30,30),('Final',30,30)]
SCORES={
 'ST-001': [[17,18,25,25],[12,15,20,22],[18,19,27,27],[16,17,23,26]],
 'ST-002': [[13,14,17,20],[16,17,22,24],[9,13,15,19],[15,16,21,23]],
}
ATT={ 'ST-001':[(27,30),(20,30),(29,30),(24,30)],
      'ST-002':[(21,30),(26,30),(18,30),(28,30)] }

def reset_demo():
    DATA.mkdir(parents=True, exist_ok=True)
    SETTINGS.write_text(json.dumps(DEFAULT,indent=2),encoding='utf-8')
    subjects=[];assess=[];att=[];prev=[]
    for stu in STUDENTS:
        sid=stu['id']
        prev.extend([{'id':f'PRE-{sid}-1','student_id':sid,'title':'Semester 1', 'credits':'16','gpa':'3.30'},
                     {'id':f'PRE-{sid}-2','student_id':sid,'title':'Semester 2', 'credits':'17','gpa':'3.45'}])
        for i,(code,name,credit) in enumerate(COURSES):
            subid=f'{sid}-{code}'
            subjects.append({'id':subid,'student_id':sid,'code':code,'name':name,'credits':str(credit)})
            for j,(component,maximum,weight) in enumerate(COMP):
                assess.append({'id':f'AS-{sid}-{i}-{j}','subject_id':subid,'component':component,
                               'obtained':str(SCORES[sid][i][j]),'max_marks':str(maximum),'weight':str(weight)})
            attended,held=ATT[sid][i]
            att.append({'id':f'AT-{sid}-{i}','subject_id':subid,'attended':str(attended),'held':str(held)})
    for name,rows in [('students',STUDENTS),('subjects',subjects),('assessments',assess),
                      ('attendance',att),('previous_semesters',prev)]:save_all(name,rows)
    return len(subjects)

if __name__=='__main__':
    print(f'Created demo data for {len(STUDENTS)} fictional students and {reset_demo()} subjects.')
