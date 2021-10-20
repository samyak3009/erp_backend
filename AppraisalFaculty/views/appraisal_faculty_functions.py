
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# '''essentials'''

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db.models import Q, Sum, F, Value, CharField, Case, When, Value, IntegerField
import json
# from datetime import datetime
# import datetime
from datetime import datetime
from datetime import date
# import datetime
import operator


# '''import constants'''
from StudentMMS.constants_functions import requestType
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from AppraisalStaff.views.appraisal_staff_function import *
from AppraisalStaff.views.appraisal_staff_checks_function import *

# '''import models'''
from musterroll.models import EmployeePerdetail, Roles,EmployeeCertification
from login.models import EmployeePrimdetail
from login.models import AarDropdown, EmployeeDropdown
from AppraisalStaff.models import *
from AppraisalFaculty.models import *
from AppraisalStaff.constants_functions.functions import *
from StudentAcademics.models import *
from Achievement.models import *
from LessonPlan.models import *

# '''import views'''
from AppraisalStaff.views import *
from Achievement.views.achievement_function import GetAllAchievementEmployee,GetAllActivitiesEmployee
from StudentFeedback.views.feedback_function_views import individual_faculty_consolidate, faculty_feedback_details
from Accounts.views import getCurrentSession
from StudentAcademics.views import *
from login.views import checkpermission, generate_session_table_name
from musterroll.views import get_net_experience

#'''import functions'''
from aar.dept_achievement import get_all_emp
from .appraisal_faculty_checks import *

# Create your views here.

#/////////////////////////////////////////////////YASH///////////////////////////////////////////////////////////////////////////////

def create_intial_pending_request_new(emp_id, session, session_name):
    ## form_filled_status='N' and form_approved="PENDING" ###
    today_date = date.today()
    check = FacultyAppraisal.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY", session=session, form_filled_status='N', form_approved="PENDING", status="PENDING").exclude(emp_id="00007").exclude(status="DELETE").exclude(emp_id__emp_status="SEPARATE").values('id')
    #### CREATE FOR EVERY NEW FORM OPENING AND ANY UPDATION IN DETAILS ####
    details = get_emp_part_data_new(emp_id, session, {})
    if len(check) == 0 or check_if_emp_details_same_or_not_new(emp_id, details, session, session_name) == False:
        if len(details) > 0:
            FacultyAppraisal.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=details['emp_id']), dept=EmployeeDropdown.objects.get(sno=details['dept']), desg=EmployeeDropdown.objects.get(sno=details['desg']), highest_qualification=details['h_qual'], salary_type=AccountsDropdown.objects.get(sno=details['salary_type_id']), current_gross_salary=details['current_gross_salary'], agp=details['agp'], total_experience=details['total_experience'], emp_date=today_date, session=AccountsSession.objects.get(id=session))
            return True
        else:
            return False
    else:
        return True



def get_recomended_data_faculty_new(e_id, level,  session):
    data = {}
    data['data'] = []
    data['key'] = []
    data['heading'] = []
    heading = {1: ['Approved by 1st Reporting', 'Review request by 2nd Reporting', 'Reviewed by 1st Reporting'], 2: ['Approved by 2nd Reporting', 'Send a review request at 1st reporting', 'Approve the reviewed request by 1st Reporting'], 2: ['Approved by 3rd Reporting', 'Send a review request at 2nd Reporting', 'Approve the reviewed request by 2nd Reporting']}
    if level != 0:
        for l in range(1, int(level) + 1):
            i = 0
            qry = FacAppRecommendationApproval.objects.filter(emp_id=e_id, level=l,session=session).exclude(status="DELETE").exclude(approval_status="REVIEW").values('id', 'emp_id', 'increment_type', 'increment_amount', 'promoted_to', 'level', 'approval_status', 'added_by', 'added_by__name', 'added_by__desg__value', 'session', 'session__session', 'status', 'promoted_to__value').order_by('id')
            if len(qry) > 0:

                for q in qry:
                    amount = 0.0
                    if q['increment_amount']!=None:
                        try:
                            amount = float(q['increment_amount'])
                        except:
                            amount = 0.0
                    q['editable'] = check_if_form_editable_or_not_faculty_new(e_id, l, session, level, None)
                    q['table_data'] = get_increment_in_salary(q['increment_type'], e_id, q['session'], get_salary_type(e_id, q['session'], {})['salary_type__value'], amount)
                    # print(q['table_data'], 'vrinda')
                    data['data'].append(q)
                    data['key'].append(q['approval_status'])
                    data['heading'].append(str(q['approval_status']) + ' by ' + str(q['added_by__desg__value']))
                    i = i + 1

        return data
    return data




def get_data_in_faculty_form_format(data):
    ### data-format== course/branch/sem/subject/(session) where {eg:session=2018-2019} #######
    format_data = ''
    flag = 0
    for d in data:
        if flag == 0:
            format_data = str(d)
            flag = 1
        else:
            format_data = format_data + ' / ' + str(d)
    return format_data




def get_period(day):
    year = int(day / 365)
    week = int((day % 365 /7))
    days = (day % 365) % 7
    if year>0:
        period = str(year) + ' '+ "years " + str(week) +' '+"weeks "+str(days)+" "+"days"
    elif week > 0:
        period = str(week) +' '+"weeks "+str(days)+" "+"days"
    elif days>=0:
        period = str(days+1)+" "+"days"
    return period



def get_last_x_year_ses(session_name,x):
    year = []
    for i in range(1,x+1):
        Sessions=[]
        Sessions.append(str(int(session_name[:2]) - i) + str(int(session_name[:2]) - (i-1)) + 'o')
        Sessions.append(str(int(session_name[:2]) - i) + str(int(session_name[:2]) - (i-1)) + 'e')
        year.append(Sessions)
    return year


######################################################################CAT-1######################################################################
# def get_employee_subject_section_wise_lecture_plan_new(emp_id, session, session_name):####LESSON PLAN PROPOSED AND TAKEN
#   ### data-format== course/branch/sem/subject/(session) where {eg:session=2018-2019} #######
#   data = []
#   Sessions = []
#   Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'o')
#   Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'e')
#   for ses in Sessions:
#       Attendance = generate_session_table_name('Attendance_', ses)
#       LessonProposeApproval = generate_session_table_name('LessonProposeApproval_', ses)
#       qry = Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY").exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").values('section__sem_id', 'subject_id','section','isgroup','group_id').distinct()
#       if len(qry) > 0:
#           for q in qry:
#               qry_approved_lp = list(LessonProposeApproval.objects.filter(propose_detail__lesson_propose__subject=q['subject_id'], propose_detail__lesson_propose__added_by=emp_id).exclude(status="DELETE").values('propose_detail__id', 'approval_status'))
#               approved_propose_detail=[]
#               for qry_app in qry_approved_lp:
#                   if qry_app['propose_detail__id'] not in approved_propose_detail:
#                       approved_propose_detail.append(qry_app['propose_detail__id'])
#               lectures = Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY", section__sem_id=q['section__sem_id'], subject_id=q['subject_id'],section=q['section'],normal_remedial='N',isgroup=q['isgroup']).exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").values('section__sem_id', 'section__sem_id__sem', 'section__sem_id__dept__course', 'section__sem_id__dept__course__value', 'section__sem_id__dept__dept', 'section__sem_id__dept__dept__value', 'subject_id', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id__sub_name', 'subject_id__subject_type', 'subject_id__subject_type__value','section__section').annotate(total=Count('id')).distinct()
#               if len(lectures) > 0:
#                   lectures[0]['subject'] = str(lectures[0]['subject_id__sub_name'])+' (' + str(lectures[0]['subject_id__sub_alpha_code']) + ' - ' + str(lectures[0]['subject_id__sub_num_code']) + ')'
#                   semester =  lectures[0]['section__sem_id__sem']
#                   format_data_array = [lectures[0]['section__sem_id__dept__course__value'], lectures[0]['section__sem_id__dept__dept__value'],semester,lectures[0]['section__section'], lectures[0]['subject']]
#                   format_data = str(get_data_in_faculty_form_format(format_data_array))
#                   lectures[0]['data-format'] = format_data
#                   lectures[0]['session_name'] = ses
#                   lectures[0]['proposed']=len(approved_propose_detail)
#                   data.append(lectures[0])
#   return data

def get_employee_subject_section_wise_lecture_plan_new(emp_id, session, session_name):####LESSON PLAN PROPOSED AND TAKEN
    ### data-format== course/branch/sem/subject/(session) where {eg:session=2018-2019} #######
    data = []
    Sessions = []
    Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'o')
    Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'e')
    # att_type = list(StudentAcademicsDropdown.objects.filter(value__in=['NORMAL','TUTORIAL'],session__in=[8,9]).values_list('sno',flat=True))
    for ses in Sessions:
        Attendance = generate_session_table_name('Attendance_', ses)
        LessonProposeApproval = generate_session_table_name('LessonProposeApproval_', ses)
        qry = Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY").exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").values('section__sem_id', 'subject_id','section','isgroup','group_id').distinct()
        if len(qry) > 0:
            for q in qry:
                if q['isgroup'] == 'N':
                    extra_filter2={'section':q['section']}
                    extra_filter1={'propose_detail__lesson_propose__section':q['section']}
                else:
                    extra_filter2={'group_id':q['group_id']}
                    extra_filter1={'propose_detail__lesson_propose__group_id':q['group_id']}
                qry_approved_lp = list(LessonProposeApproval.objects.filter(propose_detail__lesson_propose__subject=q['subject_id'], propose_detail__lesson_propose__added_by=emp_id).filter(**extra_filter1).exclude(status="DELETE").values('propose_detail__id', 'approval_status'))
                approved_propose_detail=[]
                for qry_app in qry_approved_lp:
                    if qry_app['propose_detail__id'] not in approved_propose_detail:
                        approved_propose_detail.append(qry_app['propose_detail__id'])
                lectures = Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY", section__sem_id=q['section__sem_id'],section=q['section'] ,subject_id=q['subject_id'],isgroup=q['isgroup']).filter(**extra_filter2).exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").values('section__sem_id', 'section__sem_id__sem', 'section__sem_id__dept__course', 'section__sem_id__dept__course__value', 'section__sem_id__dept__dept', 'section__sem_id__dept__dept__value', 'subject_id', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id__sub_name', 'subject_id__subject_type', 'subject_id__subject_type__value','section__section','group_id__group_name').annotate(total=Count('id')).distinct()
                # print(lectures)
                if len(lectures) > 0:
                    if lectures[0]['group_id__group_name'] != None:
                        lectures[0]['subject'] = str(lectures[0]['subject_id__sub_name'])+' (' + str(lectures[0]['subject_id__sub_alpha_code']) + ' - ' + str(lectures[0]['subject_id__sub_num_code']) + ')' + ' /GROUP NAME' + ' (' + str(lectures[0]['group_id__group_name']) + ')'
                    else:
                        lectures[0]['subject'] = str(lectures[0]['subject_id__sub_name'])+' (' + str(lectures[0]['subject_id__sub_alpha_code']) + ' - ' + str(lectures[0]['subject_id__sub_num_code']) + ')'
                    semester =  lectures[0]['section__sem_id__sem']
                    format_data_array = [lectures[0]['section__sem_id__dept__course__value'], lectures[0]['section__sem_id__dept__dept__value'],semester,lectures[0]['section__section'], lectures[0]['subject']]
                    format_data = str(get_data_in_faculty_form_format(format_data_array))
                    lectures[0]['data-format'] = format_data
                    lectures[0]['session_name'] = ses
                    lectures[0]['proposed']=len(approved_propose_detail)
                    data.append(lectures[0])
    return data

def get_overall_att_subject_section_wise_lecture_new(emp_id, session, session_name):#########CLASS OVERALL ATT
    data = []
    Sessions = []
    Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'o')
    Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'e')
    #NORMAL AND TUTORIAL
    att_type = list(StudentAcademicsDropdown.objects.filter(value__in=['NORMAL','TUTORIAL'],session__in=[8,9]).values_list('sno',flat=True))
    for ses in Sessions:
        Attendance = generate_session_table_name('Attendance_', ses)
        StudentAttStatus = generate_session_table_name('StudentAttStatus_', ses)
        studentSession = generate_session_table_name('studentSession_', ses)
        qry = Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY").exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").values('section__sem_id','section__sem_id__dept__course__value','section__sem_id__dept__dept__value','section__sem_id__sem', 'subject_id','section','section__section','subject_id__sub_alpha_code','subject_id__sub_num_code','subject_id__sub_name').distinct()
        for q in qry:
            lectures = list(Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY", section__sem_id=q['section__sem_id'], subject_id=q['subject_id'],section=q['section'],normal_remedial__in=['N','T']).exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").values_list("id",flat=True))
            total_present_in_lec = StudentAttStatus.objects.filter(marked_by=emp_id,marked_by__emp_category__value="FACULTY",present_status="P",approval_status="APPROVED",att_id__in=lectures,att_type__in=att_type).exclude(status="DELETE").exclude(marked_by__emp_status="SEPARATE").exclude(marked_by="00007").count()
            total_strength = StudentAttStatus.objects.filter(marked_by=emp_id,marked_by__emp_category__value="FACULTY",present_status__in=["P","A"],approval_status="APPROVED",att_id__in=lectures,att_type__in=att_type).exclude(status="DELETE").exclude(marked_by__emp_status="SEPARATE").exclude(marked_by="00007").count()
            if len(lectures) > 0:
                q['subject'] = '(' + str(q['subject_id__sub_alpha_code']) + ' - ' + str(q['subject_id__sub_num_code']) + ')'
                q['total_present_in_lec'] = total_present_in_lec
                q['total_strength'] = total_strength
                semester = int_to_Roman(int(q['section__sem_id__sem']))
                format_data_array = [q['section__sem_id__dept__course__value'], q['section__sem_id__dept__dept__value'],semester,q['section__section'],q['subject_id__sub_name'], q['subject']]
                format_data = str(get_data_in_faculty_form_format(format_data_array))
                q['data-format'] = format_data
                q['session_name'] = ses
                
                data.append(q)
    return data


