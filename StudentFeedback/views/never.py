from login.views import generate_session_table_name
def student_report(report_type,data,ids,dynamic_argument):
	StuFeedbackMarks = generate_session_table_name("StuFeedbackMarks_",session_name)

	''' data : HIDDEN_DATA , data : SEMI_HIDDEN_DATA ,data : COMPLETE_DATA'''
	if(report_type=="SINGLE_STUDENT"):
		ids=[faculty_list]
		# dynamic_filter['feedback_id__emp_id__in']=ids
	else:
		pass
		# dynamic_filter['feedback_id__emp_id__in']=ids
	if 'subject' in dynamic_argument:
		dynamic_filter['feedback_id__subject__in']=dynamic_argument['subject']
	if 'residential_status' in dynamic_argument:
		dynamic_filter['attribute__residential_status__in']=dynamic_argument['residential_status']
	if 'max_marks' in dynamic_argument:
		dynamic_filter['attribute__max_marks__in']=dynamic_argument['max_marks']
	if 'min_marks' in dynamic_argument:
		dynamic_filter['attribute__min_marks__in']=dynamic_argument['min_marks']
	if 'gender' in dynamic_argument:
		dynamic_filter['attribute__gender__in']=dynamic_argument['gender']
	if 'gender' in dynamic_argument:
		dynamic_filter['attribute__eligible_settings_id__in']=dynamic_argument['eligible_settings']
	if 'sem' in dynamic_argument: 
		dynamic_filter['attribute__eligible_settings_id__sem__in']=dynamic_argument['sem']
	if 'gender' in dynamic_argument:
		dynamic_filter['subject_type__in']=dynamic_argument['subject_type']
	if 'attribute_status' in dynamic_argument:
		dynamic_filter['attribute__eligible_settings_id__status__in']=dynamic_argument['attribute_status']
	values_array=[]
	if data=="HIDDEN_DATA":
		values_array=['feedback_id','feedback_id__feedback_id','feedback_id__emp_id','feedback_id__subject','feedback_id__subject__sub_name','feedback_id__total_lectures','feedback_id__subject__sub_alpha_code','feedback_id__subject__sub_num_code','feedback_id__subject__subject_type__value','feedback_id__remark','feedback_id__feedback_id__uniq_id','feedback_id__feedback_id__attendance_per','feedback_id__feedback_id__locked','feedback_id__feedback_id__status','feedback_id__feedback_id__time_stamp','marks','attribute','attribute__name','attribute__gender__value','attribute__min_marks','attribute__max_marks','attribute__residential_status','attribute__eligible_settings_id__sem__sem','attribute__eligible_settings_id__sem','attribute__eligible_settings_id__sem__dept__dept__value','attribute__eligible_settings_id__sem__dept__course__value','subject_type']
	elif data=="SEMI_HIDDEN_DATA":
		values_array=['feedback_id','feedback_id__feedback_id','feedback_id__emp_id','feedback_id__subject','feedback_id__subject__sub_name','feedback_id__total_lectures','feedback_id__subject__sub_alpha_code','feedback_id__subject__sub_num_code','feedback_id__subject__subject_type__value','feedback_id__remark','feedback_id__feedback_id__uniq_id','feedback_id__feedback_id__attendance_per','feedback_id__feedback_id__locked','feedback_id__feedback_id__status','feedback_id__feedback_id__time_stamp','marks','attribute','attribute__name','attribute__gender__value','attribute__min_marks','attribute__max_marks','attribute__residential_status','attribute__eligible_settings_id__sem__sem','attribute__eligible_settings_id__sem','attribute__eligible_settings_id__sem__dept__dept__value','attribute__eligible_settings_id__sem__dept__course__value','subject_type']
	if data=="COMPLETE_DATA":
		values_array=['feedback_id','feedback_id__feedback_id','feedback_id__emp_id','feedback_id__subject','feedback_id__subject__sub_name','feedback_id__total_lectures','feedback_id__subject__sub_alpha_code','feedback_id__subject__sub_num_code','feedback_id__subject__subject_type__value','feedback_id__remark','feedback_id__feedback_id__uniq_id','feedback_id__feedback_id__uniq_id__uniq_id__name','feedback_id__feedback_id__uniq_id__section__section','feedback_id__feedback_id__uniq_id__uniq_id__lib','feedback_id__feedback_id__uniq_id__class_roll_no','feedback_id__feedback_id__uniq_id__fee_status','feedback_id__feedback_id__uniq_id__mob','feedback_id__feedback_id__attendance_per','feedback_id__feedback_id__locked','feedback_id__feedback_id__status','feedback_id__feedback_id__time_stamp','marks','attribute','attribute__name','attribute__gender__value','attribute__min_marks','attribute__max_marks','attribute__residential_status','attribute__eligible_settings_id__sem__sem','attribute__eligible_settings_id__sem','attribute__eligible_settings_id__sem__dept__dept__value','attribute__eligible_settings_id__sem__dept__course__value','subject_type']
	result=list(StuFeedbackMarks.objects.filter(feedback_id__feedback_id__uniq_id__in=ids,**dynamic_filter).values(*values_array))

