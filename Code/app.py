"""AcadInsight local website with Python standard-library HTTP server.

No Flask installation is needed: coursework emphasizes Python, functions,
OOP, NumPy/Pandas/Matplotlib. Visit http://127.0.0.1:8765 after starting.
This local coursework demo is NOT a public web server and has no login.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
from pathlib import Path
from io import StringIO
import csv
import json
import sys
import mimetypes
import threading
from acadinsight.config import DATA, get_settings, set_settings
from acadinsight.storage import all_rows, find, create, upsert, new_id, delete_subject, SCHEMA
from acadinsight.analytics import student_dashboard, finite_float, whole, dataframe_summary
from acadinsight.charts import chart_png
from acadinsight.demo_data import reset_demo

ROOT=Path(__file__).resolve().parent
PORT=8765
API_LOCK=threading.RLock()

def required(d,key):
    x=str(d.get(key,'')).strip()
    if not x:raise ValueError(f'{key} is required')
    if len(x)>140:raise ValueError(f'{key} is too long')
    return x

def parse_payload(route, data):
    if route=='students':
        return {'id':new_id('ST'),'name':required(data,'name'),
                'program':str(data.get('program','BS Artificial Intelligence')).strip()[:100],
                'section':str(data.get('section','AI/3-1')).strip()[:30]}
    if route=='subjects':
        sid=required(data,'student_id')
        if not find('students',sid):raise ValueError('Student not found')
        credits=finite_float(data.get('credits'),'Credit hours',.5,12)
        return {'id':new_id('SUB'),'student_id':sid,'code':required(data,'code').upper(),
                'name':required(data,'name'),'credits':str(credits)}
    if route=='assessments':
        subid=required(data,'subject_id')
        if not find('subjects',subid):raise ValueError('Subject not found')
        label=required(data,'component')
        maximum=finite_float(data.get('max_marks'),'Maximum marks',.001,100000)
        obtained=finite_float(data.get('obtained'),'Obtained marks',0,maximum)
        weight=finite_float(data.get('weight'),'Weight',0,100)
        others=[a for a in all_rows('assessments') if a['subject_id']==subid and a['component'].lower()!=label.lower()]
        if sum(float(a['weight']) for a in others)+weight>100.000001:
            raise ValueError('Assessment weights must not exceed 100%')
        existing=next((a for a in all_rows('assessments') if a['subject_id']==subid and a['component'].lower()==label.lower()),None)
        return {'id':existing['id'] if existing else new_id('AS'),'subject_id':subid,
                'component':label,'obtained':str(obtained),'max_marks':str(maximum),'weight':str(weight)}
    if route=='attendance':
        subid=required(data,'subject_id')
        if not find('subjects',subid):raise ValueError('Subject not found')
        attended=whole(data.get('attended'),'Attended classes')
        held=whole(data.get('held'),'Held classes')
        if attended>held:raise ValueError('Attended classes cannot exceed classes held')
        existing=next((a for a in all_rows('attendance') if a['subject_id']==subid),None)
        return {'id':existing['id'] if existing else new_id('AT'), 'subject_id':subid,
                'attended':str(attended),'held':str(held)}
    if route=='previous_semesters':
        sid=required(data,'student_id')
        if not find('students',sid):raise ValueError('Student not found')
        title=required(data,'title')
        credits=finite_float(data.get('credits'),'Previous credits',.5,300)
        gpa=finite_float(data.get('gpa'),'Previous GPA',0,4)
        existing=next((a for a in all_rows('previous_semesters') if a['student_id']==sid and a['title'].lower()==title.lower()),None)
        return {'id':existing['id'] if existing else new_id('PRE'),'student_id':sid,
                'title':title,'credits':str(credits),'gpa':str(gpa)}
    raise ValueError('Unsupported route')

class Handler(BaseHTTPRequestHandler):
    def log_message(self,fmt,*args):
        print('[AcadInsight]',fmt%args)
    def respond(self,data,code=200,ctype='application/json; charset=utf-8',download=None):
        payload=(json.dumps(data,allow_nan=False).encode('utf-8') if ctype.startswith('application/json') else data)
        self.send_response(code)
        self.send_header('Content-Type',ctype)
        self.send_header('Content-Length',str(len(payload)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        if download:self.send_header('Content-Disposition',f'attachment; filename="{download}"')
        self.end_headers()
        self.wfile.write(payload)
    def fail(self,error):
        self.respond({'ok':False,'error':str(error)},400)
    def do_GET(self):
        try:self._get()
        except (ValueError, KeyError) as e:self.fail(e)
        except Exception as e:print('ERROR:',e,file=sys.stderr);self.respond({'ok':False,'error':'Unexpected server error'},500)
    def _get(self):
        u=urlparse(self.path);path=u.path
        qs=parse_qs(u.query)
        sid=qs.get('student_id',[''])[0]
        if path in ('/','/index.html'):
            return self.respond((ROOT/'static'/'index.html').read_bytes(),ctype='text/html; charset=utf-8')
        if path.startswith('/static/'):
            name=path.removeprefix('/static/')
            if name not in ('app.css','app.js'):
                return self.respond({'ok':False,'error':'Not found'},404)
            ctype=mimetypes.guess_type(name)[0] or 'text/plain'
            return self.respond((ROOT/'static'/name).read_bytes(),ctype=ctype+'; charset=utf-8')
        if path=='/api/students':return self.respond({'students':all_rows('students')})
        if path=='/api/settings':return self.respond(get_settings())
        if path=='/api/dashboard':return self.respond(student_dashboard(sid))
        if path=='/api/summary':
            df=dataframe_summary(sid)
            return self.respond({'rows':df.astype(object).where(df.notna(),None).to_dict(orient='records')})
        if path=='/api/chart':
            return self.respond(chart_png(sid,qs.get('type',['grades'])[0]),ctype='image/png')
        if path=='/api/export':
            table=qs.get('table',[''])[0]
            if table not in SCHEMA:raise ValueError('Invalid export table')
            mem=StringIO();writer=csv.DictWriter(mem,fieldnames=SCHEMA[table]);writer.writeheader();writer.writerows(all_rows(table))
            return self.respond(mem.getvalue().encode('utf-8-sig'),ctype='text/csv; charset=utf-8',download=f'acadinsight_{table}.csv')
        self.respond({'ok':False,'error':'Not found'},404)
    def do_POST(self):
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n<=0 or n>150000:raise ValueError('JSON body is empty or too large')
            body=json.loads(self.rfile.read(n))
            if not isinstance(body,dict):raise ValueError('Expected JSON object')
            route=urlparse(self.path).path
            with API_LOCK:
                if route=='/api/settings':return self.respond({'ok':True,'settings':set_settings(body)})
                if route=='/api/reset':reset_demo();return self.respond({'ok':True,'message':'Demo data restored'})
                entity=route.removeprefix('/api/')
                if entity not in SCHEMA:raise ValueError('Unknown endpoint')
                payload=parse_payload(entity,body)
                if entity in ('assessments','attendance','previous_semesters'):upsert(entity,payload)
                else:create(entity,payload)
                return self.respond({'ok':True,'record':payload},201)
        except (ValueError,TypeError,KeyError,json.JSONDecodeError) as e:self.fail(e)
        except Exception as e:print('ERROR:',e,file=sys.stderr);self.respond({'ok':False,'error':'Unexpected server error'},500)
    def do_DELETE(self):
        try:
            u=urlparse(self.path)
            sid=parse_qs(u.query).get('id',[''])[0]
            if u.path!='/api/subjects' or not sid:raise ValueError('Only subject deletion is supported')
            with API_LOCK:delete_subject(sid)
            self.respond({'ok':True})
        except ValueError as e:self.fail(e)

if __name__=='__main__':
    if not all_rows('students'):
        print('No student records found; loading fictional demo records.')
        reset_demo()
    print(f'AcadInsight started at http://127.0.0.1:{PORT}')
    print('Local class demo only. Press Ctrl+C to stop.')
    try:ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
    except KeyboardInterrupt:print('\nServer stopped.')