def get_employee_subject_setion_wise_total_lecture_new(emp_id, session, session_name):######SUBJECT TAKEN IN SECTIONS
    ### data-format== course/branch/sem/subject/section(session) where {eg:session=2018-2019} #######
    data = []
    Sessions = []
    Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'o')
    Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'e')
    subject_type = set()
    for ses in Sessions:
        Attendance = generate_session_table_name('Attendance_', ses)
        qry = Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY").exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").values('section__sem_id', 'subject_id', 'section','subject_id__sub_name','subject_id__sub_alpha_code','subject_id__sub_num_code').distinct()
        if len(qry) > 0:
            for q in qry:
                lectures = list(Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY", subject_id=q['subject_id'], section=q['section']).exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").values('section__sem_id', 'section__sem_id__sem', 'section__sem_id__dept__course', 'section__sem_id__dept__course__value', 'section__sem_id__dept__dept', 'section__sem_id__dept__dept__value', 'subject_id', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id__sub_name', 'section', 'section__section', 'subject_id__subject_type', 'subject_id__subject_type__value').distinct())
                # print(len(lectures))
                for x in lectures:
                    x['subject'] = '(' + str(x['subject_id__sub_alpha_code']) + ' - ' + str(x['subject_id__sub_num_code']) + ')'
                    format_data_array = [x['section__sem_id__dept__course__value'], x['section__sem_id__dept__dept__value'], x['section__sem_id__sem'], x['subject']]
                    format_data = str(get_data_in_faculty_form_format(format_data_array))
                    x['data-format'] = format_data
                    x['session_name'] = ses
                    data.append(x)
                    subject_type.add(x['subject_id__subject_type'])
    return [data, subject_type]



def get_employee_exclude_lab_subject_setion_wise_total_lecture_new(emp_id, session, session_name):######SUBJECT TAKEN IN SECTIONS
    ### data-format== course/branch/sem/subject/section(session) where {eg:session=2018-2019} #######
    data = []
    Sessions = []
    Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'o')
    Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'e')
    subject_type = set()
    for ses in Sessions:
        Attendance = generate_session_table_name('Attendance_', ses)
        qry = Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY").exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").exclude(subject_id__max_university_marks=0).exclude(subject_id__subject_type__value="LAB").values('section__sem_id', 'subject_id', 'section','subject_id__sub_name','subject_id__sub_alpha_code','subject_id__sub_num_code').distinct()
        if len(qry) > 0:
            for q in qry:
                lectures = list(Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY", subject_id=q['subject_id'], section=q['section']).exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").exclude(subject_id__subject_type__value="LAB").values('section__sem_id', 'section__sem_id__sem', 'section__sem_id__dept__course', 'section__sem_id__dept__course__value', 'section__sem_id__dept__dept', 'section__sem_id__dept__dept__value', 'subject_id', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id__sub_name', 'section', 'section__section', 'subject_id__subject_type', 'subject_id__subject_type__value').distinct())
                for x in lectures:
                    x['subject'] = '(' + str(x['subject_id__sub_alpha_code']) + ' - ' + str(x['subject_id__sub_num_code']) + ')'
                    format_data_array = [x['section__sem_id__dept__course__value'], x['section__sem_id__dept__dept__value'], x['section__sem_id__sem'], x['subject']]
                    format_data = str(get_data_in_faculty_form_format(format_data_array))
                    x['data-format'] = format_data
                    x['session_name'] = ses
                    data.append(x)
                    subject_type.add(x['subject_id__subject_type'])
    return [data, subject_type]


def get_score_cat1_A1_new(per):
    per_point_marks =10/((100-80)+1)
    if per<80:
        score_claimed=0
    else:
        score_claimed = round((per-79)*per_point_marks,2)
    return score_claimed




def get_heading_of_cat1_new(part, level, status):
    part = str(part)
    heading = []
    if part == "A1":
        main_heading = 'A1.Lectures(including additional skills subjects), Seminars, Tutorials, Practical’s, Project Guidance (B.Tech, B.Pharm, M.Tech, M.Pharm, MBA, MCA)  Contact Hour <p style="color:blue">(Give semester wise details, where necessary)</p>'
        heading = ['Session','Course/Paper & Year', 'Total lectures as per academic calendar (a)', 'Total no of lecture takne as per portal (b)','Difference(b-a)' ,'% of classes taken as per documented record (a/b)*100', 'Score claimed']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')
    elif part == "A2":
        main_heading  = 'A2.Percentage of average attendance <p style="color:blue"> Score obtained as per % of attendance (90-100=5, 89-85=4, 84-80=3, 79-75=2, 74-70=1)(Max. 5 Marks)</p>'
        heading = ['Session','Course/Paper/Year & Subject', '% of Average Attendance', 'Score obtained as per % of attendance']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')
    elif part == "A3":
        main_heading = 'A3.Details of MOOC’s Developed <p style="color:blue">(1 MOOCs/05 Marks)</p>'
        heading = ['MOOC Title','MOOC Type','Details of MOOC’s Developed ','Score Claimed']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')
    elif part == "A4":
        main_heading = 'A4.MOOC’s (NPTEL/Coursera/edx) <p style="color:blue">Certification Elite + Gold-10 Marks, Elite + Silver-8 Marks, Elite-7 Marks, Pass-5 Marks </p>'
        heading = ['Name of Course','MOOCs Type','NPTEL Type','Score Claimed']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')
    elif part == "A5":
        main_heading = 'A5.Academic Result <p style="color:blue">(Entire Academic Year)</p>'
        heading = ['Branch/Semester/Section','Subject','Result (Clear Pass %)','Result (Ext.Theory Exam Average)','No of Students with marks in external exam']
        
    elif part == "A6":
        main_heading = 'A6.Invited Lectures/ presentation in conferences/ talks in refresher courses at National or International Conference/Seminars <p style="color:blue">(International (out of India) -5 Marks, National (within India) -2.5 Marks each) (Max:5 Marks)</p>'
        heading = ['Date','Event Name','Details of event','Class/ Talk or session Chair','International/National','Score claimed']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')
    elif part == "A7":
        main_heading = 'A7.1 week Industrial training/Professional Training,1 week refresher program, 1 week FDP attended or organized <p style="color:blue"> [Attended other than ICT mode- 2 Marks each, Attended ICT mode-1 marks each, Organized other than ICT mode- 3 Marks each, Organized ICT mode- 2 marks each].(If more than one coordinator then 3 or 2 marks equally divided between them)    (Max:5 Marks)</p>'
        heading = ['From Date','To date','Programme','Level','Duration','Role','Organized by','ICT mode/OTHER THAN ICT MODE','Score claimed']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')
    elif part == "A8":
        main_heading = "A8.Feedback Survey"
        heading = ['Course','Branch','Semester','Section','Subject','Student feedback']
        # if int(level) >= 1:
        #   if len(status) == 1:
        #       heading.append('Score Awarded')
        #   else:
        #       heading.append('Score Awarded')
        #       heading.append('score Reviewed')
    return {'main_heading':main_heading,'heading':heading}#HEADINGS


def get_cat1_form_data_new(emp_id, level, session, session_name):
    if int(level) > 1:
        level = 1

    final_data = {} 
    extra_filter = {}
    extra_filter1 = {}
    statuses = []
    category = 'cat1'
    final_data['main_heading'] = "CATEGORY -I (Maximum Marks: 100) (TEACHING, LEARNING & ACADEMIC RELATED ACTIVITIES)"
    #### NO. OF SUBPARTS IN CAT1 = 8 ####
    for i in range(1, 9):
        data = {}       
        data['heading'] = []
        if str('A' + str(i)) not in final_data:
            final_data[str('A' + str(i))] = {}

        statuses = []
        status = []
        if int(level) <= 1:
            status = list(FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level),session=session).exclude(status="DELETE").values('approval_status').order_by('approval_status'))
            if len(status) == 0:
                statuses.append({'status': "PENDING"})
            else:
                for s in status:
                    statuses.append({'status': s['approval_status']})
        else:
            if len(status) == 0:
                statuses.append({'status': "PENDING"})
        if i==1:
            data['heading'] = get_heading_of_cat1_new('A' + str(i), level, statuses)
            sub_category = str('A' + str(i))
            lectures = get_employee_subject_section_wise_lecture_plan_new(emp_id, session, session_name)
            qry = list(FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable"))
            if len(qry)>0:
                if int(level)>0:
                    if int(level)==1:
                        if len(statuses) == 1:
                            if "PENDING"  in str(statuses[0]['status']):
                                for d in qry[0]['data_sub_category']['data']:
                                    d['score_awarded']= d['score_claimed']
                        else:
                            if "REVIEW" == statuses[-1]['status']:
                                for d in qry[0]['data_sub_category']['data']:
                                    d['score_reviewed']= d['score_awarded']
                    data.update(qry[0]['data_sub_category'])
                else:
                    for d in qry[0]['data_sub_category']['data']:
                        if "score_awarded" in d:
                            d.pop("score_awarded")
                        if "score_reviewed" in d:
                            d.pop("score_reviewed")
                    if 'overall_score_awarded' in qry[0]['data_sub_category'].keys():
                        qry[0]['data_sub_category'].pop('overall_score_awarded')
                    if 'overall_score_reviewed' in qry[0]['data_sub_category'].keys():
                        qry[0]['data_sub_category'].pop('overall_score_reviewed')
                    data.update(qry[0]['data_sub_category'])
                final_data['A' + str(i)] = data
            else:
                add_per_rows = 0
                avg = 0
                for lec in lectures:
                    if lec['proposed']!=0:
                        lec['difference'] = lec['proposed']-lec['total']
                        if lec['total']<lec['proposed']:
                            lec['% of classes taken'] = round((lec['total']/lec['proposed'])*100,2)
                        else :
                            lec['% of classes taken'] = 100
                    else:
                        lec['proposed'] = "---"
                        lec['difference']="---"
                        lec['% of classes taken'] = 100
                    lec['score_claimed']=get_score_cat1_A1_new(lec['% of classes taken'])
                    if lec['score_claimed']==0:
                        percent_per_rows =0
                    add_per_rows = add_per_rows+lec['score_claimed']
                if len(lectures)>0:
                    avg = round(add_per_rows/len(lectures),2)
                data['data']=lectures
                data['overall_score']=avg
                final_data['A' + str(i)] = data
        if i ==2 :
            data['heading'] = get_heading_of_cat1_new('A' + str(i), level, statuses)
            sub_category = str('A' + str(i))
            attendance = get_overall_att_subject_section_wise_lecture_new(emp_id, session, session_name)
            qry = list(FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable"))
            if len(qry)>0:
                if int(level)>0:
                    data.update(qry[0]['data_sub_category'])
                    if int(level)==1:
                        if len(statuses) == 1:
                            if "PENDING" in statuses[0]['status']:
                                for d in qry[0]['data_sub_category']['data']:
                                    d['score_awarded']= d['score_claimed']
                        else:
                            if "REVIEW" == statuses[-1]['status']:
                                for d in qry[0]['data_sub_category']['data']:
                                    d['score_reviewed']= d['score_awarded']
                    data.update(qry[0]['data_sub_category'])
                else:
                    for d in qry[0]['data_sub_category']['data']:
                        if "score_awarded" in d:
                            d.pop("score_awarded")
                        if "score_reviewed" in d:
                            d.pop("score_reviewed")
                    if 'overall_score_awarded' in qry[0]['data_sub_category'].keys():
                        qry[0]['data_sub_category'].pop("overall_score_awarded")
                    if 'overall_score_reviewed' in qry[0]['data_sub_category'].keys():
                        qry[0]['data_sub_category'].pop('overall_score_reviewed')
                    data.update(qry[0]['data_sub_category'])
                final_data['A' + str(i)] = data
            else:
                add_per_rows = 0
                for att in attendance:
                    att['avg'] = 0
                    if(att['total_strength'])>0:
                        avg = round(att['total_present_in_lec']/att['total_strength']*100,2)
                        att['avg'] = avg
                        if avg >=90:
                            att['score_claimed'] = 5
                        elif avg<90 and avg>=85:
                            att['score_claimed']=4
                        elif avg<85 and avg>=80:
                            att['score_claimed']=3
                        elif avg<80 and avg>=75:
                            att['score_claimed']=2
                        elif avg<75 and avg>=70:
                            att['score_claimed']=1
                        else:
                            att['score_claimed']=0
                    else:
                        att['score_claimed']=0
                    add_per_rows = add_per_rows+att['score_claimed']
                    if int(level)==1:
                        att['score_awarded'] = att['score_claimed']
                avg_row_per = round(add_per_rows/len(attendance),2)
                data['data']=attendance
                data['overall_score']=avg_row_per
                data['overall_score_per'] = round((data['overall_score']/5)*100,2)
            final_data['A' + str(i)] = data
        if i==3:
            data['heading'] = get_heading_of_cat1_new('A' + str(i), level, statuses)
            sub_category = str('A' + str(i))
            qry = list(FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable"))
            if len(qry)>0:
                if int(level)>0:
                    if int(level)==1:
                        if len(statuses) == 1:
                            if "PENDING" in statuses[0]['status']:
                                for d in qry[0]['data_sub_category']['data']:
                                    d['score_awarded']= d['score_claimed']
                        else:
                            if "REVIEW" == statuses[-1]['status']:
                                for d in qry[0]['data_sub_category']['data']:
                                    d['score_reviewed']= d['score_awarded']
                    data.update(qry[0]['data_sub_category'])
                else:
                    for d in qry[0]['data_sub_category']['data']:
                        if "score_awarded" in d:
                            d.pop("score_awarded")
                        if "score_reviewed" in d:
                            d.pop("score_reviewed")
                    if 'overall_score_awarded' in qry[0]['data_sub_category'].keys():
                        qry[0]['data_sub_category'].pop("overall_score_awarded")
                    if 'overall_score_reviewed' in qry[0]['data_sub_category'].keys():
                        qry[0]['data_sub_category'].pop('overall_score_reviewed')
                    data.update(qry[0]['data_sub_category'])
                final_data['A' + str(i)] = data
            else:
                data['data'] = [{}]
                data['overall_score'] = 0
            final_data['A' + str(i)] = data
        if i==4:
            data['heading'] = get_heading_of_cat1_new('A' + str(i), level, statuses)
            sub_category = str('A' + str(i))
            qry = list(FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable"))
            if len(qry)>0:
                if int(level)>0:
                    if int(level)==1:
                        if len(statuses) == 1:
                            if "PENDING" in statuses[0]['status']:
                                for d in qry[0]['data_sub_category']['data']:
                                    d['score_awarded']= d['score_claimed']
                        else:
                            if "REVIEW" == statuses[-1]['status']:
                                for d in qry[0]['data_sub_category']['data']:
                                    d['score_reviewed']= d['score_awarded']
                    data.update(qry[0]['data_sub_category'])
                else:
                    for d in qry[0]['data_sub_category']['data']:
                        if "score_awarded" in d:
                            d.pop("score_awarded")
                        if "score_reviewed" in d:
                            d.pop("score_reviewed")
                    if 'overall_score_awarded' in qry[0]['data_sub_category'].keys():
                        qry[0]['data_sub_category'].pop("overall_score_awarded")
                    if 'overall_score_reviewed' in qry[0]['data_sub_category'].keys():
                        qry[0]['data_sub_category'].pop('overall_score_reviewed')
                    data.update(qry[0]['data_sub_category'])
                final_data['A' + str(i)] = data
            else:
                from_date = date(2019, 8, 1)
                to_date = date(2020, 7, 31)
                certificate = EmployeeCertification.objects.filter(emp_id=emp_id,issue_date__range=[from_date,to_date]).exclude(status="DELETE").values("course_name","certified_by","mooc_type__value","nptel_type__value","link")
                score_claimed = 0
                if len(certificate)>0:
                    for q in certificate:
                        if q['nptel_type__value'] is not None:
                            if "ELITE + GOLD" in q['nptel_type__value'].upper() :
                              q['score_claimed']=10
                              score_claimed = score_claimed+10
                            elif "ELITE + SILVER" in q['nptel_type__value'].upper():
                              q['score_claimed'] = 8
                              score_claimed = score_claimed+8
                            elif "ELITE" in q['nptel_type__value'].upper():
                              q['score_claimed'] = 7
                              score_claimed = score_claimed+7
                            else:
                              q['score_claimed'] = 5
                              score_claimed = score_claimed+5
                        else:
                            q['nptel_type__value'] ='---'
                            if  q['mooc_type__value'] is  None:
                                q['mooc_type__value'] = '---'
                            q['score_claimed'] = 5
                            score_claimed = score_claimed+5 
                    data['data'] = list(certificate)
                else:
                    data['data']=[]
                    row_data ={'nptel_type__value':'---',"score_claimed":'---','course_name':'---',"mooc_type__value":'---'}
                    data['data'].append(row_data)
                if len(certificate)>0:
                    data['overall_score'] = round(score_claimed/len(certificate),2)
                else:
                    data['overall_score'] =0
            final_data['A' + str(i)] = data
        # if i==5 or i==8:
        #   lectures_data = get_employee_subject_setion_wise_total_lecture_new(emp_id, session, session_name)
        #   lectures = lectures_data[0]
        #   subject_type = lectures_data[1]

        if i==5:
            data['heading'] = get_heading_of_cat1_new('A' + str(i), level, statuses)
            sub_category = str('A' + str(i))
            qry = list(FacAppAcadData.objects.filter(fac_app_id__emp_id=emp_id,fac_app_id__session=session).exclude(status=0).values('external_data','score_claimed'))
            if (len(qry)>0):
                if int(level)>0:
                    if int(level)==1:
                        if len(statuses) == 1:
                            if "PENDING" in statuses[0]['status']:
                                for d in qry[0]['external_data']['last_xyrs_data']:
                                    d['score_awarded']= d['score_claimed']
                                qry[0]['external_data']['heading_past_marks'].append('Score Awarded')
                        else:
                            if "REVIEWED" not in statuses[-1]['status'] and 'REVIEW' in statuses[-1]['status']: 
                                for d in qry[0]['external_data']['last_xyrs_data']:
                                    d['score_reviewed']= d['score_awarded']
                                qry[0]['external_data']['heading_past_marks'].append('Score Reviewed')

                else:
                    for d in qry[0]['external_data']['last_xyrs_data']:
                        if "score_awarded" in d:
                            d.pop("score_awarded")
                        if "score_reviewed" in d:
                            d.pop("score_reviewed")
                    if 'overall_score_awarded' in qry[0]['external_data'].keys():
                        qry[0]['external_data'].pop("overall_score_awarded")
                    if 'overall_score_reviewed' in qry[0]['external_data'].keys():
                        qry[0]['external_data'].pop("overall_score_reviewed")
                data.update(qry[0]['external_data'])
            else:
                lectures_data = get_employee_exclude_lab_subject_setion_wise_total_lecture_new(emp_id, session, session_name)
                lectures = lectures_data[0]
                subject_type = lectures_data[1]
                data['data']=[]
                for lec in lectures:
                    semester = int_to_Roman(int(lec['section__sem_id__sem']))
                    format_data = [lec['section__sem_id__dept__course__value'],lec['section__sem_id__dept__dept__value'], semester, lec['section__section']]
                    lec['data-format'] = get_data_in_faculty_form_format(format_data)
                    lec['university_marks'] = get_university_marks_subject_wise(lec)
                    data['data'].append(lec)
                marks_data = get_past_marks_details_new(emp_id, session, session_name,data['data'])
                data['last_xyrs_data']=marks_data[0]
                data['overall_score'] = 0
                data['heading_past_marks'] = ['Sno','Subject','Average Academic Year','Old/New','Past 5 years marks details','Score Claimed']
            final_data['A' + str(i)] = data
        if i==6:
            data['heading'] = get_heading_of_cat1_new('A' + str(i), level, statuses)
            sub_category = str('A' + str(i))
            qry = list(FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable"))
            if len(qry)>0:
                if int(level)>0:
                    if int(level)==1:
                        if len(statuses) == 1:
                            if "PENDING" in statuses[0]['status']:
                                for d in qry[0]['data_sub_category']['data']:
                                    if d['score_claimed'] =='---':
                                        d['score_awarded'] = 0
                                    else:
                                        d['score_awarded']= d['score_claimed']
                        else:
                            if "REVIEW" == statuses[-1]['status']:
                                for d in qry[0]['data_sub_category']['data']:
                                    d['score_reviewed']= d['score_awarded']
                    data.update(qry[0]['data_sub_category'])
                else:
                    for d in qry[0]['data_sub_category']['data']:
                        if "score_awarded" in d:
                            d.pop("score_awarded")
                        if "score_reviewed" in d:
                            d.pop("score_reviewed")
                    if 'overall_score_awarded' in qry[0]['data_sub_category'].keys():
                        qry[0]['data_sub_category'].pop("overall_score_awarded")
                    if 'overall_score_reviewed' in qry[0]['data_sub_category'].keys():
                        qry[0]['data_sub_category'].pop('overall_score_reviewed')
                    data.update(qry[0]['data_sub_category'])
                final_data['A' + str(i)] = data
            else:
                lec_achievement = GetAllAchievementEmployee(emp_id,"LECTURES AND TALKS",session)
                score_claimed = 0
                if len(lec_achievement)>0:
                    for ach in lec_achievement:
                        if 'INTERNATIONAL' in ach['type_of_event__value']:
                            score_claimed = score_claimed+5
                            ach['score_claimed'] = 5
                        elif 'NATIONAL' in ach['type_of_event__value']:
                            score_claimed = score_claimed+2.5
                            ach['score_claimed'] = 2.5
                        else:
                            ach['score_claimed'] = 0
                    if score_claimed>5:
                        score_claimed = 5
                    data['overall_score'] = round((score_claimed),2)
                    data['data'] = lec_achievement
                else:
                    data['data'] = []
                    row_data = get_null_values_for_achievement_new('LECTURES AND TALKS', level, statuses)
                    data['data'].append(row_data)
                    data['overall_score'] = 0

            final_data['A' + str(i)] = data
        if i==7:
            data['heading'] = get_heading_of_cat1_new('A' + str(i), level, statuses)
            sub_category = str('A' + str(i))
            qry = list(FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable"))
            if len(qry)>0:
                if int(level)>0:
                    if int(level)==1:
                        if len(statuses)== 1:
                            if "PENDING" in statuses[0]['status']:
                                for d in qry[0]['data_sub_category']['data']:
                                    if d['score_claimed'] =='---':
                                        d['score_awarded'] = 0
                                    else:
                                        d['score_awarded']= d['score_claimed']
                        else:
                            if "REVIEW" == statuses[-1]['status']:
                                for d in qry[0]['data_sub_category']['data']:
                                    d['score_reviewed']= d['score_awarded']
                    data.update(qry[0]['data_sub_category'])            
                else:
                    for d in qry[0]['data_sub_category']['data']:
                        if "score_awarded" in d:
                            d.pop("score_awarded")
                        if "score_reviewed" in d:
                            d.pop("score_reviewed")
                    if 'overall_score_awarded' in qry[0]['data_sub_category'].keys():
                        qry[0]['data_sub_category'].pop("overall_score_awarded")
                    if 'overall_score_reviewed' in qry[0]['data_sub_category'].keys():
                        qry[0]['data_sub_category'].pop('overall_score_reviewed')
                    data.update(qry[0]['data_sub_category'])
                final_data['A' + str(i)] = data
            else:
                train_achievement = GetAllAchievementEmployee(emp_id,"TRAINING AND DEVELOPMENT PROGRAM",session)
                score_claimed =0
                if len(train_achievement)>0:
                    # print(train_achievement)
                    for tr_ach in train_achievement:
                        # if 'FDP' in tr_ach['category__value']:
                        week_check_days =(tr_ach['to_date']-tr_ach['from_date'])
                        tr_ach['days'] =  get_period(week_check_days.days)
                        # if 'FDP' in tr_ach['category__value']:
                        if int(week_check_days.days+1)>=5:
                            if 'ATTENDED' in tr_ach['role__value']:
                                if  tr_ach['training_sub_type__value'] is not None:
                                    if 'OTHER THAN ICT MODE' in tr_ach['training_sub_type__value']:
                                        score_claimed = score_claimed+2
                                        tr_ach['score_claimed'] = 2
                                    elif 'ICT MODE' in tr_ach['training_sub_type__value']:
                                        score_claimed = score_claimed+1
                                        tr_ach['score_claimed'] = 1
                                else:
                                    tr_ach['score_claimed'] = 0
                                    tr_ach['training_sub_type__value'] = '---'
                            elif 'ORGANIZED' in tr_ach['role__value']:
                                if  tr_ach['training_sub_type__value'] is not None:
                                    if 'ICT MODE' in tr_ach['training_sub_type__value']:
                                        score_claimed = score_claimed+2
                                        tr_ach['score_claimed'] = 2
                                    elif 'OTHER THAN ICT MODE' in tr_ach['training_sub_type__value']:
                                        score_claimed = score_claimed+3
                                        tr_ach['score_claimed'] = 3
                                else:
                                    tr_ach['score_claimed'] = 0
                                    tr_ach['training_sub_type__value'] = '---'
                            else :
                                tr_ach['score_claimed'] = 0
                                tr_ach['training_sub_type__value'] = '---'
                        else:
                            tr_ach['score_claimed'] = 0
                    if score_claimed>5:
                        score_claimed = 5
                    data['overall_score'] = round((score_claimed),2)
                    data['data'] = train_achievement
                else:
                    data['data']=[]
                    row_data = get_null_values_for_achievement_new('TRAINING AND DEVELOPMENT PROGRAM', level, statuses)
                    data['data'].append(row_data)
                    data['overall_score'] = 0
            final_data['A' + str(i)] = data
        if i == 8:
            lectures_data = get_employee_subject_setion_wise_total_lecture_new(emp_id, session, session_name)
            lectures = lectures_data[0]
            subject_type = lectures_data[1]
            data['heading'] = get_heading_of_cat1_new('A' + str(i), level, statuses)
            sub_category = str('A' + str(i))
            qry = list(FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable"))
            if len(qry)>0:
                if int(level)>0:
                    if int(level)==1:
                        if len(statuses)==1:
                            if "PENDING" in statuses[0]['status']:
                                for d in qry[0]['data_sub_category']['data']:
                                    d['score_awarded']= d['score_claimed']
                        else:
                            if "REVIEW" == statuses[-1]['status']:
                                for d in qry[0]['data_sub_category']['data']:
                                    d['score_reviewed']= d['score_awarded']
                    data.update(qry[0]['data_sub_category'])
                else:
                    for d in qry[0]['data_sub_category']['data']:
                        if "score_awarded" in d:
                            d.pop("score_awarded")
                        if "score_reviewed" in d:
                            d.pop("score_reviewed")
                    if 'overall_score_awarded' in qry[0]['data_sub_category'].keys():
                        qry[0]['data_sub_category'].pop("overall_score_awarded")
                    if 'overall_score_reviewed' in qry[0]['data_sub_category'].keys():
                        qry[0]['data_sub_category'].pop('overall_score_reviewed')
                    data.update(qry[0]['data_sub_category'])
                final_data['A' + str(i)] = data
            else:
                data['data']=[]
                Sessions = []
                Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'o')
                Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'e')
                for ses in Sessions:
                    temp_data = []
                    # data_value =[]
                    feedback = faculty_feedback_details([emp_id], ses, subject_type)
                    if len(feedback) > 0:
                        # temp_emp_list=[]
                        for f_back in feedback:
                            row_data = {'course':f_back['course_sem_section'],'branch': f_back['branch'], 'semester': f_back['sem'], 'section': f_back['section'], 'subject': f_back['subject'], 'overall_avg': f_back['TOTAL'], 'student_feedback': f_back['TOTAL'], 'score_claimed': 0}
                            data['data'].append(row_data)
                            temp_data.append(row_data)
                        score=get_total_of_cat1_new(temp_data, 'A' + str(i), level, statuses)
                        data['f' + str(ses[-1])] =score['overall_feedback']
                        data['f' + str(ses[-1]) + 'score'] = score['total']

                if 'fo' not in data and 'fe' in data:
                    data['final_feedback'] = round(data['fe'], 2)

                elif 'fe' not in data and 'fo' in data:
                    data['final_feedback'] = round(data['fo'], 2)
                elif 'fe' not in data and 'fe' not in data:
                    data['final_feedback'] = round(0, 2)
                else:
                    data['final_feedback'] = round(((data['fo'] + data['fe']) / 2), 2)

                data['final_total'] = 0

                if data['final_feedback'] != None and data['final_feedback'] > 0:
                    if data['final_feedback'] >= 8.4:
                        data['overall_score'] = 30
                    elif data['final_feedback'] >= 6.5 and data['final_feedback'] < 8.4:
                        difference = data['final_feedback'] - 6.4
                        data['overall_score'] = round((difference/0.1) *1.5, 2)
                    else:
                        data['overall_score'] = 0
            final_data['A' + str(i)] = data

        if int(level)==1:
            if len(statuses) == 1:
                if "PENDING" in statuses[0]['status']:
                    data['overall_score_awarded']= data['overall_score']
            else:
                if "REVIEW" == statuses[-1]['status']:
                    data['overall_score_reviewed']= data['overall_score_awarded']


    return final_data#MAIN FUNCTION CAT-1



def get_total_of_cat1_new(data, part, level, status):
    total_data = 0
    length = len(data)
    part = str(part)
    if 'A8' in part:
        total_data = {'overall_feedback': 0, 'total': 0}
        for d in data:
            total_data['overall_feedback'] = total_data['overall_feedback'] + d['student_feedback']

        if int(length) > 0:
            total_data['overall_feedback'] = round(total_data['overall_feedback'] / length, 2)
            if float(total_data['overall_feedback']) >= 8.4:
                total_data['total'] = 30
            elif float(total_data['overall_feedback']) >= 6.5 and float(total_data['overall_feedback']) < 8.4:
                difference = total_data['overall_feedback'] - 6.4
                total_data['total'] = round(float(difference/0.1) *1.5, 2)
            if int(level) >= 1:
                if len(status) == 1:
                    total_data['score_awarded'] = total_data['total']
                else:
                    total_data['score_awarded'] = total_data['total']
                    total_data['score_reviewed'] = total_data['total']
    return total_data

def get_past_marks_details_new(emp_id, session, session_name,data1):
    year = get_last_x_year_ses(session_name,5)
    Sessions=[]
    Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'o')
    Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'e')
    data_list =[]
    final_sc=0
    l =0
    for ses in Sessions:
        Attendance = generate_session_table_name('Attendance_', ses)
        qry = Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY").exclude(subject_id__max_university_marks=0).exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").exclude(subject_id__subject_type__value="LAB").values( 'subject_id','subject_id__sub_name','subject_id__sub_alpha_code','subject_id__sub_num_code','section__sem_id','section__sem_id__dept').distinct()
        for q in qry:
            l=l+1
            data={}
            year_li =[]
            total_avg_curr = 0
            score_claimed =0
            flag1=0
            for f in data1:
                if f['subject_id'] == q['subject_id']:
                    flag1 = flag1+1
                    total_avg_curr = total_avg_curr + f['university_marks']['average_external_per']
            if flag1>0:
                total_avg_curr = round(total_avg_curr/flag1,2)
            flag = 0
            for y,s in enumerate(year,1):
                data_li ={}
                data_dict={"mo":None,"me":None}
                for i in range(2):
                    try:
                        SubjectInfo = generate_session_table_name('SubjectInfo_',s[i])
                        StudentUniversityMarks = generate_session_table_name('StudentUniversityMarks_', s[i])
                        ses_sub_id = list(SubjectInfo.objects.filter(sub_name=q['subject_id__sub_name'],sub_alpha_code=q['subject_id__sub_alpha_code'],sub_num_code=q['subject_id__sub_num_code'],sem_id__dept=q['section__sem_id__dept']).exclude(max_university_marks=0).exclude(status="DELETE").values('id'))
                        univ_marks = list(StudentUniversityMarks.objects.filter( subject_id=ses_sub_id[0]['id']).values_list('uniq_id', flat=True).exclude(subject_id__status="DELETE").values('subject_id', 'subject_id__max_ct_marks', 'subject_id__max_ta_marks', 'subject_id__max_att_marks', 'subject_id__max_university_marks', 'external_marks', 'internal_marks', 'back_marks', 'uniq_id').order_by('uniq_id'))
                        if(len(univ_marks)>0) and 'e' in s[i]:
                            data_dict['me'] = get_external_exam_average_per_new(univ_marks)
                        elif len(univ_marks)>0 and 'o' in s[i]:
                            data_dict['mo'] = get_external_exam_average_per_new(univ_marks)
                    except:
                        pass
                if  data_dict['mo'] is not None and data_dict['me'] is None:
                    data_li['year']="20"+str(s[i][:2])+"-"+"20"+str(s[i][2:-1])
                    data_li['marks']  = data_dict['mo']
                    data_li['mark_0'] = False
                    flag = flag+1
                    score_claimed = score_claimed + data_dict['mo']
                elif  data_dict['me'] is not None and data_dict['mo'] is None:
                    data_li['year']="20"+str(s[i][:2])+"-"+"20"+str(s[i][2:-1])
                    data_li['marks']  = data_dict['me']
                    data_li['mark_0'] = False
                    score_claimed = score_claimed + data_dict['me']
                    flag = flag+1
                elif  data_dict['mo'] is  None and data_dict['me'] is None:
                    data_li['year']="20"+str(s[i][:2])+"-"+"20"+str(s[i][2:-1])
                    data_li['marks']  = 0
                    data_li['mark_0'] = True
                    score_claimed = score_claimed + 0
                else:
                    data_li['year']=s[i][:-1]
                    data_li['marks'] = round((data_dict['mo']+data_dict['me'])/2,2)
                    data_li['mark_0'] = False
                    score_claimed = score_claimed+ round((data_dict['mo']+data_dict['me'])/2,2)
                    flag = flag+1
                year_li.append(data_li)
            if flag>0:
                score_claimed = round(score_claimed/flag,2)
            
            # if total_avg_curr>=score_claimed:
            #   data['score_claimed'] = 30
            #   final_sc = final_sc+data['score_claimed']
            # elif score_claimed - total_avg_curr <=10:
            #   data['score_claimed'] =round(30 - (3*(score_claimed-total_avg_curr)),2)
            #   final_sc = final_sc+data['score_claimed']
            # elif score_claimed - total_avg_curr>10:
            #   data['score_claimed'] = 0
            #   final_sc = final_sc+data['score_claimed']
            data['score_claimed']=0
            data['sub']= q['subject_id__sub_name']+ '(' + str(q['subject_id__sub_alpha_code']) + ' - ' + str(q['subject_id__sub_num_code']) + ')'
            data['old']=year_li
            data['y_value'] = total_avg_curr
            data['A5_score_claimed'] = 0
            data['new']=[{}]
            data_list.append(data)
    if l>0:
        final_sc = round(final_sc/(l),2)
    else:
        final_sc = 0
    return [data_list,final_sc]#LAST 5 YEARS MARKS DATA
##################################################################################CAT-1-END###########################################################


#################################################################################CAT -3############################################################
def get_heading_of_cat3_new(part, level, status):
    part = str(part)
    heading = []
    main_heading = 'A(i).Extension, Co-curricular, Field based activities, Contribution to corporate life, management of the Institution and Professional Development Activities <p style="color:blue">(* All activities during Academic Year)</p>'
    if part == "A1":
        heading = ['Departmental Activities (Max:20 Marks) (Max: 3 Marks/ semester/ activity for Mentor/Class Coordinator or Lab IC, Time Table IC, Consultancy, etc), (2 Marks per event for Organizing event at departmental level), (1 Mark per event to be divided between all co-coordinators)','From date','To date','Description','Score claimed']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')
    elif part == "A2":
        main_heading = 'A(ii)Monthly/on occurrence uploading of data as individual and Coordinator on KIET ERP <p style="color:blue">(Max:3 Marks)</p>'
        heading = ['Monthly/on occurrence uploading of data as individual and Coordinator on KIET ERP','Score claimed']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')
    elif part =='A3':
        main_heading = 'A(iii).Publicity of different events on social media on regular basis <p style="color:blue">(Max:2 Marks)</p>'
        heading = ['Publicity of different events on social media on regular basis (Max:2 Marks)','Score claimed']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')
    elif part == "A4":
        main_heading = 'A(iv).Institute Activity <p style="color:blue">(Max: 15 Marks) (Max: 10 Marks/semester/activity for Chief Proctor/Additional HoD/Associate Dean (SW) / Assistant Dean (A)/ IQAC Coordinator/Chief Rector/Digital/NAAC/NBA Coordinator, etc),(5 marks per activity-Rector/Proctor)(3 Marks per activity for coordinator at institute level),(2 mark per event to be divided between all co-coordinators)</p>'
        heading = ['Institute Activity (Max: 15 Marks) (Max: 10 Marks/semester/activity for Chief Proctor/Additional HoD/Associate Dean (SW) / Assistant Dean (A)/ IQAC Coordinator/Chief Rector/Digital/NAAC/NBA Coordinator, etc),(5 marks per activity-Rector/Proctor)(3 Marks per activity for coordinator at institute level),(2 mark per event to be divided between all co-coordinators)','From date','To date','Description','Score claimed']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')

    return {"main_heading":main_heading,"heading":heading}



def get_cat3_form_data_new(emp_id, level, session, session_name):
    ### SCORE CLAIMED IS INPUT FIELD ###

    if int(level) > 1:
        level = 1

    final_data = {}
    extra_filter = {}
    statuses = []
    category = 'cat3'
    final_data['main_heading'] = "CATEGORY – III (Maximum Marks: 50)CO-CURRICULAR, EXTENSION, PROFESSIONAL DEVELOPMENT RELATED ACTIVITIES"
    for i in range(1, 5):
        data = {}
        data['data'] = []
        data['heading'] = []
        sub_category = str('A' + str(i))
        statuses = []
        status = []
        if int(level) <= 1:
            status = list(FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level),session=session).exclude(status="DELETE").values('approval_status').order_by('approval_status'))
            if len(status) == 0:
                statuses.append({'status': "PENDING"})
            else:
                for s in status:
                    statuses.append({'status': s['approval_status']})
        if str('A' + str(i)) not in final_data:
            final_data[str('A' + str(i))] = {}
        if i==1:
            data['heading'] = get_heading_of_cat3_new('A' + str(i), level, statuses)
            qry1 = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
            if len(qry1)>0:
                if int(level)>0:
                    if int(level)==1:
                        if len(statuses)==1:
                            if "PENDING" in statuses[0]['status']:
                                for d in qry1[0]['data_sub_category']['data']:
                                    if d['score_claimed'] =='---':
                                        d['score_awarded'] = 0
                                    else:
                                        d['score_awarded']= d['score_claimed']
                        else:
                            if "REVIEW" == statuses[-1]['status']:
                                for d in qry1[0]['data_sub_category']['data']:
                                    d['score_reviewed']= d['score_awarded']
                    data.update(qry1[0]['data_sub_category'])
                else:
                    for d in qry1[0]['data_sub_category']['data']:
                        if "score_awarded" in d:
                            d.pop("score_awarded")
                        if "score_reviewed" in d:
                            d.pop("score_reviewed")
                    if 'overall_score_awarded' in qry1[0]['data_sub_category'].keys():
                        qry1[0]['data_sub_category'].pop("overall_score_awarded")
                    if 'overall_score_reviewed' in qry1[0]['data_sub_category'].keys():
                        qry1[0]['data_sub_category'].pop('overall_score_reviewed')
                    data.update(qry1[0]['data_sub_category'])
            else:
                score_claimed = 0
                dept_activity = GetAllActivitiesEmployee(emp_id,['DEPARTMENTAL'])
                if len(dept_activity)>0:
                    for d in dept_activity:
                        if emp_id in d['coord_detail__act_main_emp_id'] and  d['coord_detail__act_co_emp_id'] == None or len(d['coord_detail__act_co_emp_id'])==0:
                            d['score_claimed'] = round(d['marks'],2)
                            score_claimed = score_claimed+d['score_claimed']
                        elif emp_id not in d['coord_detail__act_main_emp_id'] and emp_id in d['coord_detail__act_co_emp_id']:
                            d['score_claimed'] = round(((1/3)*d['marks']),2)
                            score_claimed = score_claimed+d['score_claimed']
                        elif emp_id in d['coord_detail__act_main_emp_id'] and emp_id not in d['coord_detail__act_co_emp_id']:
                            d['score_claimed'] = round(((2/3)*d['marks']),2)
                            score_claimed = score_claimed+d['score_claimed']
                        else:
                            d['score_claimed']=0
                            score_claimed = score_claimed+d['score_claimed']
                else:
                    dept_activity.append({"score_claimed":'---','act_type__value':'---','act_level__value':'---','act_sub_type__value':'---','score_awarded':0})
                data['data'] = dept_activity
                if score_claimed> 20:
                    score_claimed = 20
                data['overall_score'] = score_claimed
        if i==2:
            data['heading'] = get_heading_of_cat3_new('A' + str(i), level, statuses)
            qry1 = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
            if len(qry1)>0:
                if int(level)>0:
                    if int(level)==1:
                        if len(statuses)==1:
                            if "PENDING" in statuses[0]['status']:
                                for d in qry1[0]['data_sub_category']['data']:
                                    d['score_awarded']= d['score_claimed']
                        else:
                            if "REVIEW" == statuses[-1]['status']:
                                for d in qry1[0]['data_sub_category']['data']:
                                    d['score_reviewed']= d['score_awarded']
                    data.update(qry1[0]['data_sub_category'])
                else:
                    for d in qry1[0]['data_sub_category']['data']:
                        if "score_awarded" in d:
                            d.pop("score_awarded")
                        if "score_reviewed" in d:
                            d.pop("score_reviewed")
                    if 'overall_score_awarded' in qry1[0]['data_sub_category'].keys():
                        qry1[0]['data_sub_category'].pop("overall_score_awarded")
                    if 'overall_score_reviewed' in qry1[0]['data_sub_category'].keys():
                        qry1[0]['data_sub_category'].pop('overall_score_reviewed')
                    data.update(qry1[0]['data_sub_category'])
            else:
                data['data'] = [{}]
                data['overall_score'] = 0       
        if i==3:
            data['heading'] = get_heading_of_cat3_new('A' + str(i), level, statuses)
            qry1 = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
            if len(qry1)>0:
                if int(level)>0:
                    if int(level)==1:
                        if len(statuses)==1:
                            if "PENDING" in statuses[0]['status']:
                                for d in qry1[0]['data_sub_category']['data']:
                                    d['score_awarded']= d['score_claimed']
                        else:
                            if "REVIEW" == statuses[-1]['status']:
                                for d in qry1[0]['data_sub_category']['data']:
                                    d['score_reviewed']= d['score_awarded']
                    data.update(qry1[0]['data_sub_category'])
                else:
                    for d in qry1[0]['data_sub_category']['data']:
                        if "score_awarded" in d:
                            d.pop("score_awarded")
                        if "score_reviewed" in d:
                            d.pop("score_reviewed")
                    if 'overall_score_awarded' in qry1[0]['data_sub_category'].keys():
                        qry1[0]['data_sub_category'].pop("overall_score_awarded")
                    if 'overall_score_reviewed' in qry1[0]['data_sub_category'].keys():
                        qry1[0]['data_sub_category'].pop('overall_score_reviewed')
                    data.update(qry1[0]['data_sub_category'])
            else:
                data['data'] = [{}]
                data['overall_score'] = 0
        if i==4:
            data['heading'] = get_heading_of_cat3_new('A' + str(i), level, statuses)
            qry1 = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
            if len(qry1)>0:
                if int(level)>0:
                    if int(level)==1:
                        if len(statuses)==1:
                            if "PENDING" in statuses[0]['status']:
                                for d in qry1[0]['data_sub_category']['data']:
                                    if d['score_claimed'] =='---':
                                        d['score_awarded'] = 0
                                    else:
                                        d['score_awarded']= d['score_claimed']
                        else:
                            if "REVIEW" == statuses[-1]['status']:
                                for d in qry1[0]['data_sub_category']['data']:
                                    d['score_reviewed']= d['score_awarded']
                    data.update(qry1[0]['data_sub_category'])
                else:
                    for d in qry1[0]['data_sub_category']['data']:
                        if "score_awarded" in d:
                            d.pop("score_awarded")
                        if "score_reviewed" in d:
                            d.pop("score_reviewed")
                    if 'overall_score_awarded' in qry1[0]['data_sub_category'].keys():
                        qry1[0]['data_sub_category'].pop("overall_score_awarded")
                    if 'overall_score_reviewed' in qry1[0]['data_sub_category'].keys():
                        qry1[0]['data_sub_category'].pop('overall_score_reviewed')
                    data.update(qry1[0]['data_sub_category'])
            else:
                score_claimed = 0
                inst_activity =GetAllActivitiesEmployee(emp_id,['INSTITUTIONAL'])
                if len(inst_activity)>0:
                    for d in inst_activity:
                        if emp_id in d['coord_detail__act_main_emp_id'] and d['coord_detail__act_co_emp_id'] == None or len(d['coord_detail__act_co_emp_id'])==0 :
                            d['score_claimed'] = round(int(d['marks']),2)
                            score_claimed = score_claimed+d['score_claimed']
                        elif emp_id not in d['coord_detail__act_main_emp_id'] and emp_id in d['coord_detail__act_co_emp_id']:
                            d['score_claimed'] = round((1/3)*int(d['marks']),2)
                            score_claimed = score_claimed+d['score_claimed']
                        elif emp_id in d['coord_detail__act_main_emp_id'] and emp_id not in d['coord_detail__act_co_emp_id']:
                            d['score_claimed'] = round((2/3)*int(d['marks']),2)
                            score_claimed = score_claimed+d['score_claimed']
                        else:
                            d['score_claimed']=0
                            score_claimed = score_claimed+d['score_claimed']
                else:
                    inst_activity.append({"score_claimed":'---','act_type__value':'---','act_level__value':'---','act_sub_type__value':'---','score_awarded':0})
                data['data'] = inst_activity
                if score_claimed>15:
                    score_claimed = 15 
                data['overall_score'] = score_claimed
        if int(level)==1:
            if len(statuses) == 1:
                if "PENDING" in statuses[0]['status']:
                    data['overall_score_awarded']= data['overall_score']
            else:
                if "REVIEW" == statuses[-1]['status']:
                    data['overall_score_reviewed']= data['overall_score_awarded']

        final_data['A' + str(i)] = data
        if int(level)>=1:
            qry = list(FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category="A5").exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable"))
            if len(qry)>0:
                final_data['A5'] = qry[0]['data_sub_category']


    return final_data