def faculty_report(report_type,dynamic_argument):
	StuFeedbackMarks = generate_session_table_name("StuFeedbackMarks_",session_name)

	dynamic_filter={}
	if 'faculty_list'in dynamic_argument:
		dynamic_filter['feedback_id__emp_id__in']=dynamic_argument['faculty_list']
	if 'subject' in dynamic_argument:
		dynamic_filter['feedback_id__subject__in']=dynamic_argument['subject']
	if 'residential_status' in dynamic_argument:
		dynamic_filter['attribute__residential_status__in']=dynamic_argument['residential_status']
	if 'max_marks' in dynamic_argument:
		dynamic_filter['attribute__max_marks__in']=dynamic_argument['max_marks']
	if 'min_marks' in dynamic_argument:
		dynamic_filter['attribute__min_marks__in']=dynamic_argument['min_marks']
	if 'gender' in dynamic_argument:
		dynamic_filter['attribute__gender__in']=dynamic_argument['gender']
	if 'gender' in dynamic_argument:
		dynamic_filter['attribute__eligible_settings_id__in']=dynamic_argument['eligible_settings']
	if 'sem' in dynamic_argument:
		dynamic_filter['attribute__eligible_settings_id__sem__in']=dynamic_argument['sem']
	if 'gender' in dynamic_argument:
		dynamic_filter['subject_type__in']=dynamic_argument['subject_type']
	if 'attribute_status' in dynamic_argument:
		dynamic_filter['attribute__eligible_settings_id__status__in']=dynamic_argument['attribute_status']


	values_array=['feedback_id','feedback_id__feedback_id','feedback_id__emp_id','feedback_id__subject','feedback_id__subject__sub_name','feedback_id__total_lectures','feedback_id__subject__sub_alpha_code','feedback_id__subject__sub_num_code','feedback_id__subject__subject_type__value','feedback_id__remark','feedback_id__feedback_id__uniq_id','feedback_id__feedback_id__attendance_per','feedback_id__feedback_id__locked','feedback_id__feedback_id__status','feedback_id__feedback_id__time_stamp','marks','attribute','attribute__name','attribute__gender__value','attribute__min_marks','attribute__max_marks','attribute__residential_status','attribute__eligible_settings_id__sem__sem','attribute__eligible_settings_id__sem','attribute__eligible_settings_id__sem__dept__dept__value','attribute__eligible_settings_id__sem__dept__course__value','subject_type']

	if("CONSOLIDATE MARKS" in report_type):
		result=StuFeedbackMarks.objects.filter(**dynamic_filter).annotate(average_marks=Avg('marks')).values(*dynamic_argument['WISE'])
	elif("CONSOLIDATE COUNT" in report_type):
		result=StuFeedbackMarks.objects.filter(**dynamic_filter).annotate(count_student=Count('feedback_id__feedback_id__uniq_id'),count_subject=Count('feedback_id__subject')).values(*dynamic_argument['WISE'])
	else:
		result=StuFeedbackMarks.objects.filter(**dynamic_filter).values(*values_array)
	return result
