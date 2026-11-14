"""Unit checks for rubric-friendly, explainable calculations."""
import unittest
from acadinsight.analytics import calculate_subject, grade, student_dashboard, dataframe_summary, advice_for
from acadinsight.charts import chart_png
from acadinsight.storage import all_rows
from app import parse_payload

class AcadInsightTests(unittest.TestCase):
    def setUp(self):
        self.sub={'id':'S','student_id':'ST','code':'PFAI','name':'Programming for AI','credits':'3'}
    def test_weighted_mark_and_grade(self):
        marks=[{'component':'Quiz','obtained':'18','max_marks':'20','weight':'20'},
               {'component':'Final','obtained':'72','max_marks':'80','weight':'80'}]
        row=calculate_subject(self.sub,marks)
        self.assertTrue(row['complete'])
        self.assertEqual(row['percent'],90)
        self.assertEqual(row['grade']['point'],4.0)
    def test_incomplete_marks_are_not_final(self):
        row=calculate_subject(self.sub,[{'component':'Quiz','obtained':'8','max_marks':'10','weight':'20'}])
        self.assertFalse(row['complete'])
        self.assertIsNone(row['percent'])
        self.assertEqual(row['current_estimate'],80)
    def test_attendance_shortage(self):
        row=calculate_subject(self.sub,[],{'attended':'14','held':'20'})
        self.assertEqual(row['attendance']['percentage'],70)
        self.assertTrue(row['attendance']['shortage'])
        self.assertIn('Attendance',advice_for(row)[0])
    def test_no_divide_zero_attendance(self):
        row=calculate_subject(self.sub,[],{'attended':'0','held':'0'})
        self.assertIsNone(row['attendance']['percentage'])
    def test_invalid_scores_or_weights(self):
        with self.assertRaises(ValueError): calculate_subject(self.sub,[{'obtained':'21','max_marks':'20','weight':'100'}])
        with self.assertRaises(ValueError): calculate_subject(self.sub,[{'obtained':'4','max_marks':'10','weight':'110'}])
    def test_demo_student_gpa(self):
        d=student_dashboard('ST-001')
        self.assertEqual(d['stats']['completed_subjects'],4)
        self.assertAlmostEqual(d['stats']['semester_gpa'],3.58,places=2)
        self.assertEqual(d['stats']['count_below_threshold'],1)
    def test_pandas_and_graphs(self):
        df=dataframe_summary('ST-001')
        self.assertEqual(len(df),4)
        for kind in ('grades','attendance','assessments'):
            self.assertTrue(chart_png('ST-001',kind).startswith(b'\x89PNG\r\n\x1a\n'))
    def test_validation_and_dependencies(self):
        with self.assertRaises(ValueError):parse_payload('subjects',{'student_id':'does-not-exist','code':'TEST','name':'Test','credits':'3'})
        with self.assertRaises(ValueError):parse_payload('attendance',{'subject_id':'ST-001-PFAI101','attended':20,'held':10})
        with self.assertRaises(ValueError):parse_payload('assessments',{'subject_id':'ST-001-PFAI101','component':'Other','obtained':5,'max_marks':10,'weight':50})
    def test_csv_records_and_grades(self):
        self.assertEqual(len(all_rows('students')),2)
        self.assertEqual(grade(49.99)['letter'],'F')
        self.assertEqual(grade(85)['letter'],'A')

if __name__=='__main__':unittest.main(verbosity=2)