######################################################################CAT-3 -END###############################################################



######################################################################CAT-2######################################################################
def get_heading_of_cat2_new(part, level, status):
    part = str(part)
    heading = []
    if part == "A1":
        main_heading = ['A1.Papers Published in Indexed journals- SCI/SCI-E/SSCI/ESCI/SCOPUS for faculty members having experience more than 3 years.Papers Published in UGC listed Journals for faculty members having experience less than 3 years.<p style="color:blue">(15 Marks for single author, 9 Marks for 1st author and Supervisor and 6 Marks for others and these will be augmented as “SCI/SCI-E/SSCI/ESCI/SCOPUS Impact Factor/Cite ScoreTM” less than 0.499 – 4 Marks, IF between 0.5 & 0.749 – 6 Marks, IF above 0.75 – 8 Marks, UGS listed Journals -2 Marks / each Journal)</p>']
        heading = ['S.No.','Date','Full Journal paper(In IEEE reference format)','ISSN/ ISBNNo.','Sub_category','Author','Impact factor/ CiteScoreTM (if any)','Score Claimed']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')
    elif part == "A3":
        main_heading = ['B.Books published as author or as editor or Articles/Chapters or Monographs published in Books <p style="color:blue">(International publisher – 20 Marks/book & 5 Marks/chapter or Monographs in edited book, National – 10 Marks/book & 2 Marks/chapter or Monographs, local publisher-5 Marks)</p> [60% for I Author & 40% will be divided among the co-authors].']
        heading = ['S.No.','Date','Books Published/ Articles/Chapters published in Books as single author (In IEEE reference format)','ISSN/ ISBNNo.','International/National/Regional','Role','Author','Published For','Score Claimed']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')

    elif part == "A2":
        main_heading = ['A2.Full Papers published in Conference Proceedings/ Papers presented in Conferences, Seminars, Workshops, Symposia (conference in association with IEEE/ Springer/  Elsevier/ ACM/ Wiley/ IPC or organized by reputed Institutions (IIT/IISc/NIT/IIIT/JNU/Central Universities) will be considered as International otherwise will be considered as National. <p style="color:blue">([Int.Conf. 10 Marks for single author, 6 Marks for 1st author & Supervisor and 4 Marks for others], [Nat Conf 7.5 Marks for single author, 4.5 Marks for 1st author & Supervisor and 3.5 Marks for others])</p>']
        heading = ['S.No.','Type of Activity','Date','Full Papers in Conference proceedings.(In IEEE reference format)','ISSN/ ISBNNo.','Details  of Conference International/ National/Regional','Author','Score Claimed']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')
    elif part == "A4":
        main_heading = ['C(i) Ongoing /Completed Research projects and consultancies <p style="color:blue">(Projects>30 Lakhs – 20 Marks, between 5-30 Lakhs – 15 Marks, between 50,000 – 5 Lakhs – 10 Marks)</p> – [60% for PI & 40% marks will be divided among the CO-PI].']
        heading = ['S.No.','Date','Title','Agency','Period','Principal Investigator','Co-Principal Investigators','Grant/ Amount in (Rs Lakhs)','Score Claimed']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')
    elif part == "A5":
        main_heading = ['C(ii) Completed Research outcomes: Quality and Outcomes: <p style="color:blue"> (At National level output/Patent-25 Marks (if granted) & 20 Marks (if published) and at International level output/Patent-40 Marks (if granted) & 30 Marks (if published)</p> – [60% Marks for main applicants and 40% marks will be divided among remaining Co Applicants].']
        heading = ['S.No.','Title','Agency','Date','Main Applicant','Co- Applicant','Patent Level','Filed, Published & Granted','Score Claimed']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')
    elif part == "A6":
        main_heading = ['C(iii) Completed Research outcomes: Design/Industrial Design :<p style="color:blue"> (At National level Design / Industrial Design- 20 Marks(if granted) & 15 Marks (if published) and at International level Design/Industrial Design -    30 Marks(if granted) & 20 Marks(if published)</p> – [60% Marks for main applicants and 40% marks will be divided among remaining Co Applicants].']
        heading = ['S.No.','Title','Agency','Date','Main Applicant','Co- Applicant','Design Level','Filed, Published & Granted','Score Claimed']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')
    elif part == "A7":
        main_heading = ['D. Research Guidance']
        heading = ['S.No.','Date','Type of University','Guidance','Degree awarded','Score Claimed']
        if int(level) >= 1:
            if len(status) == 1:
                heading.append('Score Awarded')
            else:
                heading.append('Score Awarded')
                heading.append('score Reviewed')
    return {'main_heading':main_heading,'heading':heading}



def get_cat2_form_data_new(emp_id,level,session,session_name):
    #SCORE CLAIMED#
    if int(level) > 1:
        level = 1

    final_data = {}
    extra_filter = {}
    final_data['main_heading'] = "CATEGORY – II (Maximum Marks: 50) (RESEARCH & ACADEMIC CONTRIBUTIONS)"
    statuses = []
    category = 'cat2'
    for i in range(1, 8):
        data = {}
        data['data'] = []
        data['heading'] = []
        sub_category = str('A' + str(i))
        if str('A' + str(i)) not in final_data:
            final_data[str('A' + str(i))] = {}

        statuses = []
        status = []
        if int(level) <= 1:
            status = list(FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level),session=session).exclude(status="DELETE").values('approval_status').order_by('approval_status'))
            if len(status) == 0:
                statuses.append({'status': "PENDING"})
            else:
                for s in status:
                    statuses.append({'status': s['approval_status']})
        ### SUBPARTS IN CAT3 ARE PARTWISE ###
        if i == 1:
            ach_type = 'RESEARCH PAPER IN JOURNAL'
        if i == 2:
            ach_type = 'RESEARCH PAPER IN CONFERENCE'
        if i == 3:
            ach_type = 'BOOKS'
        if i == 4:
            ach_type = 'PROJECTS/CONSULTANCY'
        if i == 5:
            ach_type ='PATENT'
        if i == 6:
            ach_type ='DESIGN'
        if i == 7:
            ach_type = 'RESEARCH GUIDANCE / PROJECT GUIDANCE'
        data['heading'] = get_heading_of_cat2_new('A' + str(i), level, statuses)
        qry = GetAllAchievementEmployee(emp_id,ach_type,session)
        
        if len(qry) > 0:
            if 'BOOKS' in ach_type:
                qry1 = list(FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable"))
                if len(qry1)>0:
                    if int(level)>0:
                        if int(level)==1:
                            if len(statuses)==1:
                                if "PENDING" in statuses[0]['status']:
                                    for d in qry1[0]['data_sub_category']['data']:
                                        d['score_awarded']= d['score_claimed']
                            else:
                                if "REVIEW" == statuses[-1]['status']:
                                    for d in qry1[0]['data_sub_category']['data']:
                                        d['score_reviewed']= d['score_awarded']
                        data.update(qry1[0]['data_sub_category'])
                    else:
                        for d in qry1[0]['data_sub_category']['data']:
                            if "score_awarded" in d:
                                d.pop("score_awarded")
                            if "score_reviewed" in d:
                                d.pop("score_reviewed")
                        if 'overall_score_awarded' in qry1[0]['data_sub_category'].keys():
                            qry1[0]['data_sub_category'].pop("overall_score_awarded")
                        if 'overall_score_reviewed' in qry1[0]['data_sub_category'].keys():
                            qry1[0]['data_sub_category'].pop('overall_score_reviewed')
                        data.update(qry1[0]['data_sub_category'])
                else:
                    data1 = get_cat2_score_claimed_new(qry,str('A' + str(i)),emp_id)
                    data['data'] = data1[0]
                    data['overall_score'] = round((data1[1]),2)
                final_data[str('A' + str(i))] = data
            elif 'PROJECTS/CONSULTANCY' in ach_type:
                qry1 = list(FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable"))
                if len(qry1)>0:
                    if int(level)>0:
                        if int(level)==1:
                            if len(statuses)==1:
                                if "PENDING" in statuses[0]['status']:
                                    for d in qry1[0]['data_sub_category']['data']:
                                        d['score_awarded']= d['score_claimed']
                            else:
                                if "REVIEW" == statuses[-1]['status']:
                                    for d in qry1[0]['data_sub_category']['data']:
                                        d['score_reviewed']= d['score_awarded']
                        data.update(qry1[0]['data_sub_category'])
                    else:
                        for d in qry1[0]['data_sub_category']['data']:
                            if "score_awarded" in d:
                                d.pop("score_awarded")
                            if "score_reviewed" in d:
                                d.pop("score_reviewed")
                        if 'overall_score_awarded' in qry1[0]['data_sub_category'].keys():
                            qry1[0]['data_sub_category'].pop("overall_score_awarded")
                        if 'overall_score_reviewed' in qry1[0]['data_sub_category'].keys():
                            qry1[0]['data_sub_category'].pop('overall_score_reviewed')
                        data.update(qry1[0]['data_sub_category'])
                else:
                    data1 = get_cat2_score_claimed_new(qry,str('A' + str(i)),emp_id)
                    data['data'] = data1[0]
                    data['overall_score'] = round((data1[1]),2)
                final_data[str('A' + str(i))] = data

            elif 'PATENT' in ach_type:
                qry1 = list(FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable"))
                if len(qry1)>0:
                    if int(level)>0:
                        if int(level)==1:
                            if len(statuses)==1:
                                if "PENDING" in statuses[0]['status']:
                                    for d in qry1[0]['data_sub_category']['data']:  
                                        d['score_awarded']= d['score_claimed']
                            else:
                                if "REVIEW" == statuses[-1]['status']:
                                    for d in qry1[0]['data_sub_category']['data']:
                                        d['score_reviewed']= d['score_awarded']
                        data.update(qry1[0]['data_sub_category'])
                    else:
                        for d in qry1[0]['data_sub_category']['data']:
                            if "score_awarded" in d:
                                d.pop("score_awarded")
                            if "score_reviewed" in d:
                                d.pop("score_reviewed")
                        if 'overall_score_awarded' in qry1[0]['data_sub_category'].keys():
                            qry1[0]['data_sub_category'].pop("overall_score_awarded")
                        if 'overall_score_reviewed' in qry1[0]['data_sub_category'].keys():
                            qry1[0]['data_sub_category'].pop('overall_score_reviewed')
                        data.update(qry1[0]['data_sub_category'])
                else:
                    data1 = get_cat2_score_claimed_new(qry,str('A' + str(i)),emp_id)
                    data['data'] = data1[0]
                    data['overall_score'] = round((data1[1]),2)
                final_data[str('A' + str(i))] = data
            elif 'RESEARCH PAPER IN JOURNAL' in ach_type:
                sub_cat = ['SCI','SCI-E','SSCI','ESCI','SCOPOUS']
                qry1 = list(FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable"))
                if len(qry1)>0:
                    if int(level)>0:
                        if int(level)==1:
                            if len(statuses)==1:
                                if "PENDING" in statuses[0]['status']:
                                    for d in qry1[0]['data_sub_category']['data']:  
                                        d['score_awarded']= d['score_claimed']
                            else:
                                if "REVIEW" == statuses[-1]['status']:
                                    for d in qry1[0]['data_sub_category']['data']:
                                        d['score_reviewed']= d['score_awarded']
                        data.update(qry1[0]['data_sub_category'])
                    else:
                        for d in qry1[0]['data_sub_category']['data']:
                            if "score_awarded" in d:
                                d.pop("score_awarded")
                            if "score_reviewed" in d:
                                d.pop("score_reviewed")
                        if 'overall_score_awarded' in qry1[0]['data_sub_category'].keys():
                            qry1[0]['data_sub_category'].pop("overall_score_awarded")
                        if 'overall_score_reviewed' in qry1[0]['data_sub_category'].keys():
                            qry1[0]['data_sub_category'].pop('overall_score_reviewed')
                        data.update(qry1[0]['data_sub_category'])
                else:
                    data1 = get_cat2_score_claimed_new(qry,str('A' + str(i)),emp_id)
                    data['data'] = data1[0]
                    data['overall_score'] = round((data1[1]),2)
                final_data[str('A' + str(i))] = data
            elif 'RESEARCH PAPER IN CONFERENCE' in ach_type:
                qry1 = list(FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable"))
                if len(qry1)>0:
                    if int(level)>0:
                        if int(level)==1:
                            if len(statuses)==1:
                                if "PENDING" in statuses[0]['status']:
                                    for d in qry1[0]['data_sub_category']['data']:
                                        d['score_awarded']= d['score_claimed']
                            else:
                                if "REVIEW" == statuses[-1]['status']:
                                    for d in qry1[0]['data_sub_category']['data']:
                                        d['score_reviewed']= d['score_awarded']
                        data.update(qry1[0]['data_sub_category'])
                    else:
                        for d in qry1[0]['data_sub_category']['data']:
                            if "score_awarded" in d:
                                d.pop("score_awarded")
                            if "score_reviewed" in d:
                                d.pop("score_reviewed")
                        if 'overall_score_awarded' in qry1[0]['data_sub_category'].keys():
                            qry1[0]['data_sub_category'].pop("overall_score_awarded")
                        if 'overall_score_reviewed' in qry1[0]['data_sub_category'].keys():
                            qry1[0]['data_sub_category'].pop('overall_score_reviewed')
                        data.update(qry1[0]['data_sub_category'])
                else:
                    data1 = get_cat2_score_claimed_new(qry,str('A' + str(i)),emp_id)
                    data['data'] = data1[0]
                    data['overall_score'] = round((data1[1]),2)
            elif 'RESEARCH GUIDANCE / PROJECT GUIDANCE' in ach_type:
                qry1 = list(FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable"))
                if len(qry1)>0:
                    if int(level)>0:
                        if int(level)==1:
                            if len(statuses)==1:
                                if "PENDING" in statuses[0]['status']:
                                    for d in qry1[0]['data_sub_category']['data']:
                                        d['score_awarded']= d['score_claimed']
                            else:
                                if "REVIEW" == statuses[-1]['status']:
                                    for d in qry1[0]['data_sub_category']['data']:
                                        d['score_reviewed']= d['score_awarded']
                        data.update(qry1[0]['data_sub_category'])
                    else:
                        for d in qry1[0]['data_sub_category']['data']:
                            if "score_awarded" in d:
                                d.pop("score_awarded")
                            if "score_reviewed" in d:
                                d.pop("score_reviewed")
                        if 'overall_score_awarded' in qry1[0]['data_sub_category'].keys():
                            qry1[0]['data_sub_category'].pop("overall_score_awarded")
                        if 'overall_score_reviewed' in qry1[0]['data_sub_category'].keys():
                            qry1[0]['data_sub_category'].pop('overall_score_reviewed')
                        data.update(qry1[0]['data_sub_category'])
                else:
                    data1 = get_cat2_score_claimed_new(qry,str('A' + str(i)),emp_id)
                    data['data'] = data1[0]
                    data['overall_score'] = round((data1[1]),2)
            elif 'DESIGN' in ach_type:
                qry1 = list(FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable"))
                if len(qry1)>0:
                    if int(level)>0:
                        if int(level)==1:
                            if len(statuses)==1:
                                if "PENDING" in statuses[0]['status']:
                                    for d in qry1[0]['data_sub_category']['data']:  
                                        d['score_awarded']= d['score_claimed']
                            else:
                                if "REVIEW" == statuses[-1]['status']:
                                    for d in qry1[0]['data_sub_category']['data']:
                                        d['score_reviewed']= d['score_awarded']
                        data.update(qry1[0]['data_sub_category'])
                    else:
                        for d in qry1[0]['data_sub_category']['data']:
                            if "score_awarded" in d:
                                d.pop("score_awarded")
                            if "score_reviewed" in d:
                                d.pop("score_reviewed")
                        if 'overall_score_awarded' in qry1[0]['data_sub_category'].keys():
                            qry1[0]['data_sub_category'].pop("overall_score_awarded")
                        if 'overall_score_reviewed' in qry1[0]['data_sub_category'].keys():
                            qry1[0]['data_sub_category'].pop('overall_score_reviewed')
                        data.update(qry1[0]['data_sub_category'])
                else:
                    data1 = get_cat2_score_claimed_new(qry,str('A' + str(i)),emp_id)
                    data['data'] = data1[0]
                    data['overall_score'] = round((data1[1]),2)
        else:
            row_data = get_null_values_for_achievement_new(ach_type, level, statuses)
            data['data'].append(row_data)
            data['overall_score'] = 0
            data['overall_score_awarded']= data['overall_score']
            data['overall_score_reviewed'] = data['overall_score_awarded']
        if int(level)==1:
            if len(statuses)==1:
                if "PENDING" in statuses[0]['status']:
                    data['overall_score_awarded']= data['overall_score']
            else:
                if "REVIEW" == statuses[-1]['status']:
                    data['overall_score_reviewed']= data['overall_score_awarded']
        final_data['A' + str(i)] = data

    return final_data




def get_cat2_score_claimed_new(qry,part,emp_id):
    data ={}
    score_claimed = 0
    if 'A1' in part:
        date_of_join = EmployeePrimdetail.objects.filter(emp_id=emp_id).values("doj")
        d2 = date_of_join[0]['doj']
        d1 = datetime.now()
        experience = d1.year - d2.year
        if (experience>3):
            experience = True
        else:
            experience = False
        # experience = get_net_experience(emp_id)
        # if 'years' in experience[0]:

        #     if int(experience[0].split(" ")[0])>3:
        #         experience= True
        # else:
        #     experience=False
        sub_cat = ['SCI','SCI-E','SSCI','ESCI','SCOPOUS']       
        for q in qry:
            if 'UGC RECOMMENDED' not in q['journal_details__sub_category__value']:
                if q['journal_details__sub_category__value'] in sub_cat:
                    if 'SINGLE AUTHOR' in q['author__value']:
                        if q['impact_factor'] is not None:
                            if q['impact_factor']>=0.75:
                                q['score_claimed'] = 23
                                score_claimed = score_claimed + 23
                            elif q['impact_factor']>=0.5 and q['impact_factor']<0.75:
                                q['score_claimed'] = 21
                                score_claimed = score_claimed + 21
                            elif q['impact_factor']<0.5:
                                q['score_claimed'] = 19
                                score_claimed = score_claimed + 19
                            else:
                                q['score_claimed']=15
                                score_claimed = score_claimed+15
                        else:
                            q['score_claimed'] = 15
                            score_claimed = score_claimed + 15
                            q['impact_factor']='---'
                    elif 'FIRST AUTHOR' in q['author__value'] or 'SUPERVISOR' in q['author__value']:
                        if q['impact_factor'] is not None:
                            if q['impact_factor']>=0.75:
                                q['score_claimed'] = 17
                                score_claimed = score_claimed + 17
                            elif q['impact_factor']>=0.5 and q['impact_factor']<0.75:
                                q['score_claimed'] = 15
                                score_claimed = score_claimed + 15
                            elif q['impact_factor']<0.5:
                                q['score_claimed'] = 13
                                score_claimed = score_claimed + 13
                            else:
                                q['score_claimed']= 9
                                score_claimed = score_claimed+9
                        else:
                            q['score_claimed'] = 9
                            score_claimed = score_claimed + 9
                            q['impact_factor']='---'
                    elif 'CO-AUTHOR' in q['author__value']:
                        if q['impact_factor'] is not None:
                            if q['impact_factor']>=0.75:
                                q['score_claimed'] = 14
                                score_claimed = score_claimed + 14
                            elif q['impact_factor']>=0.5 and q['impact_factor']<0.75:
                                q['score_claimed'] = 12
                                score_claimed = score_claimed + 12
                            elif q['impact_factor']<0.5:
                                q['score_claimed'] = 10
                                score_claimed = score_claimed + 10
                            else:
                                q['score_claimed']= 6
                                score_claimed = score_claimed+6
                        else:
                            q['score_claimed'] = 6
                            score_claimed = score_claimed + 6
                            q['impact_factor']='---'
                elif 'UGC RECOMMENDED' in q['journal_details__sub_category__value']:
                    q['score_claimed'] = 2
                    score_claimed = score_claimed
            elif 'UGC RECOMMENDED' in q['journal_details__sub_category__value'] and experience== False:
                q['impact_factor']='---'
                q['score_claimed']=2
                score_claimed=score_claimed+ 2
            else:
                q['impact_factor'] ='---'
                q['score_claimed'] = 0
                score_claimed =score_claimed+0

    elif 'A3' in part:
        for q in qry:
            if 'FIRST AUTHOR' in q['author__value']:
                if 'INTERNATIONAL' in q['publisher_type__value']:
                    if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
                        score_claimed = score_claimed + (5)
                        q['score_claimed'] = 5
                    elif 'BOOK' in q['role_for__value']:
                        score_claimed = score_claimed + (20)
                        q['score_claimed'] = 20
                elif 'NATIONAL' in q['publisher_type__value']:
                    if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
                        score_claimed = score_claimed + (2)
                        q['score_claimed'] = 2
                    elif 'BOOK' in q['role_for__value']:
                        score_claimed = score_claimed + (10)
                        q['score_claimed'] = 10
                elif 'REGIONAL' in q['publisher_type__value']:
                    if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
                        score_claimed = score_claimed + (1)
                        q['score_claimed'] = 1
                    elif 'BOOK' in q['role_for__value']:
                        score_claimed = score_claimed + (5)
                        q['score_claimed'] = 5
            elif 'SINGLE AUTHOR' in q['author__value']:
                if 'INTERNATIONAL' in q['publisher_type__value']:
                    if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
                        score_claimed = score_claimed + (5)
                        q['score_claimed'] = 5
                    elif 'BOOK' in q['role_for__value']:
                        score_claimed = score_claimed + (20)
                        q['score_claimed'] = 20
                elif 'NATIONAL' in q['publisher_type__value']:
                    if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
                        score_claimed = score_claimed + (2)
                        q['score_claimed'] = 2
                    elif 'BOOK' in q['role_for__value']:
                        score_claimed = score_claimed + (10)
                        q['score_claimed'] = 10
                elif 'REGIONAL' in q['publisher_type__value']:
                    if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
                        score_claimed = score_claimed + (1)
                        q['score_claimed'] = 1
                    elif 'BOOK' in q['role_for__value']:
                        score_claimed = score_claimed + (5)
                        q['score_claimed'] = 5
            else :
                if 'INTERNATIONAL' in q['publisher_type__value']:
                    if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
                        score_claimed = score_claimed + 5
                        q['score_claimed'] = 5
                    elif 'BOOK' in q['role_for__value']:
                        score_claimed = score_claimed + (20)
                        q['score_claimed'] = 20
                elif 'NATIONAL' in q['publisher_type__value']:
                    if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
                        score_claimed = score_claimed + (2)
                        q['score_claimed'] = 2
                    elif 'BOOK' in q['role_for__value']:
                        score_claimed = score_claimed + (10)
                        q['score_claimed'] = 10
                elif 'REGIONAL' in q['publisher_type__value']:
                    if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
                        score_claimed = score_claimed + (1)
                        q['score_claimed'] = 1
                    elif 'BOOK' in q['role_for__value']:
                        score_claimed = score_claimed + (5)
                        q['score_claimed'] = 5
            # else:
            #   score_claimed = score_claimed + 0
            #   q['score_claimed'] = 0

    elif 'A4' in part:
        for q in qry:
            q['period'] = get_period((q['end_date']-q['start_date']).days)
            if 'PROPOSED' not in q['project_status__value']:
                if q['principal_investigator'] is not None and q['co_principal_investigator'] is not None:
                    if 'SELF' in q['principal_investigator'].upper() and 'SELF' in q['co_principal_investigator'].upper():
                        if q['amount']>=3000000:
                            score_claimed = score_claimed+(20)
                            q['score_claimed'] = 20
                        elif q['amount'] >= 500000 and q['amount']<3000000:
                            score_claimed = score_claimed + (15)
                            q['score_claimed'] = 15
                        elif q['amount'] >=50000 and q['amount']<500000:
                            score_claimed = score_claimed+(10)
                            q['score_claimed'] = 10
                        else:
                            q['score_claimed'] = 0
                    elif 'SELF' in q['principal_investigator'].upper() and 'OTHER' in q['co_principal_investigator'].upper():
                        if q['amount']>=3000000:
                            score_claimed = score_claimed+(12)
                            q['score_claimed'] = 12
                        elif q['amount'] >= 500000 and q['amount']<3000000:
                            score_claimed = score_claimed + (9)
                            q['score_claimed'] = 9
                        elif q['amount'] >=50000 and q['amount']<500000:
                            score_claimed = score_claimed+(6)
                            q['score_claimed'] = 6
                        else:
                            q['score_claimed'] = 0
                    elif 'OTHER' in q['principal_investigator'].upper() and 'SELF' in q['co_principal_investigator'].upper():
                        if q['amount']>=3000000:
                            score_claimed = score_claimed+(8)
                            q['score_claimed'] = 8
                        elif q['amount'] >= 500000 and q['amount']<3000000:
                            score_claimed = score_claimed + (6)
                            q['score_claimed'] = 6
                        elif q['amount'] >=50000 and q['amount']<500000:
                            score_claimed = score_claimed+(4)
                            q['score_claimed'] = 4
                        else:
                            q['score_claimed'] = 0
                    else:
                        q['score_claimed']=0
                else:
                    q['score_claimed']=0
            else:
                q['score_claimed'] = 0
    elif 'A5' in part:
        for q in qry:
            if 'IF FILED' not in q['patent_details__patent_status__value']:
                if q['patent_details__patent_applicant_name'] is not None and q['patent_details__patent_co_applicant_name'] is not None:
                    if 'SELF' in q['patent_details__patent_applicant_name'].upper() and 'SELF' in q['patent_details__patent_co_applicant_name'].upper():
                        if 'INTERNATIONAL' in q['patent_details__level__value']:
                            if 'IF GRANTED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 40
                                score_claimed = score_claimed+40
                            if 'PUBLISHED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 30
                                score_claimed = score_claimed+30
                        elif  'NATIONAL' in q['patent_details__level__value']:
                            if 'IF GRANTED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 25
                                score_claimed = score_claimed+25
                            if 'PUBLISHED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 20
                                score_claimed = score_claimed+20
                        else:
                            q['score_claimed']=0
                    elif 'SELF' in q['patent_details__patent_applicant_name'].upper() and 'OTHER' in q['patent_details__patent_co_applicant_name'].upper():
                        if 'INTERNATIONAL' in q['patent_details__level__value']:
                            if 'IF GRANTED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 24
                                score_claimed = score_claimed+(24)
                            if 'PUBLISHED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 18
                                score_claimed = score_claimed + (18)
                        elif  'NATIONAL' in q['patent_details__level__value']:
                            if 'IF GRANTED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 15
                                score_claimed = score_claimed+(15)
                            if 'PUBLISHED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 12
                                score_claimed = score_claimed + (12)
                        else:
                            q['score_claimed']=0
                    elif 'OTHER' in q['patent_details__patent_applicant_name'].upper() and 'SELF' in q['patent_details__patent_co_applicant_name'].upper():
                        if 'INTERNATIONAL' in q['patent_details__level__value']:
                            if 'IF GRANTED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 16
                                score_claimed = score_claimed+(16)
                            if 'PUBLISHED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 12
                                score_claimed = score_claimed + (12)
                        elif  'NATIONAL' in q['patent_details__level__value']:
                            if 'IF GRANTED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 10
                                score_claimed = score_claimed+(10)
                            if 'PUBLISHED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 8
                                score_claimed = score_claimed + (8)
                        else:
                            q['score_claimed']=0
                    else:
                        q['score_claimed']=0
                else:
                    q['score_claimed']=0
            else:
                q['score_claimed'] = 0
    elif 'A6' in part:
        for q in qry:
            if 'IF FILED' not in q['design_status__value']:
                if q['design_applicant_name'] is not None and q['design_co_applicant_name'] is not None:
                    if 'SELF' in q['design_applicant_name'].upper() and 'SELF' in q['design_co_applicant_name'].upper():
                        if 'INTERNATIONAL' in q['design_level__value']:
                            if 'IF GRANTED' in q['design_status__value']:
                                q['score_claimed'] = (30)
                                score_claimed = score_claimed+(30)
                            if 'PUBLISHED' in q['design_status__value']:
                                q['score_claimed'] = 20
                                score_claimed = score_claimed + (20)
                        elif  'NATIONAL' in q['design_level__value']:
                            if 'IF GRANTED' in q['design_status__value']:
                                q['score_claimed'] = 20
                                score_claimed = score_claimed+(20)
                            if 'PUBLISHED' in q['design_status__value']:
                                q['score_claimed'] = 15
                                score_claimed = score_claimed + (15)
                        else:
                            q['score_claimed'] = 0
                    elif 'SELF' in q['design_applicant_name'].upper() and 'OTHER' in q['design_co_applicant_name'].upper():
                        if 'INTERNATIONAL' in q['design_level__value']:
                            if 'IF GRANTED' in q['design_status__value']:
                                q['score_claimed'] = 18
                                score_claimed = score_claimed+(18)
                            if 'PUBLISHED' in q['design_status__value']:
                                q['score_claimed'] = 12
                                score_claimed = score_claimed + (12)
                        elif  'NATIONAL' in q['design_level__value']:
                            if 'IF GRANTED' in q['design_status__value']:
                                q['score_claimed'] = 12*0.6
                                score_claimed = score_claimed+(12)
                            if 'PUBLISHED' in q['design_status__value']:
                                q['score_claimed'] = 9
                                score_claimed = score_claimed + (9)
                    elif 'OTHER' in q['design_applicant_name'].upper() and 'SELF' in q['design_co_applicant_name'].upper():
                        if 'INTERNATIONAL' in q['design_level__value']:
                            if 'IF GRANTED' in q['design_status__value']:
                                q['score_claimed'] = 12
                                score_claimed = score_claimed+12
                            if 'PUBLISHED' in q['design_status__value']:
                                q['score_claimed'] = 8
                                score_claimed = score_claimed + 8
                        elif  'NATIONAL' in q['design_level__value']:
                            if 'IF GRANTED' in q['design_status__value']:
                                q['score_claimed'] = 8
                                score_claimed = score_claimed+8
                            if 'PUBLISHED' in q['design_status__value']:
                                q['score_claimed'] = 6
                                score_claimed = score_claimed + (6)
                    else:
                        q['score_claimed'] = 0
            else:
                q['score_claimed'] = 0

    elif 'A7' in part:
        for q in qry:
            if 'RESEARCH (PH. D.)' in q['guidance_for__value']:
                if 'AWARDED' in q['guidance_status__value'] and 'DEGREE' in q['guidance_for__value']:
                    q['score_claimed'] =  10
                    score_claimed = score_claimed +10
                elif 'SUBMITTED' in q['guidance_status__value'] and 'THESIS' in q['guidance_for__value']:
                    q['score_claimed'] =  7
                    score_claimed = score_claimed +7
                else:
                    q['score_claimed'] =0 
            else:
                q['score_claimed'] = 0
                score_claimed = score_claimed+0
    elif 'A2' in part:
        for q in qry:
            if q['author__value'] is not None:
                if 'INTERNATIONAL' in q['conference_detail__type_of_conference__value']:
                    if 'SINGLE AUTHOR' in q['author__value']:
                        q['score_claimed']=10
                        score_claimed=score_claimed+10
                    elif 'FIRST AUTHOR' in q['author__value'] or 'SUPERVISOR' in q['author__value']:
                        q['score_claimed']=6
                        score_claimed=score_claimed+6
                    elif 'CO-AUTHOR' in q['author__value']:
                        q['score_claimed']=4
                        score_claimed = score_claimed+4
                    else:
                        q['score_claimed'] = 0
                elif 'NATIONAL' in q['conference_detail__type_of_conference__value']:
                    if 'SINGLE AUTHOR' in q['author__value']:
                        q['score_claimed']=7.5
                        score_claimed=score_claimed+7.5
                    elif 'FIRST AUTHOR' in q['author__value'] or 'SUPERVISOR' in q['author__value']:
                        q['score_claimed']=4.5
                        score_claimed=score_claimed+4.5
                    elif 'CO-AUTHOR' in q['author__value']:
                        q['score_claimed']=3.5
                        score_claimed = score_claimed+3.5
                    else:
                        q['score_claimed'] =0 
                else:
                    q['score_claimed'] = 0
            else:
                q['score_claimed'] = 0

    return [qry,score_claimed]



def get_null_values_for_achievement_new(ach_type, level, status):
    ### ID == None ###
    ach_type = str(ach_type)
    row_data = {}
    if ach_type == "RESEARCH PAPER IN JOURNAL":
        row_data = {'paper_title': '---', 'journal_details__isbn': '---', 'published_date': '---', 'journal_details__type_of_journal__value': '---', 'journal_details__sub_category__value': '---', 'author__value': '---', 'impact_factor': '---', 'score_claimed': '---', 'id': '---'}
        if int(level) >= 1:
            if len(status) == 1:
                row_data['score_awarded'] = 0
            else:
                row_data['score_awarded'] = 0
                row_data['score_reviewed'] = 0

    elif ach_type == "RESEARCH PAPER IN CONFERENCE":
        row_data = {'paper_title': '---', 'conference_detail__conference_from': '---', 'isbn': '---', 'conference_detail__type_of_conference__value': '---', 'author__value': '---', 'score_claimed': '---', 'id': '---'}
        if int(level) >= 1:
            if len(status) == 1:
                row_data['score_awarded'] = 0
            else:
                row_data['score_awarded'] = 0
                row_data['score_reviewed'] = 0

    elif ach_type == "BOOKS":
        row_data = {'book_title': '---', 'published_date': '---', 'isbn': '---', 'publisher_type__value': '---', 'author__value': '---', 'publisher_details__publisher_name': '---', 'score_claimed': '---', 'id': '---','role':'---','role__value':'---','author':'---'}
        if int(level) >= 1:
            if len(status) == 1:
                row_data['score_awarded'] = 0
            else:
                row_data['score_awarded'] = 0
                row_data['score_reviewed'] = 0

    elif ach_type == "PROJECTS/CONSULTANCY":
        row_data = {'start_date': '---', 'project_title': '---', 'project_type__value': '---', 'period': '---', 'principal_investigator': '---', 'amount': '---', 'score_claimed': '---', 'id': '---'}
        if int(level) >= 1:
            if len(status) == 1:
                row_data['score_awarded'] = 0
            else:
                row_data['score_awarded'] = 0
                row_data['score_reviewed'] = 0

    elif ach_type == "PATENT":
        row_data = {'patent_details__patent_title': '---','company_name': '---', 'patent_date': '---', 'patent_details__level__value': '---', 'patent_details__patent_status__value': '---',  'score_claimed': '---', 'id': '---','patent_details__patent_applicant_name':'---','patent_details__patent_co_applicant_name':'---'}
        if int(level) >= 1:
            if len(status) == 1:
                row_data['score_awarded'] = 0
            else:
                row_data['score_awarded'] = 0
                row_data['score_reviewed'] = 0

    elif ach_type == "RESEARCH GUIDANCE / PROJECT GUIDANCE":
        row_data = {'guidance_status__value': '---', 'degree__value': '---', 'date_of_guidance': '---', 'score_claimed': '---', 'id': '---','guidance_for':'---','project_title':'---'}
        if int(level) >= 1:
            if len(status) == 1:
                row_data['score_awarded'] = 0
            else:
                row_data['score_awarded'] = 0
                row_data['score_reviewed'] = 0

    elif ach_type == "TRAINING AND DEVELOPMENT PROGRAM":
        row_data = {'category__value': '---', 'from_date': '---','to_date':'---', 'organizers':'---','training_type__value': '---', 'durtion': '---', 'role__value': '---', 'training_sub_type__value':'---','days':'---','organization_sector__value': '---', 'score_claimed': '---', 'id': '---'}
        if int(level) >= 1:
            if len(status) == 1:
                row_data['score_awarded'] = 0
            else:
                row_data['score_awarded'] = 0
                row_data['score_reviewed'] = 0

    elif ach_type == "LECTURES AND TALKS":
        row_data = {'category__value': '---', 'date': '---', 'topic': '---', 'role__value': '---', 'type_of_event__value': '---', 'score_claimed': '---', 'id': '---'}
        if int(level) >= 1:
            if len(status) == 1:
                row_data['score_awarded'] = 0
            else:
                row_data['score_awarded'] = 0
                row_data['score_reviewed'] = 0

    elif ach_type == 'DESIGN':
        row_data = {'design_status__value': '---', 'design_applicant_name': '---', 'design_co_applicant_name': '---', 'design_level__value': '---','design_title':'---','design_date':'---', 'score_claimed': '---', 'id': '---'}
        if int(level) >= 1:
            if len(status) == 1:
                row_data['score_awarded'] = 0
            else:
                row_data['score_awarded'] = 0
                row_data['score_reviewed'] = 0

    return row_data


#########################################################################CAT - 2 END############################################################



#####################################################################FUNCTIONS##################################################################

def get_next_level_status_new(emp_id, level, session):
    status = "PENDING"
    qry = FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level) + 1, session=session).exclude(status="DELETE").values('id', 'approval_status').order_by('-id')
    if len(qry) > 0:
        status = qry[0]['approval_status']
    return status


def get_submission_status_of_emp_new(emp_id, session):
    qry = FacultyAppraisal.objects.filter(emp_id=emp_id, session=session, level=0, form_filled_status='Y', status="SUBMITTED").exclude(status="DELETE").values('form_filled_status', 'id').order_by('-id')
    emp_status = "NOT FILLED"
    if len(qry) > 0:
        if qry[0]['form_filled_status'] == 'Y':
            emp_status = "FILLED"
        else:
            emp_status = "NOT FILLED"
    return emp_status


def int_to_Roman(num):
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num


def get_subject_wise_total_pass_stu_percentage_new(univ_marks):
    total_students = len(univ_marks)
    passed_students = 0
    per_passed_students = 0
    for univ in univ_marks:
        if check_is_pass_or_fail_new(univ)[0] == True:
            passed_students = passed_students + 1
        if total_students > 0:
            per_passed_students = (passed_students / total_students) * 100
    return round(per_passed_students, 2)

def get_subject_wise_total_pass_students_new(univ_marks):
    total_students = len(univ_marks)
    passed_students = 0
    per_passed_students = 0
    for univ in univ_marks:
        if check_is_pass_or_fail_new(univ)[0] == True:
            passed_students = passed_students + 1
        if total_students > 0:
            per_passed_students = (passed_students / total_students) * 100
    failed_students = total_students - passed_students
    return [total_students,passed_students,failed_students]

def get_external_exam_average_new(univ_marks):
    total_students = len(univ_marks)
    total_external = 0.0
    average = 0
    for univ in univ_marks:
        try:
            univ['external_marks'] = float(univ['external_marks'])
        except:
            univ['external_marks'] = 0

        try:
            univ['back_marks'] = float(univ['back_marks'])
        except:
            univ['back_marks'] = 0
        if univ['back_marks'] == None or univ['back_marks'] == 0:
            total_external = total_external + univ['external_marks']
        else:

            total_external = total_external + univ['back_marks']
    if total_students > 0:
        average = total_external / total_students
    return round(average, 2)


def get_external_exam_average_per_new(univ_marks):
    total_students = len(univ_marks)
    total_external = 0.0
    average_per = 0
    external_total_total = 0
    if len(univ_marks) > 0:
        external_total_total = univ_marks[0]['subject_id__max_university_marks']
    average = 0
    for univ in univ_marks:
        try:
            univ['external_marks'] = float(univ['external_marks'])
        except:
            univ['external_marks'] = 0

        try:
            univ['back_marks'] = float(univ['back_marks'])
        except:
            univ['back_marks'] = 0
        if univ['back_marks'] == None or univ['back_marks'] == 0:
            total_external = total_external + univ['external_marks']
        else:

            total_external = total_external + univ['back_marks']
    if total_students > 0:
        average = total_external / total_students
    if external_total_total != None and external_total_total != 0:
        average_per = float(average / external_total_total) * 100
    return round(average_per, 2)


def get_percentage_of_student_new(univ_marks):
    total_students = len(univ_marks)
    percentage = 0
    if check_is_pass_or_fail_new(univ_marks)[0] == True:
        max_marks = int(check_is_pass_or_fail_new(univ_marks)[1])
        marks_obt = int(check_is_pass_or_fail_new(univ_marks)[2])
        if int(max_marks) != 0:
            percentage = float((marks_obt / max_marks) * 100)
    return percentage


def get_university_marks_subject_wise(lectures):
    # lectures = {'session_name':---,'section__sem_id':---,'section':---,'subject_id':---}
    data = {}
    if 'section__sem_id' in lectures and 'section' in lectures:
        extra_filter = {'uniq_id__sem': lectures['section__sem_id'], 'uniq_id__section': lectures['section']}
    elif 'sem' in lectures and 'section' in lectures:
        extra_filter = {'uniq_id__sem': lectures['sem'], 'uniq_id__section__in': lectures['section']}
    else:
        extra_filter = {}
    data['below_40'] = 0
    data['in_40_49'] = 0
    data['in_50_59'] = 0
    data['above_60'] = 0
    session = Semtiming.objects.filter(session_name=lectures['session_name']).values('uid')
    if len(session) > 0:
        StudentUniversityMarks = generate_session_table_name('StudentUniversityMarks_', lectures['session_name'])
        studentSession = generate_session_table_name('studentSession_', lectures['session_name'])
        univ_marks = list(StudentUniversityMarks.objects.filter(uniq_id__session=session[0]['uid'], subject_id=lectures['subject_id']).filter(**extra_filter).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX")).values_list('uniq_id', flat=True)).exclude(subject_id__status="DELETE").values('subject_id', 'subject_id__max_ct_marks', 'subject_id__max_ta_marks', 'subject_id__max_att_marks', 'subject_id__max_university_marks', 'external_marks', 'internal_marks', 'back_marks', 'uniq_id').order_by('uniq_id'))
        data['per_passed_students'] = get_subject_wise_total_pass_stu_percentage_new(univ_marks)
        students_data = get_subject_wise_total_pass_students_new(univ_marks)
        data['total_students'] = students_data[0]
        data['passed_students'] = students_data[1]
        data['failed_students'] = students_data[2]
        data['average_external'] = get_external_exam_average_new(univ_marks)
        data['average_external_per'] = get_external_exam_average_per_new(univ_marks)
        for student in univ_marks:
            percentage = get_percentage_of_student_new(student)
            percentage = float(percentage)
            if percentage < 40:
                data['below_40'] = data['below_40'] + 1
            elif percentage < 50.0 and percentage >= 40.0:
                data['in_40_49'] = data['in_40_49'] + 1
            elif percentage < 60.0 and percentage >= 50.0:
                data['in_50_59'] = data['in_50_59'] + 1
            else:
                data['above_60'] = data['above_60'] + 1
    else:
        data['per_passed_students'] = 0
        data['average_external'] = 0
        data['below_40'] = 0
        data['in_40_49'] = 0
        data['in_50_59'] = 0
        data['above_60'] = 0
    return data





def delete_row_from_tables_new(last_id, session, level, approval_status):
    if last_id != None:
        FacAppCatWiseData.objects.filter(fac_app_id=last_id).exclude(status=0).update(status=0)
        FacAppAcadData.objects.filter(fac_app_id=last_id).exclude(status=0).update(status=0)
        return True
    else:
        return False


def get_statuses_at_reporting_level_of_faculty_new(emp_id, session):
    data = []
    qry = AarReporting.objects.filter(emp_id=emp_id).values('reporting_to', 'reporting_to__value', 'department', 'reporting_no').order_by('reporting_no')
    if len(qry) > 0:
        for q in qry:
            get_reporting_id = EmployeePrimdetail.objects.filter(dept=q['department'], desg=q['reporting_to']).exclude(emp_status="SEPARATE").exclude(emp_id="00007").values('emp_id')
            if len(get_reporting_id) > 0:
                get_status = list(FacAppRecommendationApproval.objects.filter(added_by=get_reporting_id[0]['emp_id'], level=q['reporting_no'], session=session, emp_id=emp_id).exclude(status="DELETE").values('approval_status', 'id').order_by('-id'))
                if len(get_status) > 0:
                    data.append({'status': get_status[0]['approval_status'], 'desgination': q['reporting_to__value']})
                else:
                    data.append({'status': 'PENDING', 'desgination': q['reporting_to__value']})
    return data



def check_eligibility_of_research_contributions_faculty(emp_id,level,session,session_name,desg,agp):
    status = 'RECOMMENDABLE'
    research_data = get_cat2_form_data_new(emp_id,level,session,session_name)

    if 'main_heading' in research_data:
        main_heading = research_data.pop("main_heading")
    overall_score = 0
    for i in research_data.keys():
        overall_score=overall_score +research_data[i]['overall_score']
    if 'ASSISTANT PROFESSOR' == desg:
        if agp >=6000 and agp <7000:
            if overall_score<6:
                status = 'NOT RECOMMENDABLE'
        elif agp>=7000 and agp <8000:
            if overall_score<10:
                status = 'NOT RECOMMENDABLE'
        elif agp>=8000:
            if overall_score<15:
                status = 'NOT RECOMMENDABLE'
    elif 'ASSOCIATE PROFESSOR' == desg:
        if overall_score<20:
            status = 'NOT RECOMMENDABLE'
    elif 'PROFESSOR' == desg:
        if overall_score<25:
            status = 'NOT RECOMMENDABLE'
    elif desg in ['ASSOCIATE PROFESSOR (RESEARCH)','ASSISTANT PROFESSOR (RESEARCH)','PROFESSOR (RESEARCH)']:
        if overall_score<32:
            status = 'NOT RECOMMENDABLE'
    if status == 'NOT RECOMMENDABLE':
        return [status,False]
    else:
        return [status,True]




def get_faculty_under_reporting_new(emp_id, session,session_name):
    list_emp = []
    consolidate_data = {}
    qry = list(EmployeePrimdetail.objects.filter(emp_id=emp_id).exclude(emp_status="SEPARATE").exclude(emp_id='00007').values('emp_category__value', 'cadre__value', 'ladder__value', 'desg', 'desg__value', 'dept', 'dept__value'))
    if len(qry) > 0:
        list_emp = list(AarReporting.objects.filter(reporting_to=qry[0]['desg'], department=qry[0]['dept']).exclude(emp_id__emp_category__value="TECHNICAL STAFF").exclude(emp_id__emp_category__value="STAFF").exclude(emp_id__emp_status="SEPARATE").exclude(emp_id='00007').values('emp_id', 'emp_id__name', 'emp_id__cadre__value', 'emp_id__ladder__value', 'emp_id__dept__value').order_by('emp_id__dept__value', 'emp_id__name'))
        for emp in list_emp:
            other_details = get_emp_part_data_new(emp['emp_id'], session, {})
            for k, v in other_details.items():
                emp[k] = v
            query = FacultyAppraisal.objects.filter(emp_id=emp['emp_id'], session=session).exclude(status="DELETE").exclude(status="PENDING").values()

            ############ REPORTING DETAILS ##################################
            reporting = get_reporting_of_emp_of_corresponding_band(qry[0]['dept'], qry[0]['desg'], emp['emp_id'], {})
            emp['reporting_level'] = reporting

            emp['status'] = get_statuses_at_reporting_level_of_faculty_new(emp['emp_id'], session)
            status_len = len(emp['status'])
            emp['max_reporting_emp'] = status_len
            # AWARDED MARKS EDITABLE CHECK .............
            if int(reporting) > 1:
                emp['is_awarded_editable'] = False
            else:
                if status_len >= int(reporting):
                    if emp['status'][int(reporting) - 1]['status'] != 'REVIEW' and emp['status'][int(reporting) - 1]['status'] != "REVIEWED":
                        if status_len > int(reporting):
                            if emp['status'][int(reporting)]['status'] != 'APPROVED' and emp['status'][int(reporting)]['status'] != 'REVIEWED':
                                emp['is_awarded_editable'] = True
                            else:
                                emp['is_awarded_editable'] = False
                        else:
                            emp['is_awarded_editable'] = True
                    else:
                        emp['is_awarded_editable'] = False
                else:
                    emp['is_awarded_editable'] = False
            ############################################
            # REVIEWED MARKS EDITABLE CHECK .............
            if int(reporting) >= 1 and status_len > int(reporting):
                if emp['status'][int(reporting)]['status'] == "APPROVED" or emp['status'][int(reporting)]['status'] == "REVIEWED":
                    emp['is_reviewed_editable'] = False
                elif int(reporting) > 1 and emp['status'][int(reporting)]['status'] == "REVIEW":
                    emp['is_reviewed_editable'] = False
                else:
                    emp['is_reviewed_editable'] = True
            else:
                emp['is_reviewed_editable'] = False
            ############################################
            # REVIEW CHECK .................
            emp['is_review'] = check_if_review_is_eligible(reporting)
            ####################################

            is_eligible_check = check_eligibility_of_employee_faculty(emp['emp_id'], session)
            if is_eligible_check == "NOT ELIGIBLE":
                emp['emp_status'] = "NOT ELIGIBLE"
            else:
                emp['emp_status'] = get_submission_status_of_emp_new(emp['emp_id'],  session)
                if 'NOT FILLED' not in  emp['emp_status']:
                    eligible_check = check_eligibility_of_research_contributions_faculty(emp['emp_id'],1,session,session_name,emp['current_pos__value'],emp['agp'])
                    if eligible_check[0] == "NOT RECOMMENDABLE":
                        emp['emp_status'] = "NOT RECOMMENDABLE"
            emp['desgination'] = qry[0]['desg__value']
            if len(query) > 0:
                emp['reporting'] = []
                if reporting != None:
                    for i in range(1, int(reporting + 1)):
                        status = FacAppRecommendationApproval.objects.filter(emp_id=emp['emp_id'], level=i,session=session).exclude(status="DELETE").values('approval_status', 'added_by', 'added_by__name', 'id').order_by('-id')
                        if len(status) > 0:
                            emp['reporting'].append({'status': status[0]['approval_status'], 'added_by': status[0]['added_by'], 'added_by__name': status[0]['added_by__name']})
                        else:
                            emp['reporting'].append({'status': 'PENDING', 'added_by': None, 'added_by__name': None})
            else:
                emp['reporting'] = []
                if reporting != None:
                    for i in range(1, int(reporting + 1)):
                        emp['reporting'].append({'status': 'PENDING', 'added_by': None, 'added_by__name': None})

            if len(emp['reporting']) > 0:
                if emp['reporting'][-1]['status'] == "REVIEW" or emp['reporting'][-1]['status'] == "REVIEWED":
                    emp['is_reviewed_marks'] = True
                elif int(reporting) > 1:
                    f = 0
                    for s in emp['status']:
                        if s['status'] == "REVIEW" or s['status'] == "REVIEWED":
                            emp['is_reviewed_marks'] = True
                            f =1
                            break
                    if f!=1:
                        emp['is_reviewed_marks'] = False
                else:
                    emp['is_reviewed_marks'] = False
            #################### END.......###########################################
        ############# FOR CONSOLIDATE DATA ####################
        flag = 0
        not_filled = 0
        filled = 0
        max_reporting = get_maximum_reporting(list_emp)
        # if form_type != "S-BAND":
        consolidate_data['emp'] = {}
        consolidate_data['emp']['not_filled'] = 0
        consolidate_data['emp']['filled'] = 0
        consolidate_data['emp']['total'] = 0
        for emp in list_emp:
            level_reporting = 0
            # if form_type != "S-BAND":
            consolidate_data['emp']['total'] = consolidate_data['emp']['total'] + 1
            if emp['emp_status'] == "NOT FILLED":
                consolidate_data['emp']['not_filled'] = consolidate_data['emp']['not_filled'] + 1
            if emp['emp_status'] == "FILLED":
                flag = 1
                # if form_type != "S-BAND":
                consolidate_data['emp']['filled'] = consolidate_data['emp']['filled'] + 1
                for level, status in enumerate(emp['status']):
                    if status['desgination'] == qry[0]['desg__value'] and int(level) + 1 <= int(max_reporting) and level_reporting == 0:
                        level = int(max_reporting) - 1
                    if level_reporting == 0:
                        if "level_" + str(int(level) + 1) in consolidate_data:
                            if status['status'] == "PENDING" or status['status'] == "REVIEW":
                                consolidate_data["level_" + str(int(level) + 1)]['not_filled'] = consolidate_data["level_" + str(int(level) + 1)]['not_filled'] + 1
                            if status['status'] == "APPROVED" or status['status'] == "REVIEWED":
                                consolidate_data["level_" + str(int(level) + 1)]['filled'] = consolidate_data["level_" + str(int(level) + 1)]['filled'] + 1
                            consolidate_data["level_" + str(int(level) + 1)]['total'] = consolidate_data["level_" + str(int(level) + 1)]['total'] + 1

                        else:
                            consolidate_data["level_" + str(int(level) + 1)] = {}
                            consolidate_data["level_" + str(int(level) + 1)].update({'not_filled': 0, 'filled': 0, 'total': 1})
                            if status['status'] == "PENDING" or status['status'] == "REVIEW":
                                consolidate_data["level_" + str(int(level) + 1)]['not_filled'] = 1
                            if status['status'] == "APPROVED" or status['status'] == "REVIEWED":
                                consolidate_data["level_" + str(int(level) + 1)]['filled'] = 1
                    if status['desgination'] == qry[0]['desg__value'] and int(level) + 1 <= int(max_reporting) and level_reporting == 0:
                        level_reporting = 1
        if flag == 0:
            for i in range(1, int(max_reporting) + 1):
                consolidate_data["level_" + str(i)] = {}
                consolidate_data["level_" + str(i)]['not_filled'] = 0
                consolidate_data["level_" + str(i)]['filled'] = 0
                consolidate_data["level_" + str(i)]['total'] = 0
        ################### END #################################
    return list_emp,consolidate_data




def get_remark_function_faculty_new(pre_level, level, emp_id, session):
    remark = {}
    remark['data'] = []
    remark['heading'] = []
    remark['is_editable'] = []
    for l in range(int(pre_level), int(level) + 1):
        qry = FacAppRecommendationApproval.objects.filter(level=l, emp_id=emp_id, session=session).exclude(status="DELETE").exclude(approval_status="REVIEW").values('remark', 'id', 'approval_status', 'added_by__desg__value').order_by('id')
        if len(qry) > 0:
            for q in qry:
                remark['data'].append(q['remark'])
                remark['heading'].append(str(q['added_by__desg__value']))
                remark['is_editable'].append(check_if_form_editable_or_not_faculty_new(emp_id, l,  session, level, q['approval_status']))
        else:
            get_reporting_desg = AarReporting.objects.filter(emp_id=emp_id, reporting_no=l).values('reporting_to', 'reporting_to__value')
            if len(get_reporting_desg) > 0:
                remark['heading'].append(str(get_reporting_desg[0]['reporting_to__value']))
            else:
                remark['heading'].append(None)
            remark['data'].append(None)
            remark['is_editable'].append(check_if_form_editable_or_not_faculty_new(emp_id, l,  session, level, 'PENDING'))
    return remark



def get_remark_faculty_new(level, emp_id, session):
    remark = {}
    flag = False
    if int(level) != 0:
        pre_level = 1
        remark = get_remark_function_faculty_new(pre_level, level, emp_id, session)
    return remark


def get_approval_status_for_repoprting_level_faculty_new(level, emp_id, session):
    status = "APPROVED"
    qry = FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level) + 1, session=session).exclude(status="DELETE").values('approval_status').order_by('-approval_status')
    if len(qry) > 0:
        if qry[0]['approval_status'] == "REVIEW":
            status = "REVIEWED"
    return status


def get_current_status_reporting_level_of_employee_new(level, emp_id, added_by):
    status = "PENDING"
    qry = FacAppRecommendationApproval.objects.filter(emp_id=emp_id, added_by=added_by).exclude(status="DELETE").values_list('approval_status', flat=True).order_by('-approval_status')
    if len(qry) > 0:
        status = qry[0]
    return status


def get_training_sugg_achv_new(emp_id, session):
    data = {}
    qry = list(FacultyAppraisal.objects.filter(emp_id=emp_id, form_filled_status="Y", status="SUBMITTED", session=session).exclude(status="DELETE").values('training_needs', 'suggestions','achievement_recognition').order_by('-id'))
    if len(qry) > 0:
        data['training'] = qry[0]['training_needs']
        data['suggestion'] = qry[0]['suggestions']
        data['achievement_recognition'] = qry[0]['achievement_recognition']
    return data



#####################################################################################NEW  FUNCTION BY YASH END #########################################################
####################################################################################### REPORTS ##########################################################################



def get_detpwise_consolidate_data_new(dept, session,session_name):
    data = {}
    data = {'not_filled': 0, 'filled': 0, 'total_approved': 0, 'total_employee': 0, 'not_eligible': 0,'not_recommendable':0}
    data['dept_data'] = []
    for d in dept:
        employee = list(EmployeePrimdetail.objects.filter(dept__value=d['dept__value'], emp_category__value="FACULTY").exclude(emp_id='00007').exclude(emp_status="SEPARATE").values('emp_id', 'dept', 'dept__value', 'desg', 'desg__value','current_pos__value').distinct())
        dept_data = {'dept': 'None', 'dept_data': {}}
        if len(employee) == 0:
            if d['dept__value'] in dept_data['dept']:
                dept_data['dept_data'] = {'not_filled': 0, 'filled': 0,'total_approved': 0, 'total_employee': 0, 'not_eligible': 0,'not_recommendable':0}
            else:
                dept_data['dept'] = d['dept__value']
                dept_data['dept_data'] = {'not_filled': 0, 'filled': 0, 'total_approved': 0, 'total_employee': 0, 'not_eligible': 0,'not_recommendable':0}
        for emp in employee:
            agp = get_gross_salary(emp['emp_id'],session,{})['agp']
            emp['agp'] = agp
            is_eligible_check = check_eligibility_of_employee_faculty(emp['emp_id'], session)
            eligible_check = check_eligibility_of_research_contributions_faculty(emp['emp_id'],1,session,session_name,emp['current_pos__value'],agp)
            if is_eligible_check == "NOT ELIGIBLE":
                emp_status = "NOT ELIGIBLE"
            else:
                emp_status = get_submission_status_of_emp_new(emp['emp_id'],  session)
                # if 'NOT FILLED' not in  emp_status:
                #     if eligible_check[0] == "NOT RECOMMENDABLE":
                #         emp_status = "NOT RECOMMENDABLE"
            level_status = get_statuses_at_reporting_level_of_faculty_new(emp['emp_id'], session)
            if 'NOT FILLED' in emp_status:
                if emp['dept__value'] in dept_data['dept']:
                    dept_data['dept_data']['not_filled'] = dept_data['dept_data']['not_filled'] + 1
                    dept_data['dept_data']['total_employee'] = dept_data['dept_data']['total_employee'] + 1

                    data['not_filled'] = data['not_filled'] + 1
                    data['total_employee'] = data['total_employee'] + 1
                else:
                    dept_data['dept'] = emp['dept__value']
                    dept_data['dept_data'] = {'not_filled': 1, 'filled': 0, 'total_approved': 0, 'total_employee': 1, 'not_eligible': 0,'not_recommendable':0}

                    data['not_filled'] = data['not_filled'] + 1
                    data['total_employee'] = data['total_employee'] + 1

            elif "FILLED" in emp_status:
                if emp['dept__value'] in dept_data['dept']:
                    dept_data['dept_data']['filled'] = dept_data['dept_data']['filled'] + 1
                    dept_data['dept_data']['total_employee'] = dept_data['dept_data']['total_employee'] + 1

                    data['filled'] = data['filled'] + 1
                    data['total_employee'] = data['total_employee'] + 1
                    if len(level_status) > 0:
                        if level_status[-1]['status'] == "APPROVED":
                            dept_data['dept_data']['total_approved'] = dept_data['dept_data']['total_approved'] + 1
                            data['total_approved'] = data['total_approved'] + 1
                else:
                    dept_data['dept'] = emp['dept__value']
                    dept_data['dept_data'] = {'not_filled': 0, 'filled': 1, 'total_approved': 0, 'total_employee': 1, 'not_eligible': 0,'not_recommendable':0}

                    data['filled'] = data['filled'] + 1
                    data['total_employee'] = data['total_employee'] + 1
                    if len(level_status) > 0:
                        if level_status[-1]['status'] == "APPROVED":
                            dept_data['dept_data']['total_approved'] = dept_data['dept_data']['total_approved'] + 1
                            data['total_approved'] = data['total_approved'] + 1

            elif 'NOT ELIGIBLE' in emp_status:
                if emp['dept__value'] in dept_data['dept']:
                    dept_data['dept_data']['not_eligible'] = dept_data['dept_data']['not_eligible'] + 1
                    dept_data['dept_data']['total_employee'] = dept_data['dept_data']['total_employee'] + 1

                    data['not_eligible'] = data['not_eligible'] + 1
                    data['total_employee'] = data['total_employee'] + 1
                else:
                    dept_data['dept'] = emp['dept__value']
                    dept_data['dept_data'] = {'not_filled': 0, 'filled': 0, 'total_approved': 0, 'total_employee': 1, 'not_eligible': 1,'not_recommendable':0}

                    data['not_eligible'] = data['not_eligible'] + 1
                    data['total_employee'] = data['total_employee'] + 1
            # elif 'NOT RECOMMENDABLE' in emp_status:
            #     if emp['dept__value'] in dept_data['dept']:
            #         dept_data['dept_data']['not_recommendable'] = dept_data['dept_data']['not_recommendable'] + 1
            #         dept_data['dept_data']['total_employee'] = dept_data['dept_data']['total_employee'] + 1

            #         data['not_recommendable'] = data['not_recommendable'] + 1
            #         data['total_employee'] = data['total_employee'] + 1
            #     else:
            #         dept_data['dept'] = emp['dept__value']
            #         dept_data['dept_data'] = {'not_filled': 0, 'filled': 0, 'total_approved': 0, 'total_employee': 1, 'not_eligible': 0,'not_recommendable':1}

            #         data['not_recommendable'] = data['not_recommendable'] + 1
            #         data['total_employee'] = data['total_employee'] + 1

        data['dept_data'].append(dept_data)
    return data


def get_proposed_increment_faculty_new(emp_id, level, session):
    data = {'increment_amount': 0, 'increment_type': '---', 'promoted_to': '---', 'estimated_gross_salary': 0}
    qry = FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level),session=session).exclude(status="DELETE").values('increment_type', 'id', 'increment_amount', 'promoted_to__value').order_by('-id')
    if len(qry) > 0:
        data['increment_type'] = qry[0]['increment_type']
        data['increment_amount'] = qry[0]['increment_amount']
        data['promoted_to'] = qry[0]['promoted_to__value']
        emp_salary_type = get_salary_type(emp_id, session, {})
        if len(emp_salary_type) > 0:
            salary_type = emp_salary_type['salary_type__value']
        else:
            salary_type = '---'
        salary = get_increment_in_salary(data['increment_type'], emp_id, session, salary_type, data['increment_amount'])
        data['estimated_gross_salary'] = salary['estimated_salary']
    return data




def get_total_hod_awarded_marks_new(emp_id, session, session_name, level):
    total_marks = 0
    # overall_total = 0
    data = {'cat1': 0, 'cat2': 0, 'cat3': 0}
    level = int(level)
    fac_app_id = FacultyAppraisal.objects.filter(emp_id=emp_id, session=session, status="SUBMITTED", form_filled_status='Y').exclude(status="DELETE").values_list('id', flat=True).order_by('-id')
    approval_status = FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=1).exclude(status="DELETE").exclude(approval_status="REVIEW").values_list('approval_status', flat=True).order_by('-approval_status')
    if len(fac_app_id) > 0 and len(approval_status) > 0:
        for cat in data.keys():
            qry = list(FacAppCatWiseData.objects.filter(category=cat,fac_app_id=fac_app_id[0]).exclude(status=0).values("score_awarded"))
            cat_total = sum([float(t['score_awarded']) for t in qry])
            data[cat] = float(cat_total)
            if 'cat1' in cat:
                qry1=list(FacAppAcadData.objects.filter(fac_app_id=fac_app_id[0]).exclude(status=0).values("score_awarded"))
                data[cat] = data[cat]+float(qry1[0]['score_awarded'])
            total_marks += round(data[cat],2) 
    return [total_marks,data]



def score_calculation_of_cat3_per_report_new(ach_type, qry, session,emp_id):
    data = {'total': 0}
    if 'RESEARCH PAPER IN JOURNAL' in ach_type:
        experience = get_net_experience(emp_id)
        if 'years' in experience[0]:

            if int(experience[0].split(" ")[0])>3:
                experience= True
        else:
            experience=False
        sub_cat = ['SCI','SCI-E','SSCI','ESCI','SCOPOUS']       
        for q in qry:
            if 'UGC RECOMMENDED' not in q['journal_details__sub_category__value']:
                if q['journal_details__sub_category__value'] in sub_cat:
                    if 'SINGLE AUTHOR' in q['author__value']:
                        if q['impact_factor'] is not None:
                            if q['impact_factor']>=0.75:
                                q['score_claimed'] = 23
                            elif q['impact_factor']>=0.5 and q['impact_factor']<0.75:
                                q['score_claimed'] = 21
                            elif q['impact_factor']<0.5:
                                q['score_claimed'] = 19
                            else:
                                q['score_claimed']=15
                        else:
                            q['score_claimed'] = 15
                    elif 'FIRST AUTHOR' in q['author__value'] or 'SUPERVISOR' in q['author__value']:
                        if q['impact_factor'] is not None:
                            if q['impact_factor']>=0.75:
                                q['score_claimed'] = 17
                            elif q['impact_factor']>=0.5 and q['impact_factor']<0.75:
                                q['score_claimed'] = 15
                            elif q['impact_factor']<0.5:
                                q['score_claimed'] = 13
                            else:
                                q['score_claimed']= 9
                        else:
                            q['score_claimed'] = 9
                    elif 'CO-AUTHOR' in q['author__value']:
                        if q['impact_factor'] is not None:
                            if q['impact_factor']>=0.75:
                                q['score_claimed'] = 14
                            elif q['impact_factor']>=0.5 and q['impact_factor']<0.75:
                                q['score_claimed'] = 12
                            elif q['impact_factor']<0.5:
                                q['score_claimed'] = 10
                            else:
                                q['score_claimed']= 6
                        else:
                            q['score_claimed'] = 6
                elif 'UGC RECOMMENDED' in q['journal_details__sub_category__value']:
                    q['score_claimed'] = 2
            elif 'UGC RECOMMENDED' in q['journal_details__sub_category__value'] and experience== False:
                q['score_claimed']=2
            else:
                q['score_claimed'] = 0

            data['total'] = data['total']+q['score_claimed']
    elif 'RESEARCH PAPER IN CONFERENCE' in ach_type:
        for q in qry:
            if q['author__value'] is not None:
                if 'INTERNATIONAL' in q['conference_detail__type_of_conference__value']:
                    if 'SINGLE AUTHOR' in q['author__value']:
                        q['score_claimed']=10
                    elif 'FIRST AUTHOR' in q['author__value'] or 'SUPERVISOR' in q['author__value']:
                        q['score_claimed']=6
                    elif 'CO-AUTHOR' in q['author__value']:
                        q['score_claimed']=4
                    else:
                        q['score_claimed'] = 0
                elif 'NATIONAL' in q['conference_detail__type_of_conference__value']:
                    if 'SINGLE AUTHOR' in q['author__value']:
                        q['score_claimed']=7.5
                    elif 'FIRST AUTHOR' in q['author__value'] or 'SUPERVISOR' in q['author__value']:
                        q['score_claimed']=4.5
                    elif 'CO-AUTHOR' in q['author__value']:
                        q['score_claimed']=3.5
                    else:
                        q['score_claimed'] =0 
                else:
                    q['score_claimed'] = 0
            else:
                q['score_claimed'] = 0

            data['total'] = data['total']+q['score_claimed']
    elif 'BOOKS' in ach_type:
        for q in qry:
            if 'FIRST AUTHOR' in q['author__value']:
                if 'INTERNATIONAL' in q['publisher_type__value']:
                    if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
                        q['score_claimed'] = 5*0.6
                    elif 'BOOK' in q['role_for__value']:
                        q['score_claimed'] = 20*0.6
                elif 'NATIONAL' in q['publisher_type__value']:
                    if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
                        q['score_claimed'] = 2*0.6
                    elif 'BOOK' in q['role_for__value']:
                        q['score_claimed'] = 10*0.6
                elif 'REGIONAL' in q['publisher_type__value']:
                    if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
                        q['score_claimed'] = 1*0.6
                    elif 'BOOK' in q['role_for__value']:
                        q['score_claimed'] = 5*0.6
            else :
                if 'INTERNATIONAL' in q['publisher_type__value']:
                    if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
                        q['score_claimed'] = 5*0.4
                    elif 'BOOK' in q['role_for__value']:
                        q['score_claimed'] = 20*0.4
                elif 'NATIONAL' in q['publisher_type__value']:
                    if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
                        q['score_claimed'] = 2*0.4
                    elif 'BOOK' in q['role_for__value']:
                        q['score_claimed'] = 10*0.4
                elif 'REGIONAL' in q['publisher_type__value']:
                    if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
                        q['score_claimed'] = 1*0.4
                    elif 'BOOK' in q['role_for__value']:
                        q['score_claimed'] = 5*0.4

            data['total'] = data['total']+q['score_claimed']
    elif 'PROJECTS/CONSULTANCY' in ach_type:
        for q in qry:
            q['period'] = get_period((q['end_date']-q['start_date']).days)
            if 'PROPOSED' not in q['project_status__value']:
                if q['principal_investigator'] is not None and q['co_principal_investigator'] is not None:
                    if 'SELF' in q['principal_investigator'].upper() and 'SELF' in q['co_principal_investigator'].upper():
                        if q['amount']>=3000000:
                            q['score_claimed'] = 20
                        elif q['amount'] >= 500000 and q['amount']<3000000:
                            q['score_claimed'] = 15
                        elif q['amount'] >=50000 and q['amount']<500000:
                            q['score_claimed'] = 10
                        else:
                            q['score_claimed'] = 0
                    elif 'SELF' in q['principal_investigator'].upper() and 'OTHER' in q['co_principal_investigator'].upper():
                        if q['amount']>=3000000:
                            q['score_claimed'] = 12*0.6
                        elif q['amount'] >= 500000 and q['amount']<3000000:
                            q['score_claimed'] = 9*0.6
                        elif q['amount'] >=50000 and q['amount']<500000:
                            q['score_claimed'] = 6*0.6
                        else:
                            q['score_claimed'] = 0
                    elif 'OTHER' in q['principal_investigator'].upper() and 'SELF' in q['co_principal_investigator'].upper():
                        if q['amount']>=3000000:
                            q['score_claimed'] = 8*0.4
                        elif q['amount'] >= 500000 and q['amount']<3000000:
                            q['score_claimed'] = 6*0.4
                        elif q['amount'] >=50000 and q['amount']<500000:
                            q['score_claimed'] = 4*0.4
                        else:
                            q['score_claimed'] = 0
                    else:
                        q['score_claimed']=0
                else:
                    q['score_claimed']=0
            else:
                q['score_claimed'] = 0

            data['total'] = data['total']+q['score_claimed']

    elif 'PATENT' in ach_type:
        for q in qry:
            if 'IF FILED' not in q['patent_details__patent_status__value']:
                if q['patent_details__patent_applicant_name'] is not None and q['patent_details__patent_co_applicant_name'] is not None:
                    if 'SELF' in q['patent_details__patent_applicant_name'].upper() and 'SELF' in q['patent_details__patent_co_applicant_name'].upper():
                        if 'INTERNATIONAL' in q['patent_details__level__value']:
                            if 'IF GRANTED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 40
                            if 'PUBLISHED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 30
                        elif  'NATIONAL' in q['patent_details__level__value']:
                            if 'IF GRANTED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 25
                            if 'PUBLISHED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 20
                        else:
                            q['score_claimed']=0
                    elif 'SELF' in q['patent_details__patent_applicant_name'].upper() and 'OTHER' in q['patent_details__patent_co_applicant_name'].upper():
                        if 'INTERNATIONAL' in q['patent_details__level__value']:
                            if 'IF GRANTED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 24*0.6
                            if 'PUBLISHED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 18*0.6
                        elif  'NATIONAL' in q['patent_details__level__value']:
                            if 'IF GRANTED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 15*0.6
                            if 'PUBLISHED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 12*0.6
                        else:
                            q['score_claimed']=0
                    elif 'OTHER' in q['patent_details__patent_applicant_name'].upper() and 'SELF' in q['patent_details__patent_co_applicant_name'].upper():
                        if 'INTERNATIONAL' in q['patent_details__level__value']:
                            if 'IF GRANTED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 16*0.4
                            if 'PUBLISHED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 12*0.4
                        elif  'NATIONAL' in q['patent_details__level__value']:
                            if 'IF GRANTED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 10*0.4
                            if 'PUBLISHED' in q['patent_details__patent_status__value']:
                                q['score_claimed'] = 8*0.4
                        else:
                            q['score_claimed']=0
                    else:
                        q['score_claimed']=0
                else:
                    q['score_claimed']=0
            else:
                q['score_claimed'] = 0
            data['total'] = data['total']+q['score_claimed']

    elif 'RESEARCH GUIDANCE / PROJECT GUIDANCE' in ach_type:
        for q in qry:
            if q['degree__value'] is not None and 'RESEARCH (PH. D.)' in q['degree__value'] and q['guidance_status__value'] is not None and q['guidance_for__value'] is not None:
                if 'AWARDED' in q['guidance_status__value'] and 'DEGREE' in q['guidance_for__value']:
                    q['score_claimed'] =  10
                elif 'SUBMITTED' in q['guidance_status__value'] and 'THESIS' in q['guidance_for__value']:
                    q['score_claimed'] =  7
                else:
                    q['score_claimed'] =0 
            else:
                q['score_claimed'] = 0
            data['total'] = data['total']+q['score_claimed']
    elif 'TRAINING AND DEVELOPMENT PROGRAM' in ach_type:
        for q in qry:
            week_check_days =(q['to_date']-q['from_date'])
            q['days'] =  get_period(week_check_days.days)
            if int(week_check_days.days)>=5:
                if 'ATTENDED' in q['role__value']:
                    if  q['training_sub_type__value'] is not None:
                        if 'OTHER THAN ICT MODE' in q['training_sub_type__value']:
                            q['score_claimed'] = 2
                        elif 'ICT MODE' in q['training_sub_type__value']:
                            q['score_claimed'] = 1
                    else:
                        q['score_claimed'] = 0
                elif 'ORGANIZED' in tr_ach['role__value']:
                    if  q['training_sub_type__value'] is not None:
                        if 'ICT MODE' in q['training_sub_type__value']:
                            q['score_claimed'] = 2
                        elif 'OTHER THAN ICT MODE' in q['training_sub_type__value']:
                            q['score_claimed'] = 3
                    else:
                        q['score_claimed'] = 0
                else :
                    q['score_claimed'] = 0
            else:
                q['score_claimed'] = 0

            data['total'] = data['total']+q['score_claimed']
    elif 'LECTURES AND TALKS' in ach_type:
        for q in qry:
            if 'INTERNATIONAL' in q['type_of_event__value']:
                q['score_claimed'] = 5
            elif 'NATIONAL' in q['type_of_event__value']:
                q['score_claimed'] = 2.5
            else:
                q['score_claimed'] = 0
            data['total'] = data['total']+q['score_claimed']
    elif 'DESIGN' in ach_type:
        for q in qry:
            if 'IF FILED' not in q['design_status__value']:
                if q['design_applicant_name'] is not None and q['design_co_applicant_name'] is not None:
                    if 'SELF' in q['design_applicant_name'].upper() and 'SELF' in q['design_co_applicant_name'].upper():
                        if 'INTERNATIONAL' in q['design_level__value']:
                            if 'IF GRANTED' in q['design_status__value']:
                                q['score_claimed'] = (30)
                            if 'PUBLISHED' in q['design_status__value']:
                                q['score_claimed'] = 20
                        elif  'NATIONAL' in q['design_level__value']:
                            if 'IF GRANTED' in q['design_status__value']:
                                q['score_claimed'] = 20
                            if 'PUBLISHED' in q['design_status__value']:
                                q['score_claimed'] = 15
                    elif 'SELF' in q['design_applicant_name'].upper() and 'OTHER' in q['design_co_applicant_name'].upper():
                        if 'INTERNATIONAL' in q['design_level__value']:
                            if 'IF GRANTED' in q['design_status__value']:
                                q['score_claimed'] = 18*0.6
                            if 'PUBLISHED' in q['design_status__value']:
                                q['score_claimed'] = 12*0.6
                        elif  'NATIONAL' in q['design_level__value']:
                            if 'IF GRANTED' in q['design_status__value']:
                                q['score_claimed'] = 12*0.6
                            if 'PUBLISHED' in q['design_status__value']:
                                q['score_claimed'] = 9*0.6
                    elif 'OTHER' in q['design_applicant_name'].upper() and 'SELF' in q['design_co_applicant_name'].upper():
                        if 'INTERNATIONAL' in q['design_level__value']:
                            if 'IF GRANTED' in q['design_status__value']:
                                q['score_claimed'] = 12*0.4
                            if 'PUBLISHED' in q['design_status__value']:
                                q['score_claimed'] = 8*0.4
                        elif  'NATIONAL' in q['design_level__value']:
                            if 'IF GRANTED' in q['design_status__value']:
                                q['score_claimed'] = 8*0.4
                            if 'PUBLISHED' in q['design_status__value']:
                                q['score_claimed'] = 6*0.4
            else:
                q['score_claimed'] = 0

            data['total'] = data['total']+q['score_claimed']

    data['total'] = round(data['total'],2)
    return [qry, data]









