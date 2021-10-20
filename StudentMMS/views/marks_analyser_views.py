from django.http import JsonResponse
import json
# import datetime
from datetime import datetime
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from StudentMMS.constants_functions import requestType
from Registrar.models import StudentPrimDetail, Semtiming
from django.db.models import Avg, F, Count, Sum
from StudentAcademics.models import *
import math
from Registrar.views import get_course, get_semester, get_section
from Registrar.models import StudentSemester, CourseDetail, Semtiming, Sections
from login.views import checkpermission, generate_session_table_name
from StudentPortal.views import get_branch
from Store_data.views.functions import get_overall_attendance
# from aar.dept_achievement import get_all_emp
from StudentMMS.views.mms_function_views import get_ctrule_wise_student_marks,get_student_marks_updated,get_student_subject_att_marks,get_student_subject_ta_marks,get_student_subject_att_marks_new,get_student_subject_extra_bonus_marks,get_student_subject_bonus_marks,get_student_marks_new,get_student_marks
from StudentMMS.views.harsh_views import fetch_bonus_marks
# Note:for AS treat selected branch as selcted dept
# main function for marks
def overall_marks_analyser(request):
    response_values = []
    if checkpermission(request, [rolesCheck.ROLE_MARKS_ANALYSIS_CORDINATOR]) == statusCodes.STATUS_SUCCESS:
        session = request.session['Session_id']
        if requestMethod.GET_REQUEST(request):  # list for drop down
            response_values = {}
            if (requestType.custom_request_type(request.GET, 'get_list')):
                session_range = Semtiming.objects.filter(
                    sem_start__gte="2018-06-01").values('uid', 'session', 'session_name')
                response_values['session_range'] = list(session_range)
                response_values['course'] = get_course()
            elif(requestType.custom_request_type(request.GET, 'get_course')):
                response_values['course'] = get_course()
            elif (requestType.custom_request_type(request.GET, 'get_branch')):
                course_list = request.GET['course'].split(',')
                response_values = get_branch(course_list)
            elif (requestType.custom_request_type(request.GET, 'get_sem')):
                branch_list = request.GET['dept'].split(',')
                course_list = request.GET['course'].split(',')
                # here seesion can be current session and in anlayser we can use session dropdown also.
                # session = ["1920e"]
                session= request.session['Session_name']
                response_values = get_sem_coursewise(branch_list, session,course_list)
            elif (requestType.custom_request_type(request.GET, 'get_section')):
                branch_list = request.GET['dept'].split(',')
                sem_list = request.GET['sem'].split(',')
                response_values = get_section_new(branch_list, sem_list)
            else:
                response_values = statusMessages.MESSAGE_BAD_REQUEST
            return functions.RESPONSE(response_values, statusCodes.STATUS_SUCCESS)
        if requestMethod.POST_REQUEST(request):  # for getting results
            body = json.loads(request.body)
            locked = {'locked_session': "", 'locked_course': "", 'locked_branch': "", 'locked_sem': "",
                      'locked_subject': "", 'locked_section': "", 'locked_student': ''}  # dict for sending levels freezed
########################################  COURSE    ##################################################
            if(body['type_request'] == 'Totalmarks_course'):
                # {'type_request': 'Totalmarks_course', 'selected_session': ['1819e', '1920o', '1920e'], 'selected_course': [12, 13]}
                id_list = [['course_id']]  # for giving id for chart
                # below loop is for creating the format of list in which data course
                data = [['COURSE']]
                for session in body['selected_session']:
                    data[0].append(session)
                    id_list[0].append(session)
                    locked['locked_session'] += str(session)
                    if session == body['selected_session'][-1]:
                        break
                    else:
                        locked['locked_session'] += ','
                row = 0
                for course in body['selected_course']:
                    row += 1
                    course_name = list(CourseDetail.objects.filter(
                        course=course).values("course__value").distinct())
                    data.append([course_name[0]['course__value']])
                    id_list.append([course])
                    average_all = average_query(
                        course, body['type_request'], body)
                    for avg in average_all:
                        data[row].append(avg)
                        id_list[row].append(avg)
                response_values.append(data)
                response_values.append(id_list)
                # response_values=[[["COURSE", "1920e", "1819e"], ["B.TECH", 77.38095238095238, 73.94404827207899], ["B.PHARMA", 76.05432451751251, 75.96618357487924]], [["course_id", "1920e", "1819e"], [12, 77.38095238095238, 73.94404827207899], [13, 76.05432451751251, 75.96618357487924]]]

##########################################    BRANCH    ######################################################
            elif (body['type_request'] == 'Totalmarks_branch'):
                # {"type_request": "Totalmarks_branch", "selected_session": ["1819e", "1920o", "1920e"], "selected_course": [12], "selected_branch": [], "selected_section": [], "selected_sem": [], "selected_subject": []}
                branch_list = []  # for fetching branch data from selected course
                branch_dict = get_branch(body['selected_course'])
                for dictn in branch_dict:
                    id = dictn['uid']
                    branch_list.append(id)
                id_list = [['branch_id']]  # for giving id for chart
                # below loop is for creating the format of list in which data branch
                data = [['branch']]
                body['selected_branch'] = branch_list
                for session in body['selected_session']:
                    data[0].append(session)
                    id_list[0].append(session)
                    locked['locked_session'] += str(session)
                    if session == body['selected_session'][-1]:
                        break
                    else:
                        locked['locked_session'] += ','
                course_name = CourseDetail.objects.filter(
                    course__in=body['selected_course']).values_list('course__value', flat=True).distinct()
                locked['locked_course'] += str(course_name[0])
                row = 0
                for branch in branch_list:
                    row += 1
                    branch_name = list(CourseDetail.objects.filter(
                        uid=branch).values("dept__value").distinct())
                    data.append([branch_name[0]['dept__value']])
                    average_all = average_query(
                        branch, body['type_request'], body)
                    id_list.append([branch])
                    for avg in average_all:
                        data[row].append(avg)
                        id_list[row].append(avg)
                response_values.append(data)
                response_values.append(id_list)
                # response_values=[[["branch", "1920e"], ["KSOP", 76.05432451751251]], [["branch_id", "1920e"], [50, 76.05432451751251]]]

#########################################    SEMESTER      ########################
            elif (body['type_request'] == 'Totalmarks_sem'):
                sem_list = []  # for fetching sem data from selected branch
                sem_dict = get_sem_(
                    body['selected_branch'], body['selected_session'], body['selected_course'])
                sem_list = sem_dict['sem']
                body['selected_sem'] = sem_list
                id_list = [['semester_id']]
                # below loop is for creating the format of list in which data semester
                data = [['semester']]
                for session in body['selected_session']:
                    data[0].append(session)
                    id_list[0].append(session)
                    locked['locked_session'] += str(session)
                    if session == body['selected_session'][-1]:
                        break
                    else:
                        locked['locked_session'] += ','
                course_name = CourseDetail.objects.filter(
                    course__in=body['selected_course']).values_list('course__value', flat=True).distinct()
                locked['locked_course'] += str(course_name[0])
                branch_name = list(CourseDetail.objects.filter(
                    uid__in=body['selected_branch']).values("dept__value").distinct())
                locked['locked_branch'] += str(branch_name[0]
                                               ['dept__value'])
                row = 0
                for sem in body['selected_sem']:
                    row += 1
                    data.append(['Semester:'+str(sem)])
                    average_all = average_query(
                        sem, body['type_request'], body)
                    id_list.append([sem])
                    for avg in average_all:
                        data[row].append(avg)
                        id_list[row].append(avg)
                response_values.append(data)
                response_values.append(id_list)
                # response_values=[[["semester", "1920e"], ["2", 0], ["4", 75.13513513513513], ["6", 80.10000000000001], ["8", 0]], [["semester_id", "1920e"], [2, 0], [4, 75.13513513513513], [6, 80.10000000000001], [8, 0]]]

############################################   SUBJECT  #####################################
            elif (body['type_request'] == 'Totalmarks_subject'):
                # {"type_request": "Totalmarks_subject", "selected_session": ["1819e", "1920e"], "selected_course": [12], "selected_branch": [41], "selected_section": [], "selected_sem": [4], "selected_subject": []}

                id_list = [['subject_id']]  # for giving id for chart
                # below loop is for creating the format of list in which data course
                data = [['subject']]
                for session in body['selected_session']:
                    data[0].append(session)
                    id_list[0].append(session)
                    locked['locked_session'] += str(session)
                    if session == body['selected_session'][-1]:
                        break
                    else:
                        locked['locked_session'] += ','
                course_name = CourseDetail.objects.filter(
                    course__in=body['selected_course']).values_list('course__value', flat=True).distinct()
                locked['locked_course'] += str(course_name[0])
                branch_name = list(CourseDetail.objects.filter(
                    uid__in=body['selected_branch']).values("dept__value").distinct())
                locked['locked_branch'] += str(branch_name[0]
                                               ['dept__value'])
                locked['locked_sem'] = str(body['selected_sem'][0])
                row = 0
                subject_list = get_subject(
                    body['selected_sem'], session, body['selected_branch'])
                for subject in subject_list:
                    row += 1
                    average_all = average_query(
                        subject['id'], body['type_request'], body)
                    data.append(
                        [subject['sub_name']+' '+subject['sub_alpha_code']+('('+subject['sub_num_code']+')')])
                    id_list.append([(subject['id'])])
                    for avg in average_all:
                        data[row].append(avg)
                response_values.append(data)
                response_values.append(id_list)
          # response_values=[[["subject", "1920e"], ["PHARMACEUTICAL ORGANIC CHEMISTRY-III THEORY  BP(401T)", 78.0], ["MEDICINAL CHEMISTRY-I THEORY  BP(402T)", 77.0], ["PHYSICAL PHARMACEUTICS-II THEORY  BP(403T)", 76.0], ["PHARMACOLOGY-I THEORY  BP(404T)", 76.0], ["PHARMACOGNOSY-I THEORY  BP(405T)", 77.0], ["MEDICINAL CHEMISTRY-I PRACTICAL  BP(406P)", 90.0], ["PHYSICAL PHARMACEUTICS-II PRACTICAL  BP(407P)", 90.0], ["PHARMACOLOGY-I PRACTICAL  BP(408P)", 90.0], ["PHARMACOGNOSY-I PRACTICAL  BP(409P)", 90.0], ["SOFT SKILLS  SS(410)", 0], ["GPAT  BP(411)", 0], ["BIOMEDICAL WASTE  BP(412)", 0]], [["subject_id", "1920e"], ["401T", 78.0], ["402T", 77.0], ["403T", 76.0], ["404T", 76.0], ["405T", 77.0], ["406P", 90.0], ["407P", 90.0], ["408P", 90.0], ["409P", 90.0], ["410", 0], ["411", 0], ["412", 0]]]

###############################################   SECTION_SUBJECTWISE    #################################
            # {"type_request": "Totalmarks_section_subjectwise", "selected_session": ["1819e", "1920e"], "selected_course": [12], "selected_branch": [41], "selected_section": [], "selected_sem": [4], "selected_subject": ["LASER SYSTEM AND APPLICATION"]}
            elif (body['type_request'] == 'Totalmarks_section_subjectwise'):
                section_dict = get_sec(
                    body['selected_branch'], body['selected_sem'])
                id_list = []  # for giving id for chart
                data = [['subject-section']]
                for session in body['selected_session']:
                    data[0].append(session)
                    locked['locked_session'] += str(session)
                    if session == body['selected_session'][-1]:
                        break
                    else:
                        locked['locked_session'] += ','
                course_name = CourseDetail.objects.filter(
                    course__in=body['selected_course']).values_list('course__value', flat=True).distinct()
                locked['locked_course'] += str(course_name[0])
                branch_name = list(CourseDetail.objects.filter(
                    uid__in=body['selected_branch']).values("dept__value").distinct())
                locked['locked_branch'] += str(branch_name[0]
                                               ['dept__value'])
                locked['locked_sem'] = str(body['selected_sem'][0])
                row = 0
                subjectinfo = generate_session_table_name(
                    "SubjectInfo_", body['selected_session'][0])
                subjectss = subjectinfo.objects.filter(id__in=body['selected_subject']).values(
                    'sub_name', 'sub_alpha_code', 'sub_num_code')
                locked['locked_subject'] = str(
                    subjectss[0]['sub_name']+"("+subjectss[0]['sub_alpha_code']+" "+subjectss[0]['sub_num_code']+")")
                for section in section_dict:
                    row += 1
                    data.append([section['section']])
                    average_all = average_query(
                        section['section'], body['type_request'], body)
                    for avg in average_all:
                        data[row].append(avg)
                response_values.append(data)
                response_values.append(id_list)

#########################################     SECTION       ################################
            elif(body['type_request'] == 'Totalmarks_section'):
                # {'type_request': 'Totalmarks_section', 'selected_session': ['1819e', '1920e'], 'selected_course': [12], 'selected_branch': [41], 'selected_section': [], 'selected_sem': [4], 'selected_subject': []}
                section_dict = get_sec(
                    body['selected_branch'], body['selected_sem'])
                #  (section_dict)
                id_list = [['section_id']]  # for giving id for chart
                # below loop is for creating the format of list in which data course
                data = [['section']]
                for session in body['selected_session']:
                    data[0].append(session)
                    id_list[0].append(session)
                    locked['locked_session'] += str(session)
                    if session == body['selected_session'][-1]:
                        break
                    else:
                        locked['locked_session'] += ','
                course_name = CourseDetail.objects.filter(
                    course__in=body['selected_course']).values_list('course__value', flat=True).distinct()
                locked['locked_course'] += str(course_name[0])
                branch_name = list(CourseDetail.objects.filter(
                    uid__in=body['selected_branch']).values("dept__value").distinct())
                locked['locked_branch'] += str(branch_name[0]
                                               ['dept__value'])
                locked['locked_sem'] = str(body['selected_sem'][0])
                row = 0
                for section in section_dict:
                    row += 1
                    data.append([section['section']])
                    id_list.append([section['section']])
                    average_all = average_query(
                        section['section'], body['type_request'], body)
                    for avg in average_all:
                        data[row].append(avg)
                        id_list[row].append(avg)
                response_values.append(data)
                response_values.append(id_list)
                # reponse_values=[[["section", "1920e"], ["A", 73.67567567567568], ["B", 75.02702702702703]], [["section_id", "1920e"], ["A", 73.67567567567568], ["B", 75.02702702702703]]]
#############################################  SUBJECT_SECTIONWISE   ####################################
            elif (body['type_request'] == 'Totalmarks_subject_sectionwise'):
                # below loop is for creating the format of list in which data course
                data = [['section-subject']]
                for session in body['selected_session']:
                    data[0].append(session)
                    locked['locked_session'] += str(session)
                    if session == body['selected_session'][-1]:
                        break
                    else:
                        locked['locked_session'] += ','
                course_name = CourseDetail.objects.filter(
                    course__in=body['selected_course']).values_list('course__value', flat=True).distinct()
                locked['locked_course'] += str(course_name[0])
                branch_name = list(CourseDetail.objects.filter(
                    uid__in=body['selected_branch']).values("dept__value").distinct())
                locked['locked_branch'] += str(branch_name[0]
                                               ['dept__value'])
                locked['locked_sem'] = str(body['selected_sem'][0])
                locked['locked_section'] = (Sections.objects.filter(
                    section__in=body['selected_section']).values_list('section'))[0][0]
                row = 0
                id_list = []
                for session in body['selected_session']:
                    subject_list = get_subject(
                        body['selected_sem'], session, body['selected_branch'])
                    for subject in subject_list:
                        row += 1
                        data.append(
                            [subject['sub_name']+' '+subject['sub_alpha_code']+('('+subject['sub_num_code']+')')])
                        average_all = average_query(
                            subject['id'], body['type_request'], body)
                        for avg in average_all:
                            data[row].append(avg)
                response_values.append(data)
                response_values.append(id_list)

####################################   STUDENT_LIST_SECTIONWISE    #########################################
            elif(body['type_request'] == 'student_list'):
                data = []
                session=request.session['Session_name']
                student_list = student_list_sectionwise(
                    session, body['selected_section'])
                for student in student_list:
                    name = {}
                    std_name = student['uniq_id__name'] + \
                        ' ( '+student['uniq_id__uni_roll_no']+' )'
                    name['name'] = std_name
                    name['unique_id'] = student['uniq_id']
                    data.append(name)
                response_values.append(data)
######################################    INDIVIDUAL STUDENT_MARKS   ##########################
            elif (body['type_request'] == 'Totalmarks_individualstudent'):
                # here seesion can be current session and in anlayser we can use session dropdown also.
                course_name = CourseDetail.objects.filter(
                    course__in=body['selected_course']).values_list('course__value', flat=True).distinct()
                locked['locked_course'] += str(course_name[0])
                branch_name = list(CourseDetail.objects.filter(
                    uid__in=body['selected_branch']).values("dept__value").distinct())
                locked['locked_branch'] += str(branch_name[0]['dept__value'])
                locked['locked_sem'] = str(StudentSemester.objects.filter(
                    sem_id__in=body['selected_sem']).values('sem')[0]['sem'])
                locked['locked_section'] = (Sections.objects.filter(
                    section_id__in=body['selected_section']).values('section')[0]['section'])
                student = StudentPrimDetail.objects.filter(
                    uniq_id__in=body['selected_student']).values('name', 'uni_roll_no')
                locked['locked_student'] = student[0]['name'] + \
                    '( '+student[0]['uni_roll_no']+' )'
                # session = ["1920e"]
                session = [request.session['Session_name']]
                session_list, ind_stu_session, marks_list = [], [], []
                data = [['semester']]
                data[0].append('Percent')
                id_list = [['sem_id']]
                id_list[0].append('percent')
                sem_name = StudentSemester.objects.filter(
                    sem_id__in=body['selected_sem']).values_list('sem', flat=True)
                sem_dict = individual_sem(
                    body['selected_branch'], sem_name)
                qry = (Semtiming.objects.all().values(
                    'session_name').order_by('sem_start'))
                for sess in qry:
                    ses = sess['session_name']
                    session_list.append(ses)
                index = session_list.index(session[0])
                for sem in range(1, len(sem_dict)+1):
                    ind_stu_session.append(
                        session_list[index-(len(sem_dict)-1)])
                    index += 1
                col = 0
                for sem in sem_dict:
                    section = Sections.objects.filter(
                        sem_id=sem['sem_id']).values('section_id')
                for i in range(len(sem_dict)):
                    col += 1
                    sesion = ind_stu_session[i]
                    if sesion ==ind_stu_session[-1] :
                        continue
                    data.append(['Semester '+str(sem_dict[i]['sem'])])
                    id_list.append([sem_dict[i]['sem_id']])
                    if sesion < '1819e':#here session is before 1819o but as in table 1819e come before 1819o
                        final_avg=0
                        id_list[col].append(final_avg)
                        data[col].append(final_avg)
                        continue
                    
                    Studentfinalmarks = generate_session_table_name(
                        "StudentFinalMarksStatus_", sesion)
                    qry_marks = Studentfinalmarks.objects.filter(uniq_id__in=body['selected_student']).exclude(Year_obtained__isnull=True, Year_total__isnull=True).aggregate(avg_obt=Avg("Year_obtained"),
                                                                                                                                                                                avg_total=Avg("Year_total"))
                    marks_list.append(qry_marks)
                    if "e" in sesion:
                        odd_sem_marks = marks_list[-2]
                        if((qry_marks['avg_obt']) == None or (qry_marks['avg_total']) == None):
                            final_avg = 0
                        else:
                            final_avg = ((int(qry_marks['avg_obt'] - odd_sem_marks['avg_obt']) / int(
                                qry_marks['avg_total'] - odd_sem_marks['avg_total'])) * 100)
                    else:
                        final_avg = average_calculation(qry_marks)
                    if final_avg == None:
                        final_avg = 0
                    data[col].append(final_avg)
                    id_list[col].append(final_avg)
                response_values.append(data)
                response_values.append(id_list)
####################################    INDIVIDUAL STUDENT MARKS SEMESTER_SPECIFIC     ###########################
            elif (body['type_request'] == 'Totalmarks_indstd_semesterwise'):
                id_list = [['subject_id']]  # for giving id for chart
                id_list[0].append('percent')
                # below loop is for creating the format of list in which data course
                course_name = CourseDetail.objects.filter(
                    course__in=body['selected_course']).values_list('course__value', flat=True).distinct()
                locked['locked_course'] += str(course_name[0])
                branch_name = list(CourseDetail.objects.filter(
                    uid__in=body['selected_branch']).values("dept__value").distinct())
                locked['locked_branch'] += str(branch_name[0]
                                               ['dept__value'])
                locked['locked_sem'] = str(StudentSemester.objects.filter(
                    sem_id__in=body['selected_sem']).values('sem')[0]['sem'])
                locked['locked_section'] = (Sections.objects.filter(
                    section_id__in=body['selected_section']).values('section')[0]['section'])
                student = StudentPrimDetail.objects.filter(
                    uniq_id__in=body['selected_student']).values('name', 'uni_roll_no')
                locked['locked_student'] = student[0]['name'] + \
                    '( '+student[0]['uni_roll_no']+' )'
                data = [['subject']]
                data[0].append('percent')
                # session = ["1920e"]
                session= request.session['Session_name']
                individual_session = individual_sesssion(body)
                sem_name = list(StudentSemester.objects.filter(
                    sem_id__in=body['selected_sem']).values_list('sem', flat=True))
                qry = (Semtiming.objects.all().values(
                    'session_name').order_by('session_name'))
                studentSession = generate_session_table_name(
                    'studentSession_', individual_session)
                section_id_ind = studentSession.objects.filter(
                    uniq_id__in=body['selected_student']).values_list('section_id', flat=True)
                if (sem_name[0] == 2) and (body['selected_course']==[12]):
                    body['selected_branch'] = [59]
                    body['selected_sem'] = [312]
                elif (sem_name[0] == 1) and (body['selected_course']==[12]):
                    body['selected_branch'] = [59]
                    body['selected_sem'] = [311]
                subject_list = get_subject_by_semid(
                    body['selected_sem'], individual_session, body['selected_branch'])
                row = 0
                for subject in subject_list:

                    Studentunivesitymarks = generate_session_table_name(
                        'StudentUniversityMarks_', individual_session)

                    qry_subject = Studentunivesitymarks.objects.filter(uniq_id__in=body['selected_student'],uniq_id__sem_id__dept__in=body['selected_branch'], uniq_id__sem_id__in=body['selected_sem'], uniq_id__section_id=section_id_ind[0], subject_id=subject['id']).exclude(external_marks__isnull=True, internal_marks__isnull=True, subject_id__max_university_marks__isnull=True, subject_id__max_ct_marks__isnull=True,
                                                                                                                                                                                                                                             subject_id__max_ta_marks__isnull=True, subject_id__max_att_marks__isnull=True).aggregate(avg_ext=Avg("external_marks"), avg_int=Avg("internal_marks"), avg_max_ext=Avg('subject_id__max_university_marks'), avg_max_ct=Avg('subject_id__max_ct_marks'), avg_max_ta=Avg('subject_id__max_ta_marks'), avg_max_att=Avg('subject_id__max_att_marks'))
                    if((qry_subject['avg_ext'] or qry_subject['avg_int']) == None):
                        final_avg = 0
                    else:
                        row += 1
                        data.append(
                        [subject['sub_name']+' '+subject['sub_alpha_code']+('('+subject['sub_num_code']+')')])
                        id_list.append([subject['id']])
                        total_obt = (
                            qry_subject['avg_ext']+qry_subject['avg_int'])
                        total_ext = (qry_subject['avg_max_ext']+qry_subject['avg_max_ct'] +
                                     qry_subject['avg_max_ta']+qry_subject['avg_max_att'])
                        final_avg = (int(total_obt)/int(total_ext))*100
                        data[row].append(final_avg)
                        id_list[row].append(final_avg)
                response_values.append(data)
                response_values.append(id_list)
#################################     INDIVIDUAL STUDENT EXTERNAL AND INTERNAL SUBJECWISE      ######################################
            elif (body['type_request'] == 'Totalmarks_indstd_subjectwise'):
                session = individual_sesssion(body)
                course_name = CourseDetail.objects.filter(
                    course__in=body['selected_course']).values_list('course__value', flat=True).distinct()
                locked['locked_course'] += str(course_name[0])
                branch_name = list(CourseDetail.objects.filter(
                    uid__in=body['selected_branch']).values("dept__value").distinct())
                locked['locked_branch'] += str(branch_name[0]['dept__value'])
                locked['locked_sem'] = str(StudentSemester.objects.filter(
                    sem_id__in=body['selected_sem']).values('sem')[0]['sem'])
                locked['locked_section'] = (Sections.objects.filter(
                    section_id__in=body['selected_section']).values('section')[0]['section'])
                student = StudentPrimDetail.objects.filter(
                    uniq_id__in=body['selected_student']).values('name', 'uni_roll_no')
                locked['locked_student'] = student[0]['name'] + \
                    '( '+student[0]['uni_roll_no']+' )'
                subjectinfo = generate_session_table_name(
                    "SubjectInfo_", session)
                subjectss = subjectinfo.objects.filter(id__in=body['selected_subject']).values(
                    'sub_name', 'sub_alpha_code', 'sub_num_code','subject_type')
                locked['locked_subject'] = str(
                    subjectss[0]['sub_name']+"("+subjectss[0]['sub_alpha_code']+" "+subjectss[0]['sub_num_code']+")")
                if subjectss[0]['subject_type']!= 84:
                    response_values ={'msg':'THERE IS NO INTERNAL DISTRIBUTION FOR SUBJECTS OTHER THAN THEORY'}
                    return functions.RESPONSE(response_values, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                data = []
                id_list = [['external']]
                id_list.append(['internal'])
                id_list[1].append(
                    'here no id required but for click ivewrittend this')
                external = ind_stu_ext_subject(
                    body['selected_student'], session, body['selected_subject'])
                internal = ind_Stu_int_subject(
                    body['selected_student'], session, body['selected_subject'])
                data.append(external)
                data.append(internal)
                response_values.append(data)
                response_values.append(id_list)

##########################     INDIVIDUAL STUDENT INTERNA CT AND PUE WISE      ###############################
            elif (body['type_request'] == 'Totalmarks_indstd_examwise'):
                session = individual_sesssion(body)
                course_name = CourseDetail.objects.filter(
                    course__in=body['selected_course']).values_list('course__value', flat=True).distinct()
                locked['locked_course'] += str(course_name[0])
                branch_name = list(CourseDetail.objects.filter(
                    uid__in=body['selected_branch']).values("dept__value").distinct())
                locked['locked_branch'] += str(branch_name[0]['dept__value'])
                locked['locked_sem'] = str(StudentSemester.objects.filter(
                    sem_id__in=body['selected_sem']).values('sem')[0]['sem'])
                locked['locked_section'] = (Sections.objects.filter(
                    section_id__in=body['selected_section']).values('section')[0]['section'])
                subjectinfo = generate_session_table_name(
                    "SubjectInfo_", session)
                subjectss = subjectinfo.objects.filter(id__in=body['selected_subject']).values(
                    'sub_name', 'sub_alpha_code', 'sub_num_code','subject_type','max_ct_marks')
                locked['locked_subject'] = str(
                    subjectss[0]['sub_name']+"("+subjectss[0]['sub_alpha_code']+" "+subjectss[0]['sub_num_code']+")")
                student = StudentPrimDetail.objects.filter(
                    uniq_id__in=body['selected_student']).values('name', 'uni_roll_no')
                locked['locked_student'] = student[0]['name'] + \
                    '( '+student[0]['uni_roll_no']+' )'
                id_list = []
                session = individual_sesssion(body)
                exams = get_exam_list(session)
                marks = get_examwise_data(
                    body['selected_student'], exams, body['selected_subject'], session)
                response_values.append(marks[0])
                response_values.append(id_list)
            response_values.append([locked])
            response_values.append([body])
            return functions.RESPONSE(response_values, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(response_values, statusCodes.STATUS_SUCCESS)
    else:
        response_values = statusMessages.MESSAGE_FORBIDDEN
        return functions.RESPONSE(response_values, statusCodes.STATUS_FORBIDDEN)
# query function
# function for calculation of average


def average_query(params, type_request, body):  # params is the value asked
    # params=12 or 41 or A (single value),type request, requestbody
    average_list = []  # for whole list of average i.e for each branch ,course,or sem
    for session_name in body['selected_session']:
        Studentfinalmarks = generate_session_table_name(
            'StudentFinalMarksStatus_', session_name)
        Studentunivesitymarks = generate_session_table_name(
            'StudentUniversityMarks_', session_name)
        if (type_request == 'Totalmarks_course'):
            qry_course = Studentfinalmarks.objects.filter(uniq_id__uniq_id__dept_detail__course__sno=params).exclude(Year_obtained__isnull=True, Year_total__isnull=True).aggregate(avg_obt=Avg("Year_obtained"),
                                                                                                                                                                                    avg_total=Avg("Year_total"))
            final_avg = average_calculation(qry_course)
        elif (type_request == 'Totalmarks_sem'):
            qry_sem = Studentfinalmarks.objects.filter(uniq_id__uniq_id__dept_detail__course__sno__in=body['selected_course'], uniq_id__sem_id__dept__in=body['selected_branch'], uniq_id__sem_id__sem=params).exclude(Year_obtained__isnull=True,
                                                                                                                                                                                                                       Year_total__isnull=True).aggregate(avg_obt=Avg("Year_obtained"), avg_total=Avg("Year_total"))
            final_avg = average_calculation(qry_sem)
        elif (type_request == 'Totalmarks_branch'):

            qry_branch = Studentfinalmarks.objects.filter(uniq_id__uniq_id__dept_detail__course__sno__in=body['selected_course'],
                                                          uniq_id__sem_id__dept=params).exclude(Year_obtained__isnull=True, Year_total__isnull=True).aggregate(avg_obt=Avg("Year_obtained"), avg_total=Avg("Year_total"))
            final_avg = average_calculation(qry_branch)
        elif(type_request == "Totalmarks_section"):
            qry_section = Studentfinalmarks.objects.filter(uniq_id__uniq_id__dept_detail__course__sno__in=body['selected_course'], uniq_id__sem_id__dept__in=body['selected_branch'], uniq_id__sem_id__sem__in=body['selected_sem'], uniq_id__section_id__section=params).exclude(Year_obtained__isnull=True,
                                                                                                                                                                                                                                                                                  Year_total__isnull=True).aggregate(avg_obt=Avg("Year_obtained"), avg_total=Avg("Year_total"))
            final_avg = average_calculation(qry_section)
        elif(type_request == "Totalmarks_subject"):
            qry_subject = Studentunivesitymarks.objects.filter(uniq_id__sem_id__dept__course__in=body['selected_course'], uniq_id__sem_id__dept__in=body['selected_branch'], uniq_id__sem_id__sem__in=body['selected_sem'], subject_id=params).exclude(external_marks__isnull=True,
                                                                                                                                                                                                                                                       internal_marks__isnull=True, subject_id__max_university_marks__isnull=True, subject_id__max_ct_marks__isnull=True, subject_id__max_ta_marks__isnull=True, subject_id__max_att_marks__isnull=True).aggregate(avg_ext=Avg("external_marks"), avg_int=Avg("internal_marks"), avg_max_ext=Avg('subject_id__max_university_marks'), avg_max_ct=Avg('subject_id__max_ct_marks'), avg_max_ta=Avg('subject_id__max_ta_marks'), avg_max_att=Avg('subject_id__max_att_marks'))
            if((qry_subject['avg_ext']) == None or (qry_subject['avg_int']) == None):
                final_avg = 0
            else:
                total_obt = (qry_subject['avg_ext']+qry_subject['avg_int'])
                total_ext = (qry_subject['avg_max_ext']+qry_subject['avg_max_ct'] +
                             qry_subject['avg_max_ta']+qry_subject['avg_max_att'])
                final_avg = (int(total_obt)/int(total_ext))*100
        elif (type_request == "Totalmarks_subject_sectionwise"):
            qry_subject = Studentunivesitymarks.objects.filter(uniq_id__sem_id__dept__course__in=body['selected_course'], uniq_id__sem_id__dept__in=body['selected_branch'], uniq_id__sem_id__sem__in=body['selected_sem'], uniq_id__section_id__section=body['selected_section'][0], subject_id=params).exclude(external_marks__isnull=True,
                                                                                                                                                                                                                                                                                                                 internal_marks__isnull=True, subject_id__max_university_marks__isnull=True, subject_id__max_ct_marks__isnull=True, subject_id__max_ta_marks__isnull=True, subject_id__max_att_marks__isnull=True).aggregate(avg_ext=Avg("external_marks"), avg_int=Avg("internal_marks"), avg_max_ext=Avg('subject_id__max_university_marks'), avg_max_ct=Avg('subject_id__max_ct_marks'), avg_max_ta=Avg('subject_id__max_ta_marks'), avg_max_att=Avg('subject_id__max_att_marks'))
            if((qry_subject['avg_ext']) == None or (qry_subject['avg_int']) == None):
                final_avg = 0
            else:
                total_obt = (qry_subject['avg_ext']+qry_subject['avg_int'])
                total_ext = (qry_subject['avg_max_ext']+qry_subject['avg_max_ct'] +
                             qry_subject['avg_max_ta']+qry_subject['avg_max_att'])
                final_avg = (int(total_obt)/int(total_ext))*100

        elif (type_request == "Totalmarks_section_subjectwise"):
            qry_subject = Studentunivesitymarks.objects.filter(uniq_id__sem_id__dept__course__in=body['selected_course'], uniq_id__sem_id__dept__in=body['selected_branch'], uniq_id__sem_id__sem__in=body['selected_sem'], subject_id__in=body['selected_subject'], uniq_id__section_id__section=params).exclude(external_marks__isnull=True,
                                                                                                                                                                                                                                                                                                                  internal_marks__isnull=True, subject_id__max_university_marks__isnull=True, subject_id__max_ct_marks__isnull=True, subject_id__max_ta_marks__isnull=True, subject_id__max_att_marks__isnull=True).aggregate(avg_ext=Avg("external_marks"), avg_int=Avg("internal_marks"), avg_max_ext=Avg('subject_id__max_university_marks'), avg_max_ct=Avg('subject_id__max_ct_marks'), avg_max_ta=Avg('subject_id__max_ta_marks'), avg_max_att=Avg('subject_id__max_att_marks'))
            if((qry_subject['avg_ext'] or qry_subject['avg_int']) == None):
                final_avg = 0
            else:
                total_obt = (qry_subject['avg_ext']+qry_subject['avg_int'])
                total_ext = (qry_subject['avg_max_ext']+qry_subject['avg_max_ct'] +
                             qry_subject['avg_max_ta']+qry_subject['avg_max_att'])
                final_avg = (int(total_obt)/int(total_ext))*100
        if final_avg == None:
            final_avg = 0
        average_list.append(final_avg)
    return average_list

#function for bonus marks of individual std
def fetch_bonus_marks_individual_student(uniq_id,subject_id,sem_id,session_name):
    #every input is value not list
    BonusMarks = generate_session_table_name("BonusMarks_", session_name)
    fetch_rules_subrules = list(BonusMarks.objects.filter(uniq_id=uniq_id, rule_id__app_id__subject=subject_id, rule_id__app_id__sem_id=sem_id).exclude(status="DELETE").values('rule_id__rule_no', 'rule_id__subrule_no').distinct())
    bonus_marks = 0
    for each_rule in fetch_rules_subrules:
        b_marks = BonusMarks.objects.filter(uniq_id=uniq_id, rule_id__app_id__subject=subject_id, rule_id__app_id__sem_id=sem_id, rule_id__rule_no=each_rule['rule_id__rule_no'], rule_id__subrule_no=each_rule['rule_id__subrule_no']).exclude(status="DELETE").values_list('total_bonus_marks', flat=True)
        if len(b_marks) > 0:
            bonus_marks = float(b_marks[0])
    return bonus_marks

#funtion for sem list in dropdown
def get_sem_coursewise(dept, session,course_list):
    if course_list ==['12']:
        if dept == ['59']:
            q3 = StudentSemester.objects.filter(
                dept__in=dept).values('sem', 'sem_id').order_by('sem')
        else:
            q2 = list(Semtiming.objects.filter(
                session_name__in=[session]).values('sem_type'))
            if q2[0]['sem_type'] == "odd":
                q3 = StudentSemester.objects.filter(dept__in=dept).exclude(sem=1).annotate(odd=F('sem') % 2).filter(
                    odd=True).order_by('sem').distinct().values('sem', 'sem_id').order_by('sem')
            elif q2[0]['sem_type'] == "even":
                q3 = StudentSemester.objects.filter(dept__in=dept).exclude(sem=2).annotate(odd=F('sem') % 2).filter(
                    odd=False).order_by('sem').distinct().values('sem', 'sem_id').order_by('sem')
    else:
        q2 = list(Semtiming.objects.filter(
                session_name__in=[session]).values('sem_type'))
        if q2[0]['sem_type'] == "odd":
            q3 = StudentSemester.objects.filter(dept__in=dept).annotate(odd=F('sem') % 2).filter(
                    odd=True).order_by('sem').distinct().values('sem', 'sem_id').order_by('sem')
        elif q2[0]['sem_type'] == "even":
            q3 = StudentSemester.objects.filter(dept__in=dept).annotate(odd=F('sem') % 2).filter(
                    odd=False).order_by('sem').distinct().values('sem', 'sem_id').order_by('sem')
    return(list(q3))


# for student list for every section
def student_list_sectionwise(session, section_id):
    studentSession = generate_session_table_name("studentSession_", session)
    student_list = list(studentSession.objects.filter(section__in=section_id).exclude(uniq_id__uni_roll_no__isnull=True).values(
        'uniq_id__name', 'uniq_id__uni_roll_no', 'uniq_id').order_by('uniq_id__name'))
    return(student_list)

# function for list of sem student completed before current sem
def individual_sem(dept, selected_sem):
    sem_id_qry = []
    if dept == [59]:
        if selected_sem[0]==1:
            sem_id_qry = StudentSemester.objects.filter(
            dept__in=dept,sem=selected_sem[0]).values('sem_id', 'sem').order_by('sem')

        else:
            sem_id_qry = StudentSemester.objects.filter(
            dept__in=dept).values('sem_id', 'sem').order_by('sem')
    else:
        qry = StudentSemester.objects.filter(
            dept__in=dept).values('sem', 'sem_id').order_by('sem')
        for sem in qry:
            if sem['sem'] <= int(selected_sem[0]):
                sem_id_qry.append(sem)
            else:
                continue
    return(sem_id_qry)

def get_sem_(dept, session, course_list):
    # dept=41,42,
    sem = []
    if dept == [59]:
        q3 = StudentSemester.objects.filter(
            dept__in=dept).values('sem').order_by('sem')
        for x in range(0, len(q3)):
            sem.append(q3[x]['sem'])
        d1 = {'sem': list(sem)}
        return(d1)
    q2 = list(Semtiming.objects.filter(
        session_name__in=session).values('sem_type'))
    q3 = StudentSemester.objects.none()
    if q2[0]['sem_type'] == "odd":
        q3 = StudentSemester.objects.filter(dept__in=dept).annotate(odd=F('sem') % 2).filter(
            odd=True).order_by('sem').distinct().values('sem').order_by('sem')
    elif q2[0]['sem_type'] == "even":
        q3 = StudentSemester.objects.filter(dept__in=dept).annotate(odd=F('sem') % 2).filter(
            odd=False).order_by('sem').distinct().values('sem').order_by('sem')
    for x in range(0, len(q3)):
        if (q3[x]['sem'] == 1 or q3[x]['sem'] == 2) and course_list[0] == 12:
            continue
        sem.append(q3[x]['sem'])
    d1 = {'sem': list(sem)}
    return(d1)


def get_sec(dept, sem):
    # dept=41,42.sem=1,3,5,7
    q4 = list(StudentSemester.objects.filter(dept__in=dept,
                                             sem__in=sem).values_list('sem_id', flat=True))
    q5 = list(Sections.objects.filter(sem_id__in=q4).annotate(
        max1=Count('section')).exclude(status='DELETE').values('section', 'section_id').order_by('section').distinct())
    # [{'section': 'A', 'section_id': 10}, {'section': 'B', 'section_id': 11}]
    return(q5)


def get_section_new(dept, sem):
    qry = list(Sections.objects.filter(sem_id__sem__in=sem, dept__in=dept).annotate(
        max1=Count('section')).exclude(status='DELETE').values('section', 'section_id').order_by('section'))
    return(qry)

#function for subject list by sem name
def get_subject(sem, session_name, branch):
    SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
    query_sub = list(SubjectInfo.objects.filter(sem__sem__in=sem, sem__dept__uid__in=branch).exclude(status='DELETE').exclude(
        subject_type__in=[87, 100]).values('sub_num_code', 'sub_name', 'sub_alpha_code', 'id', 'subject_type').distinct())  # value added excluded
    return query_sub
#function for sb=ubject list by sem id
def get_subject_by_semid(sem_id, session_name, branch):
    SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
    query_sub = list(SubjectInfo.objects.filter(sem__in=sem_id, sem__dept__uid__in=branch).exclude(status='DELETE').exclude(
        subject_type__in=[87, 100]).values('sub_num_code', 'sub_name', 'sub_alpha_code', 'id', 'subject_type').distinct())  # value added excluded
    return query_sub



#####################################################
###FUNCTION FOR ALL INTERNAL DATA IN CHART FORMAT OF A STUDENT
########################################################
def ind_Stu_int_subject(uniq_id, session_name, subject_id):
    # for calculting internal % of marks of given sub
    batch_from=StudentPrimDetail.objects.filter(uniq_id__in=uniq_id).values('batch_from')[0]['batch_from']
    exam_list = []
    absolute_marks = [['Internal - External']]
    absolute_marks[0].append('marks')
    SubjectInfo=generate_session_table_name('SubjectInfo_',session_name)
    qry= SubjectInfo.objects.filter(id__in=subject_id).exclude(status='DELETE').values('sem__dept__course','sem','subject_type','max_att_marks','max_ct_marks')
    course=qry[0]['sem__dept__course']
    sem_id=qry[0]['sem']
    ###TA MARKS
    TAmarks = get_student_subject_ta_marks(uniq_id[0], session_name, subject_id[0])
    if TAmarks != 'N/A':
        TAmarks = math.ceil(float(TAmarks))
    ####
    session_num = int(session_name[:2])
    ###ATT MARKS
    if session_num <19:
        Attmarks= get_student_subject_att_marks(uniq_id[0],session_name,subject_id[0],qry[0]['subject_type'],sem_id,qry[0]['max_att_marks'])
    else:
        Attmarks= get_student_subject_att_marks_new_subjectwise(uniq_id,session_name,subject_id[0],qry[0]['subject_type'],sem_id,qry[0]['max_att_marks'])
    ####
    given_marks_dict = {}
    given_max_marks_dict = {}
    exam_list=get_exam_list(session_name)
    batch_from=StudentPrimDetail.objects.filter(uniq_id__in=uniq_id).values('batch_from')[0]['batch_from']
    studentmarks = generate_session_table_name(
        "StudentMarks_", session_name)
    QuesPaperSectionDetails=generate_session_table_name('QuesPaperSectionDetails_',session_name)
    for exam in exam_list:
        ques_paper_id = list(studentmarks.objects.filter(
            marks_id__exam_id=exam['sno'], uniq_id__in=uniq_id, marks_id__subject_id__in=subject_id).exclude(marks__isnull=True).exclude(status='DELETE').values_list('ques_id__section_id__ques_paper_id', flat=True))
        if ques_paper_id == []:
            continue
        max_marks = QuesPaperSectionDetails.objects.filter(
            ques_paper_id=ques_paper_id[0]).aggregate(max_marks=Sum('max_marks'))
        marks_obt = studentmarks.objects.filter(
            marks_id__exam_id=exam['sno'], uniq_id__in=uniq_id, marks_id__subject_id__in=subject_id).exclude(marks__isnull=True).exclude(status='DELETE').aggregate(total_marks_obt=Sum('marks'))
        given_marks_dict[str(exam['sno'])] = marks_obt['total_marks_obt']
        given_max_marks_dict[str(exam['sno'])] = max_marks['max_marks']
    ###FOR BPHARM
    if course ==13:
        max_int_marks=25
        exammarks_obt=pointer_converter(uniq_id, exam_list, subject_id, session_name,course)
        tamarks = ['Teachar Assessment Marks']
        tamarks.append(TAmarks)
        absolute_marks.append(tamarks)
        ctmarks = ['CT Marks']
        ctmarks.append(exammarks_obt)
        absolute_marks.append(ctmarks)
        attmarks = ['Attendence Marks']
        attmarks.append(Attmarks['att_marks'])
        absolute_marks.append(attmarks)
        total_int_obt = (TAmarks+Attmarks['att_marks']+exammarks_obt)
    else:
        max_int_marks=50
        if batch_from <=2018:
            if batch_from <= 2017:
                max_int_marks=30
            exammarks_obt=pointer_converter(uniq_id, exam_list, subject_id, session_name,course)
            tamarks = ['Teachar Assessment Marks']
            tamarks.append(TAmarks)
            absolute_marks.append(tamarks)
            ctmarks = ['CT Marks']
            ctmarks.append(exammarks_obt)
            absolute_marks.append(ctmarks)
            attmarks = ['Attendence Marks']
            attmarks.append(Attmarks['att_marks'])
            absolute_marks.append(attmarks)
            total_int_obt = (TAmarks+Attmarks['att_marks']+exammarks_obt)
        else:
            store_ctmarks = generate_session_table_name(
                'Store_Ctmarks_RuleWise_', session_name)
            Subjectinfo = generate_session_table_name('SubjectInfo_', session_name)
            max_marks_qry = list(Subjectinfo.objects.filter(id__in=subject_id).values(
                'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks'))
            exams = get_exam_list(session_name)
            exam_list=[]
            for exam in exams:
                exam_list.append(exam['sno'])
            exammarks = store_ctmarks.objects.filter(exam_id__in=exam_list, uniq_id__in=uniq_id, subject_id__in=subject_id).exclude(
                status='DELETE').exclude(ct_marks_obtained="N/A").aggregate(obt_total=Sum('ct_marks_obtained'), total=Sum('ct_marks_total'))
            max_int_marks = (max_marks_qry[0]['max_ct_marks'] +
                            max_marks_qry[0]['max_ta_marks']+max_marks_qry[0]['max_att_marks'])
            tamarks = ['Teachar Assessment Marks']
            tamarks.append(TAmarks)
            absolute_marks.append(tamarks)
            ctmarks = ['CT Marks']
            ctmarks.append((exammarks['obt_total']))
            absolute_marks.append(ctmarks)
            attmarks = ['Attendence Marks']
            attmarks.append(Attmarks['att_marks'])
            absolute_marks.append(attmarks)
            total_int_obt = (TAmarks+Attmarks['att_marks']+(exammarks['obt_total']))
    ###BONUS MARKS #####
    if session_num < 19:
        bonus_marks_data = get_student_subject_bonus_marks(uniq_id[0], given_marks_dict, given_max_marks_dict, session_name, qry[0]['subject_type'], sem_id, Attmarks['att_per'], total_int_obt, max_int_marks)
        total_marks = bonus_marks_data['marks_obtained']
    else:
        bonus_marks_data=fetch_bonus_marks_individual_student(uniq_id[0],subject_id[0],sem_id,session_name)
        total_marks=total_int_obt+(bonus_marks_data)
    bonus_marks=['Bonus Marks']
    bonus_marks.append(total_marks-total_int_obt)
    absolute_marks.append(bonus_marks)
    remainig = ['']
    remainig.append(max_int_marks-total_marks)
    #########
    absolute_marks.append(remainig)
    return absolute_marks
##FUNCTION FOR ATT MARKS AFTER STORE
def get_student_subject_att_marks_new_subjectwise(uniq_id, session_name, subject_id,subject_type, sem_id, max_att_marks):
	AttMarksRule = generate_session_table_name("AttMarksRule_", session_name)
	session_num = int(session_name[:2])
	data = {}
	qry_from_to_date = Semtiming.objects.filter(session_name=session_name).values('sem_start', 'sem_end', 'uid')
	session = qry_from_to_date[0]['uid']
	if session_num >= 19:
		query = get_overall_attendance(uniq_id, session_name, session)
		for q in query:
			data[q['uniq_id']] = {}
			for sub, sub_data in q['sub_wise_att'].items():
				if sub==subject_id:
					data[q['uniq_id']][sub] = {}
					sub_att_per = 0
					marks = 'N/A'
					if sub_data['total_att'] > 0:
						sub_att_per = round((sub_data['present_count'] * 100.0) / sub_data['total_att'])
					else:
						sub_att_per = 0

					qry_rule = AttMarksRule.objects.filter(subject_type=subject_type, sem=sem_id, from_att_per__lte=sub_att_per, to_att_per__gte=sub_att_per, max_att_marks=max_att_marks).exclude(status='DELETE').values('marks').order_by('-id')[:1]

					if len(qry_rule) == 0:
						marks = "Rule Not Defined for this attendance percentage"
					else:
						marks = min(max_att_marks, qry_rule[0]['marks'])
					data[q['uniq_id']][sub] = {'att_per': sub_att_per, 'att_marks': marks}

	return {'att_per': sub_att_per, 'att_marks': marks}

###FUNCTIONN FOR EXTERNAL MARKS OF INDIVIDUAL STUDENT
def ind_stu_ext_subject(uniq_id, session, subject_id):
    absolute_marks = [['Interanl-External']]
    absolute_marks[0].append('marks')
    Studentunivesitymarks = generate_session_table_name(
        'StudentUniversityMarks_', session)
    marks = Studentunivesitymarks.objects.filter(uniq_id=uniq_id[0], subject_id__in=subject_id).values(
        'external_marks', 'subject_id__max_university_marks')
    external = ['MARKS OBTAINED']
    external.append(int(marks[0]['external_marks']))
    absolute_marks.append(external)
    remainig = ['']
    remainig.append(
        int(marks[0]['subject_id__max_university_marks'])-int(marks[0]['external_marks']))
    absolute_marks.append(remainig)
    return absolute_marks

#FUNCTION FOR EXAM LIST
def get_exam_list(session_name):
    session = Semtiming.objects.filter(
        session_name=session_name).values_list('uid', flat=True)
    exam_list = []
    qry = StudentAcademicsDropdown.objects.filter(field="EXAM NAME", session=session[0]).exclude(
        value__isnull=True).exclude(status="DELETE").values("sno", "value")
    for q in qry:
        exam_list.append({'sno': q['sno'], 'value': q['value']})
    return exam_list


def individual_sesssion(body):
    ind_stu_session = []
    body['seleted_session'] = ["1920e"]
    sem_name = list(StudentSemester.objects.filter(
        sem_id__in=body['selected_sem']).values_list('sem', flat=True))
    sem_dict = list(individual_sem(
        body['selected_branch'], sem_name))
    qry = (Semtiming.objects.all().values(
        'session_name', 'session', 'sem_start').order_by('sem_start'))
    student_start_year = StudentPrimDetail.objects.filter(
        uniq_id__in=body['selected_student']).values_list('batch_from', flat=True)
    for q in qry:
        session_start = q['session'].split('-')[0]
        if (str(session_start) == str(student_start_year[0])):
            sem_start_date = q['sem_start']
            break
    for q in qry:
        if q['sem_start'] >= sem_start_date:
            ind_stu_session.append(q['session_name'])
    for sems in sem_dict:
        if sems['sem'] == sem_name[0]:
            index_sem = sem_dict.index(sems)
            individual_session = ind_stu_session[index_sem]
    return individual_session

#function for querying marks examwise
def get_examwise_data(student_uniq_id, exam_list, subject_id, session_name):
    #returns two array max marks and marks obt
    StudentMarks = generate_session_table_name(
        "StudentMarks_", session_name)
    QuesPaperSectionDetails=generate_session_table_name('QuesPaperSectionDetails_',session_name)
    absolute_marks=[]
    absolute_percent=[['Internal']]
    absolute_percent[0].append('Percent')
    absolute_percent[0].append("{ role: 'tooltip', 'p': {'html': true}}")
    marks = []
    for exam in exam_list:
        ques_paper_id = list(StudentMarks.objects.filter(
            marks_id__exam_id=exam['sno'], uniq_id__in=student_uniq_id, marks_id__subject_id__in=subject_id).exclude(marks__isnull=True).exclude(status='DELETE').values_list('ques_id__section_id__ques_paper_id', flat=True))
        if ques_paper_id == []:
            continue
        max_marks = QuesPaperSectionDetails.objects.filter(
            ques_paper_id=ques_paper_id[0]).aggregate(max_marks=Sum('max_marks'))
        marks_obt = StudentMarks.objects.filter(
            marks_id__exam_id=exam['sno'], uniq_id__in=student_uniq_id, marks_id__subject_id__in=subject_id).exclude(marks__isnull=True).exclude(status='DELETE').aggregate(total_marks_obt=Sum('marks'))
        marks.append(marks_obt)
        exam_per=[exam['value']]
        if marks_obt['total_marks_obt'] != None:
            exam_per.append((marks_obt['total_marks_obt']/max_marks['max_marks'])*100)
            exam_per.append('<div><strong>'+exam['value']+'<br><b>Percent :'+str(round(((marks_obt['total_marks_obt']/max_marks['max_marks'])*100),2))+'% </b><br>Marks:'+str(int(marks_obt['total_marks_obt']))+'/'+str(int(max_marks['max_marks']))+'</strong></div>') 
        else:
            exam_per.append(0)
        # absolute_marks.append(percent)
        absolute_percent.append(exam_per)
    absolute_marks.append(absolute_percent)
    return(absolute_marks)

#function for converting marks as sent in internal before store
def pointer_converter(student_uniq_id, exam_list, subject_id, session_name,course):
#input are in list except course and session_name

    batch_from=StudentPrimDetail.objects.filter(uniq_id__in=student_uniq_id).values('batch_from')[0]['batch_from']

    studentmarks = generate_session_table_name(
        "StudentMarks_", session_name)
    QuesPaperSectionDetails=generate_session_table_name('QuesPaperSectionDetails_',session_name)
    pointer=0

    absolute_marks = [['Internal']]
    absolute_marks[0].append('marks')
    point = []
    for exam in exam_list:
        ques_paper_id = list(studentmarks.objects.filter(
            marks_id__exam_id=exam['sno'], uniq_id__in=student_uniq_id, marks_id__subject_id__in=subject_id).exclude(marks__isnull=True).exclude(status='DELETE').values_list('ques_id__section_id__ques_paper_id', flat=True))
        if ques_paper_id == []:
            continue
        max_marks = QuesPaperSectionDetails.objects.filter(
            ques_paper_id=ques_paper_id[0]).aggregate(max_marks=Sum('max_marks'))
        marks_obt = studentmarks.objects.filter(
            marks_id__exam_id=exam['sno'], uniq_id__in=student_uniq_id, marks_id__subject_id__in=subject_id).exclude(marks__isnull=True).exclude(status='DELETE').aggregate(total_marks_obt=Sum('marks'))
        if course ==13:
            max_conv_m=5
        else:
            if batch_from == 2018:
                max_conv_m=15
            elif batch_from == 2017:
                max_conv_m=10
        pointer = math.ceil((marks_obt['total_marks_obt']/max_marks['max_marks'])*max_conv_m)
        point.append(pointer)
        point.sort()
    pointer= point[-1]+point[-2]
    return(pointer)
###############################
#functions for employee data
############################
def get_all_emp(dept, category):
    s = EmployeePrimdetail.objects.filter(emp_status='ACTIVE', dept=EmployeeDropdown.objects.get(sno=dept), emp_category=EmployeeDropdown.objects.get(sno=category)).exclude(
        emp_id="00007").extra(select={'emp_name': 'name', 'emp_code': 'emp_id'}).exclude(emp_status="SEPARATE").values('emp_name', 'emp_code', 'dept__value', 'desg__value').order_by('name').all()
    return s

def get_dept_id(uid):
    q2 = list(CourseDetail.objects.filter(uid=uid).values('dept'))
    return(q2[0]['dept'])

def Average(lst):
    if len(lst) != 0:
        return sum(lst) / len(lst)
    else:
        return 0


def faculty_check(session, faculty_id):
    qry_session = Semtiming.objects.filter(
        session_name=session).values('sem_start')[0]['sem_start']
    qry = EmployeePrimdetail.objects.filter(
        emp_id=faculty_id).values('name', 'doj')
    # list_date=list(qry[0]['doj'])
    if qry[0]['doj'] <= qry_session:
        status = True
    else:
        status = False
    return status


def unique(list1):
    unique_list = []
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    return(unique_list)


def course_faculty(session, faculty_lst):
    course_list = []
    timetable = generate_session_table_name('FacultyTime_', session)
    qry = timetable.objects.filter(emp_id__in=faculty_lst, subject_id_id__subject_type__in=[84, 86]).values(
        'section_id__dept__course', 'section_id__dept__course__value').distinct()
    qry_f=unique(qry)
    for q in qry_f:
        course_list.append(q)
    return(course_list)

#for list of branch taught by faculty in single session
def branch_faculty(session, faculty_lst, course_list):
    branch_list = []
    timetable = generate_session_table_name('FacultyTime_', session)
    qry = timetable.objects.filter(emp_id__in=faculty_lst, subject_id_id__subject_type__in=[
        84, 86], section_id__dept__course__in=course_list).values('section_id__dept', 'section_id__dept__dept_id__value').distinct()
    for q in qry:
        branch_list.append(q)
    return(branch_list)

def semester_faculty(session, faculty_lst, branch_list):
    sem_list = []
    timetable = generate_session_table_name('FacultyTime_', session)
    qry = timetable.objects.filter(emp_id__in=faculty_lst, subject_id_id__subject_type__in=[
        84, 86], section_id__dept__in=branch_list).values('section_id__sem_id', 'section_id__sem_id__sem').distinct()
    for q in qry:
        sem_list.append(q)
    return(sem_list)


def section_faculty_subjectwise(session, faculty_lst, branch_list, sem_list, subject_list):
    section_list = []
    timetable = generate_session_table_name('FacultyTime_', session)
    qry = timetable.objects.filter(emp_id__in=faculty_lst, subject_id_id__subject_type__in=[
        84, 86], section_id__dept__in=branch_list, subject_id__in=subject_list).values('section_id', 'section_id__section').distinct()
    for q in qry:
        section_list.append(q)
    return(section_list)


def subject_faculty_course(session, faculty_lst,course):
    subject_list = []
    timetable = generate_session_table_name('FacultyTime_', session)
    qry = timetable.objects.filter(emp_id__in=faculty_lst, subject_id_id__subject_type__in=[
        84, 86],section_id__dept__course=course ).exclude(subject_id_id__sub_alpha_code__in=["MEN", "LIB"]).values('subject_id', 'subject_id__sub_name').distinct()
    for q in qry:
        subject_list.append(q['subject_id'])
    return(subject_list)

def subject_faculty_branch(session, faculty_lst,branch):
    subject_list = []
    timetable = generate_session_table_name('FacultyTime_', session)
    qry = timetable.objects.filter(emp_id__in=faculty_lst, subject_id_id__subject_type__in=[
        84, 86],section_id__dept=branch ).exclude(subject_id_id__sub_alpha_code__in=["MEN", "LIB"]).values('subject_id', 'subject_id__sub_name').distinct()
    for q in qry:
        subject_list.append(q['subject_id'])
    return(subject_list)

def subject_faculty_sem(session, faculty_lst,sem):
    subject_list = []
    timetable = generate_session_table_name('FacultyTime_', session)
    qry = timetable.objects.filter(emp_id__in=faculty_lst, subject_id_id__subject_type__in=[
        84, 86],section_id__sem_id=sem ).exclude(subject_id_id__sub_alpha_code__in=["MEN", "LIB"]).values('subject_id','section_id__sem_id','subject_id__sub_num_code','subject_id__sub_name','subject_id__sub_alpha_code').distinct()
    for q in qry:
        subject_list.append(q['subject_id'])
    return(subject_list)
def faculty_subject_section(session,faculty_lst,subject):
    subject_list = []
    timetable = generate_session_table_name('FacultyTime_', session)
    qry = timetable.objects.filter(emp_id__in=faculty_lst, subject_id_id__subject_type__in=[
        84, 86],subject_id__sub_name=subject ).exclude(subject_id_id__sub_alpha_code__in=["MEN", "LIB"]).values('subject_id', 'subject_id__sub_name').distinct()
    for q in qry:
        subject_list.append(q['subject_id'])
    return(subject_list)



def marks_subjectwise_sem(session, subject_list):
    marks_list = []
    Studentuniversity = generate_session_table_name(
        'StudentUniversityMarks_', session)
    for subject in subject_list:
        qry_subject = Studentuniversity.objects.filter(subject_id=subject['subject_id']).exclude(external_marks__isnull=True,
                                                                                                 internal_marks__isnull=True, subject_id__max_university_marks__isnull=True, subject_id__max_ct_marks__isnull=True, subject_id__max_ta_marks__isnull=True, subject_id__max_att_marks__isnull=True).aggregate(avg_ext=Avg("external_marks"), avg_int=Avg("internal_marks"), avg_max_ext=Avg('subject_id__max_university_marks'), avg_max_ct=Avg('subject_id__max_ct_marks'), avg_max_ta=Avg('subject_id__max_ta_marks'), avg_max_att=Avg('subject_id__max_att_marks'))
        if((qry_subject['avg_ext']) == None or (qry_subject['avg_int']) == None):
            final_avg = 0
        else:
            total_obt = (qry_subject['avg_ext']+qry_subject['avg_int'])
            total_ext = (qry_subject['avg_max_ext']+qry_subject['avg_max_ct'] +
                         qry_subject['avg_max_ta']+qry_subject['avg_max_att'])
            final_avg = (float(total_obt)/float(total_ext))*100
        # marks_list.append(subject)
        marks_list.append(round(final_avg, 2))
    return marks_list


def marks_subjectwise(session, subject_list):
    marks_list = []
    Studentuniversity = generate_session_table_name(
        'StudentUniversityMarks_', session)
    for subject in subject_list:
        qry_subject = Studentuniversity.objects.filter(subject_id=subject).exclude(external_marks__isnull=True,
                                                                                   internal_marks__isnull=True, subject_id__max_university_marks__isnull=True, subject_id__max_ct_marks__isnull=True, subject_id__max_ta_marks__isnull=True, subject_id__max_att_marks__isnull=True).aggregate(avg_ext=Avg("external_marks"), avg_int=Avg("internal_marks"), avg_max_ext=Avg('subject_id__max_university_marks'), avg_max_ct=Avg('subject_id__max_ct_marks'), avg_max_ta=Avg('subject_id__max_ta_marks'), avg_max_att=Avg('subject_id__max_att_marks'))
        if((qry_subject['avg_ext']) == None or (qry_subject['avg_int']) == None):
            final_avg = 0
        else:
            total_obt = (qry_subject['avg_ext']+qry_subject['avg_int'])
            total_ext = (qry_subject['avg_max_ext']+qry_subject['avg_max_ct'] +
                         qry_subject['avg_max_ta']+qry_subject['avg_max_att'])
            final_avg = (float(total_obt)/float(total_ext))*100
        marks_list.append(round(final_avg, 2))
    avg=[Average(marks_list)]
    return avg[0]
def marks_subjectwise_sub_section(session, subject_list):
    marks_list = []
    Studentuniversity = generate_session_table_name(
        'StudentUniversityMarks_', session)
    for subject in subject_list:
        qry_subject = Studentuniversity.objects.filter(subject_id__sub_name=subject).exclude(external_marks__isnull=True,
                                                                                   internal_marks__isnull=True, subject_id__max_university_marks__isnull=True, subject_id__max_ct_marks__isnull=True, subject_id__max_ta_marks__isnull=True, subject_id__max_att_marks__isnull=True).aggregate(avg_ext=Avg("external_marks"), avg_int=Avg("internal_marks"), avg_max_ext=Avg('subject_id__max_university_marks'), avg_max_ct=Avg('subject_id__max_ct_marks'), avg_max_ta=Avg('subject_id__max_ta_marks'), avg_max_att=Avg('subject_id__max_att_marks'))
        if((qry_subject['avg_ext']) == None or (qry_subject['avg_int']) == None):
            final_avg = 0
        else:
            total_obt = (qry_subject['avg_ext']+qry_subject['avg_int'])
            total_ext = (qry_subject['avg_max_ext']+qry_subject['avg_max_ct'] +
                         qry_subject['avg_max_ta']+qry_subject['avg_max_att'])
            final_avg = (float(total_obt)/float(total_ext))*100
        marks_list.append(round(final_avg, 2))
    avg=[Average(marks_list)]
    return avg[0]
###############################                    #################
##############################     FACULTY          #############################
#################################################################################


def faculty_analyser(request):
    response_values = []
    if checkpermission(request, [rolesCheck.ROLE_MARKS_ANALYSIS_CORDINATOR]) == statusCodes.STATUS_SUCCESS:
        # session = request.session['Session_id']
        if requestMethod.GET_REQUEST(request):  # list for drop down
            response_values = {}
            if (requestType.custom_request_type(request.GET, 'get_list')):
                session_range = Semtiming.objects.filter(
                    sem_start__gte="2018-06-01").values('uid', 'session', 'session_name')
                response_values['session_range'] = list(session_range)
                response_values['course'] = get_course()
            elif(requestType.custom_request_type(request.GET, 'get_course')):
                response_values['course'] = get_course()

            elif (requestType.custom_request_type(request.GET, 'get_branch')):
                course_list = request.GET['course'].split(',')
                response_values = get_branch(course_list)
            elif (requestType.custom_request_type(request.GET, 'get_sem')):
                branch_list = request.GET['dept'].split(',')
                course_list = request.GET['course'].split(',')
                # here seesion can be current session and in anlayser we can use session dropdown also.
                session = request.session['Session_name']
                response_values = get_sem_coursewise(branch_list, session,course_list)
            elif (requestType.custom_request_type(request.GET, 'get_section')):
                branch_list = request.GET['dept'].split(',')
                sem_list = request.GET['sem'].split(',')
                response_values = get_section_new(branch_list, sem_list)
            elif(requestType.custom_request_type(request.GET, 'get_employee')):
                response_values = {}
                dept = get_dept_id(request.GET['dept'])
                employees = list(get_all_emp(dept, 223))
                employee_list = []
                for employee in employees:
                    employee_list.append(
                        {"emp_name": employee["emp_name"]+" ( "+employee["emp_code"] + " )", "emp_code": employee["emp_code"]})
                response_values["faculty"] = employee_list
            else:
                response_values = statusMessages.MESSAGE_BAD_REQUEST
        if requestMethod.POST_REQUEST(request): 
            body = json.loads(request.body)
################################## FACULTY COURSEWISE ######################################
            if body['type_request']=='faculty_coursewise':
                for faculty in body['selected_employee']:
                    body['selected_employee']=[faculty]
                    multifaculty=[]
                    data=[['course']]
                    id_list=[['course']]
                    data_dict={}
                    locked = {'locked_session': "", 'locked_course': "", 'locked_branch': "", 'locked_sem': "",
                              'locked_subject': "", 'locked_section': "", 'locked_faculty': "",'locked_status':""}  # dict for sending levels freezed
                    for session in body['selected_session']:
                        timetable = generate_session_table_name('FacultyTime_', session)
                        locked['locked_session'] += str(session)
                        if session == body['selected_session'][-1]:
                            qry = timetable.objects.filter(emp_id__in=[faculty], subject_id_id__subject_type__in=[84, 86]).values('section_id__dept__course__value','section_id__dept','section_id__dept__course').distinct()
                            for q in qry:
                                if [q['section_id__dept__course__value']] not in data:
                                    data.append([q['section_id__dept__course__value']])
                                    id_list.append([q['section_id__dept__course']])
                            break
                        else:
                            locked['locked_session'] += ','
                        qry = timetable.objects.filter(emp_id__in=[faculty], subject_id_id__subject_type__in=[84, 86]).values('section_id__dept__course__value','section_id__dept','section_id__dept__course').distinct()
                        for q in qry:
                            if [q['section_id__dept__course__value']] not in data:
                                data.append([q['section_id__dept__course__value']])
                                id_list.append([q['section_id__dept__course']])
                    emp = EmployeePrimdetail.objects.filter(
                        emp_id=faculty).values('name', 'emp_id')
                    locked['locked_faculty'] += str(
                        emp[0]['name']+'( '+str(emp[0]['emp_id'])+' )')
                    for session in body['selected_session']:
                        course_dict={}
                        faculty_present=faculty_check(session,faculty)
                        if faculty_present == True:
                            course_list = course_faculty(session, [faculty])
                            if course_list ==[]:
                                course_dict['']=0
                                data_dict[str(session)]=course_dict
                                continue
                            else:
                                for course in course_list:
                                    subject_list = subject_faculty_course(session, [faculty],course['section_id__dept__course'])
                                    marks = marks_subjectwise(
                                        session, subject_list)
                                    course_dict[course['section_id__dept__course__value']]=marks
                                    data_dict[str(session)]=course_dict
                        else:
                            course_dict['notpresent']=0
                            data_dict[session]=course_dict
                    count=0
                    for keys,values in data_dict.items():
                        count+=1
                        if len(data)>1:
                            for d in range(1,len(data)):
                                data[d].append(0)
                        data[0].append(keys)
                        id_list[0].append(keys)
                        for key ,value in values.items():
                            if len(data)>1:
                                for d in data:
                                    if d[0]==key:
                                        index=data.index(d)
                                        data[index][count]=value                    
                    if len(data)==1:
                        locked['locked_status'] += 'TAUGHT NOTHING'
                    multifaculty.append(data)
                    multifaculty.append(id_list)
                    multifaculty.append([locked])
                    multifaculty.append([body])
                    body=json.loads(request.body)
                    response_values.append(multifaculty)
################################################  FACULTY BRANCHWISE #############################################33333333333333333333333
            elif body['type_request']=='faculty_branchwise':
                for faculty in body['selected_employee']:
                    data=[['branch']]
                    id_list=[['branch']]
                    data_dict={}
                    locked = {'locked_session': "", 'locked_course': "", 'locked_branch': "", 'locked_sem': "",
                              'locked_subject': "", 'locked_section': "", 'locked_faculty': ""}  # dict for sending levels freezed
                    for session in body['selected_session']:
                        timetable = generate_session_table_name('FacultyTime_', session)
                        locked['locked_session'] += str(session)
                        if session == body['selected_session'][-1]:
                            qry = timetable.objects.filter(emp_id__in=[faculty],section_id__dept__course__in=body['selected_course'],subject_id_id__subject_type__in=[84, 86]).exclude(status='DELETE').values('section_id__dept','section_id__dept__dept_id__value').distinct()
                            for q in qry:

                                if [q['section_id__dept__dept_id__value']] not in data:
                                    data.append([q['section_id__dept__dept_id__value']])
                                    id_list.append([q['section_id__dept']])
                            break
                        else:
                            locked['locked_session'] += ','
                        qry = timetable.objects.filter(emp_id__in=[faculty],section_id__dept__course__in=body['selected_course'], subject_id_id__subject_type__in=[84, 86]).exclude(status='DELETE').values('section_id__dept','section_id__dept__dept_id__value').distinct()
                        for q in qry:
                            if [q['section_id__dept__dept_id__value']] not in data:
                                data.append([q['section_id__dept__dept_id__value']])
                                id_list.append([q['section_id__dept']])
                    emp = EmployeePrimdetail.objects.filter(
                        emp_id=faculty).values('name', 'emp_id')
                    locked['locked_faculty'] += str(
                        emp[0]['name']+'( '+str(emp[0]['emp_id'])+' )')
                    course_name = CourseDetail.objects.filter(
                    course__in=body['selected_course']).values_list('course__value', flat=True).distinct()
                    locked['locked_course'] += str(course_name[0])
                    for session in body['selected_session']:
                        branch_dict={}
                        branch_list = branch_faculty(session, [faculty],body['selected_course'])
                        if branch_list ==[]:
                            branch_dict['']=0
                            data_dict[str(session)]=branch_dict
                            continue
                        else:
                            for branch in branch_list:
                                subject_list = subject_faculty_branch(session, [faculty],branch['section_id__dept'])
                                marks = marks_subjectwise(
                                    session, subject_list)
                                branch_dict[branch['section_id__dept__dept_id__value']]=marks
                                data_dict[str(session)]=branch_dict
                    count=0
                    for keys,values in data_dict.items():
                        count+=1
                        if len(data)>1:
                            for d in range(1,len(data)):
                                data[d].append(0)
                        data[0].append(keys)
                        id_list[0].append(keys)

                        for key ,value in values.items():
                            if len(data)>1:
                                for d in data:
                                    if d[0]==key:
                                        index=data.index(d)
                                        data[index][count]=value
                    response_values.append(data)
                    response_values.append(id_list)
                    response_values.append([locked])
                    response_values.append([body])
########################################   FACULTY_SEMWISE #########################################
            elif body['type_request']=='faculty_semwise':
                for faculty in body['selected_employee']:
                    data=[['semester']]
                    id_list=[['semester']]
                    data_dict={}
                    locked = {'locked_session': "", 'locked_course': "", 'locked_branch': "", 'locked_sem': "",
                              'locked_subject': "", 'locked_section': "", 'locked_faculty': ""}  # dict for sending levels freezed
                    for session in body['selected_session']:
                        timetable = generate_session_table_name('FacultyTime_', session)
                        locked['locked_session'] += str(session)
                        if session == body['selected_session'][-1]:
                            qry = timetable.objects.filter(emp_id__in=[faculty],section_id__dept__in=body['selected_branch'],section_id__dept__course__in=body['selected_course'], subject_id_id__subject_type__in=[84, 86]).exclude(status='DELETE').values('section_id__sem_id','section_id__sem_id_id__sem').distinct()
                            for q in qry:
                                if ['Semester '+str(q['section_id__sem_id_id__sem'])] not in data:
                                    data.append((['Semester '+str(q['section_id__sem_id_id__sem'])]))
                                    id_list.append([q['section_id__sem_id']])
                            break
                        else:
                            locked['locked_session'] += ','
                        qry = timetable.objects.filter(emp_id__in=[faculty],section_id__dept__in=body['selected_branch'],section_id__dept__course__in=body['selected_course'], subject_id_id__subject_type__in=[84, 86]).exclude(status='DELETE').values('section_id__sem_id','section_id__sem_id_id__sem').distinct()
                        for q in qry:
                            if ['Semester '+str(q['section_id__sem_id_id__sem'])] not in data:
                                data.append((['Semester '+str(q['section_id__sem_id_id__sem'])]))
                                id_list.append([q['section_id__sem_id']])
                    emp = EmployeePrimdetail.objects.filter(
                        emp_id=faculty).values('name', 'emp_id')
                    locked['locked_faculty'] += str(
                        emp[0]['name']+'( '+str(emp[0]['emp_id'])+' )')
                    course_name = CourseDetail.objects.filter(
                    course__in=body['selected_course']).values_list('course__value', flat=True).distinct()
                    locked['locked_course'] += str(course_name[0])
                    branch_name = list(CourseDetail.objects.filter(
                    uid__in=body['selected_branch']).values("dept__value").distinct())
                    locked['locked_branch'] += str(branch_name[0]['dept__value'])
                    for session in body['selected_session']:
                        sem_dict={}
                        sem_list = semester_faculty(session, [faculty],body['selected_branch'])
                        if sem_list ==[]:
                            sem_dict['']=0
                            data_dict[str(session)]=sem_dict
                            continue
                        else:
                            for sem in sem_list:
                                subject_list = subject_faculty_sem(session, [faculty],sem['section_id__sem_id'])
                                marks = marks_subjectwise(
                                    session, subject_list)
                                sem_dict['Semester '+ str(sem['section_id__sem_id__sem'])]=marks
                                data_dict[str(session)]=sem_dict
                    count=0
                    for keys,values in data_dict.items():
                        count+=1
                        if len(data)>1:
                            for d in range(1,len(data)):
                                data[d].append(0)
                        data[0].append(keys)
                        id_list[0].append(keys)

                        for key ,value in values.items():
                            if len(data)>1:
                                for d in data:
                                    if d[0]==key:
                                        index=data.index(d)
                                        data[index][count]=value
                    response_values.append(data)
                    response_values.append(id_list)
                    response_values.append([locked])
                    response_values.append([body])
###################################   FACULTY SUBJECTWISE  ###############################################
            elif body['type_request']=='faculty_subjectwise':
                for faculty in body['selected_employee']:
                    data=[['subject']]
                    id_list=[['subject']]
                    data_dict={}
                    locked = {'locked_session': "", 'locked_course': "", 'locked_branch': "", 'locked_sem': "",
                              'locked_subject': "", 'locked_section': "", 'locked_faculty': ""}  # dict for sending levels freezed
                    for session in body['selected_session']:
                        timetable = generate_session_table_name('FacultyTime_', session)
                        locked['locked_session'] += str(session)
                        if session == body['selected_session'][-1]:
                            qry = timetable.objects.filter(emp_id__in=[faculty],section_id__sem_id__in=body['selected_sem'], subject_id_id__subject_type__in=[84, 86]).exclude(status='DELETE').values('subject_id','section_id__sem_id','subject_id__sub_num_code','subject_id__sub_name','subject_id__sub_alpha_code').distinct()
                            for q in qry:
                                if [str(q['subject_id__sub_name'])+'('+str(q['subject_id__sub_alpha_code'])+' '+str(q['subject_id__sub_num_code'])+')'] not in data:
                                    data.append([str(q['subject_id__sub_name'])+'('+str(q['subject_id__sub_alpha_code'])+' '+str(q['subject_id__sub_num_code'])+')'])
                                    id_list.append([str(q['subject_id__sub_name'])])
                            break
                        else:
                            locked['locked_session'] += ','
                        qry = timetable.objects.filter(emp_id__in=[faculty],section_id__sem_id__in=body['selected_sem'], subject_id_id__subject_type__in=[84, 86]).exclude(status='DELETE').values('subject_id','section_id__sem_id','subject_id__sub_num_code','subject_id__sub_name','subject_id__sub_alpha_code').distinct()
                        for q in qry:
                            
                            if [str(q['subject_id__sub_name'])+'('+str(q['subject_id__sub_alpha_code'])+' '+str(q['subject_id__sub_num_code'])+')'] not in data:
                                data.append([str(q['subject_id__sub_name'])+'('+str(q['subject_id__sub_alpha_code'])+' '+str(q['subject_id__sub_num_code'])+')'])
                                id_list.append([str(q['subject_id__sub_name'])])
                    emp = EmployeePrimdetail.objects.filter(
                        emp_id=faculty).values('name', 'emp_id')
                    locked['locked_faculty'] += str(
                        emp[0]['name']+'( '+str(emp[0]['emp_id'])+' )')
                    course_name = CourseDetail.objects.filter(
                    course__in=body['selected_course']).values_list('course__value', flat=True).distinct()
                    locked['locked_course'] += str(course_name[0])
                    branch_name = list(CourseDetail.objects.filter(
                    uid__in=body['selected_branch']).values("dept__value").distinct())
                    locked['locked_branch'] += str(branch_name[0]['dept__value'])
                    locked['locked_sem'] = str(StudentSemester.objects.filter(
                        sem_id__in=body['selected_sem']).values('sem')[0]['sem'])

                    for session in body['selected_session']:
                        sub_dict={}
                        subject_list = subject_faculty_sem(session, [faculty],body['selected_sem'][0])
                        if subject_list ==[]:
                            sub_dict['']=0
                            data_dict[str(session)]=sub_dict
                            continue
                        else:
                            for subject in subject_list:
                                marks = marks_subjectwise(
                                    session, [subject])
                                sub_dict[str(q['subject_id__sub_name'])+'('+str(q['subject_id__sub_alpha_code'])+' '+str(q['subject_id__sub_num_code'])+')']=marks
                                data_dict[str(session)]=sub_dict
                    count=0
                    for keys,values in data_dict.items():
                        count+=1
                        if len(data)>1:
                            for d in range(1,len(data)):
                                data[d].append(0)
                        data[0].append(keys)
                        id_list[0].append(keys)
                        for key ,value in values.items():
                            if len(data)>1:
                                for d in data:
                                    if d[0]==key:
                                        index=data.index(d)
                                        data[index][count]=value
                    response_values.append(data)
                    response_values.append(id_list)
                    response_values.append([locked])
                    response_values.append([body])
########################################### FACULTY SECTION SUBJECTWISE ##################################################
            elif body['type_request']=='faculty_section_subjectwise':
                for faculty in body['selected_employee']:
                    data=[['section-subject']]
                    id_list=[]
                    data_dict={}
                    locked = {'locked_session': "", 'locked_course': "", 'locked_branch': "", 'locked_sem': "",
                              'locked_subject': "", 'locked_section': "", 'locked_faculty': ""}  # dict for sending levels freezed
                    for session in body['selected_session']:
                        timetable = generate_session_table_name('FacultyTime_', session)
                        locked['locked_session'] += str(session)
                        if session == body['selected_session'][-1]:
                            qry = timetable.objects.filter(emp_id__in=[faculty],subject_id__sub_name__in=body['selected_subject'], subject_id_id__subject_type__in=[84, 86]).exclude(status='DELETE').values('section_id','section_id__section').distinct()
                            for q in qry:
                                if ['Section'+str(q['section_id__section'])] not in data:
                                    data.append(['Section'+str(q['section_id__section'])])
                                    # id_list.append([q['section_id']])
                            break
                        else:
                            locked['locked_session'] += ','
                        qry = timetable.objects.filter(emp_id__in=[faculty],subject_id__sub_name__in=body['selected_subject'],subject_id_id__subject_type__in=[84, 86]).exclude(status='DELETE').values('section_id','section_id__section').distinct()
                        for q in qry:
                            if ['Section'+str(q['section_id__section'])]not in data:
                                data.append(['Section'+str(q['section_id__section'])])
                                # id_list.append([q['section_id']])
                    emp = EmployeePrimdetail.objects.filter(
                        emp_id=faculty).values('name', 'emp_id')
                    locked['locked_faculty'] += str(
                        emp[0]['name']+'( '+str(emp[0]['emp_id'])+' )')
                    course_name = CourseDetail.objects.filter(
                    course__in=body['selected_course']).values_list('course__value', flat=True).distinct()
                    locked['locked_course'] += str(course_name[0])
                    branch_name = list(CourseDetail.objects.filter(
                    uid__in=body['selected_branch']).values("dept__value").distinct())
                    locked['locked_branch'] += str(branch_name[0]['dept__value'])
                    locked['locked_sem'] = str(StudentSemester.objects.filter(
                        sem_id__in=body['selected_sem']).values('sem')[0]['sem'])

                    subjectinfo = generate_session_table_name(
                    "SubjectInfo_", session)
                    subjectss = subjectinfo.objects.filter(sub_name__in=body['selected_subject']).exclude(status='DELETE').values(
                    'sub_name', 'sub_alpha_code', 'sub_num_code','subject_type').distinct()
                    locked['locked_subject'] = str(
                    subjectss[0]['sub_name']+" ( "+subjectss[0]['sub_alpha_code']+" "+subjectss[0]['sub_num_code']+" ) ")

                    for session in body['selected_session']:
                        section_dict={}
                        section_list = faculty_subject_section(session, [faculty],body['selected_subject'][0])#used subject name instead of id, AS have diff sub id of same sem for diff session
                        if section_list ==[]:
                            section_dict['']=0
                            data_dict[str(session)]=section_dict
                            continue
                        else:
                            for section in section_list:
                                marks = marks_subjectwise_sub_section(
                                    session, body['selected_subject'])
                                section_dict['Section'+str(q['section_id__section'])]=marks
                                data_dict[str(session)]=section_dict
                    count=0
                    for keys,values in data_dict.items():
                        count+=1
                        if len(data)>1:
                            for d in range(1,len(data)):
                                data[d].append(0)
                        data[0].append(keys)
                        for key ,value in values.items():
                            if len(data)>1:
                                for d in data:
                                    if d[0]==key:
                                        index=data.index(d)
                                        data[index][count]=value
                    response_values.append(data)
                    response_values.append(id_list)
                    response_values.append([locked])
                    response_values.append([body])
            return functions.RESPONSE(response_values, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(response_values, statusCodes.STATUS_SUCCESS)
    else:
        response_values = statusMessages.MESSAGE_UNAUTHORIZED
        return functions.RESPONSE(response_values, statusCodes.STATUS_UNAUTHORIZED)

###############
###############
# below this code of extenal marks analyzer by ritika

###############
###############


def get_subjects(sem, dept, session_name):
    subject_type = ["THEORY", "ELECTIVE/SPECIALIZATION"]
    SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
    query = SubjectInfo.objects.filter(
        sem__sem=sem, sem__dept=dept, subject_type__value__in=subject_type).exclude(status='DELETE')
    query_sub = query.exclude(max_university_marks=0).values(
        'sub_name', 'id', 'sub_alpha_code', 'sub_num_code')
    return list(query_sub)


def get_sub(sem, dept, session_name, id):
    subject_type = ["THEORY", "ELECTIVE/SPECIALIZATION"]
    SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
    query = SubjectInfo.objects.filter(
        id=id, sem__sem=sem, sem__dept=dept, subject_type__value__in=subject_type).exclude(status='DELETE')
    query_sub = query.exclude(max_university_marks=0).values(
        'sub_name', 'sub_alpha_code', 'sub_num_code')
    return list(query_sub)

# added status=DELETE filter in get_sec which was previously defined in StudentPortal/views.py############################################3


def get_sec_(dept, sem):
    # dept=41,42.sem=1,3,5,7
    q4 = list(StudentSemester.objects.filter(dept__in=dept,
                                             sem__in=sem).values_list('sem_id', flat=True))
    q5 = list(Sections.objects.filter(sem_id__in=q4).exclude(status="DELETE").annotate(
        max1=Count('section')).values_list('section', flat=True))
    section = set()
    for q in q5:
        if q not in section:
            section.add(q)

    d1 = {'sec': sorted(section)}
    return(d1)


def average_calculation(average):
    if((average['avg_obt'] == None or average['avg_total'] == None) or (average['avg_total'] == 0)):
        per = 0
    else:
        per = (int(average['avg_obt'])/int(average['avg_total']))*100
        if per > 100:
            per=100
    return round(per, 3)


def average_function(param, body, type_request):
    # param=course
    # result:average course
    if(type_request == "univ_avg"):
        average_all = []
        for session_name in body['selected_session']:
            markstable = generate_session_table_name(
                "StudentUniversityMarks_", session_name)
            average_qry = markstable.objects.filter(subject_id__sem__dept__course=param).exclude(external_marks__isnull=True).aggregate(avg_obt=Sum("external_marks"),
                                                                                                                                        avg_total=Sum("subject_id__max_university_marks"))
            per = average_calculation(average_qry)
            average_all.append(per)
        return average_all
# param=branch
# average=branch
    if(type_request == "univ_avg_branch"):
        average_all = []
        subject_type = ["THEORY", "ELECTIVE/SPECIALIZATION"]

        for session_name in body['selected_session']:
            markstable = generate_session_table_name(
                "StudentUniversityMarks_", session_name)
            average_qry = markstable.objects.filter(subject_id__sem__dept__course__in=body['selected_course'],
                                                    subject_id__subject_type__value__in=subject_type,
                                                    subject_id__sem__dept=param
                                                    ).exclude(external_marks__isnull=True).aggregate(avg_obt=Sum("external_marks"), avg_total=Sum("subject_id__max_university_marks"))
            per = average_calculation(average_qry)
            average_all.append(per)
        return average_all
# param=sem
# average=sem
    if(type_request == "univ_avg_semester"):
        average_all = []
        subject_type = ["THEORY", "ELECTIVE/SPECIALIZATION"]
        for session_name in body['selected_session']:
            markstable = generate_session_table_name(
                "StudentUniversityMarks_", session_name)
            average_qry = markstable.objects.filter(subject_id__sem__dept__course__in=body['selected_course'],
                                                    subject_id__subject_type__value__in=subject_type,
                                                    subject_id__sem__dept__in=body['selected_branch'], subject_id__sem__sem=param).exclude(external_marks__isnull=True).aggregate(avg_obt=Sum("external_marks"), avg_total=Sum("subject_id__max_university_marks"))
            per = average_calculation(average_qry)
            average_all.append(per)
        return average_all
# param=sec
# average=sec
    if(type_request == "univ_avg_section"):
        subject_type = ["THEORY", "ELECTIVE/SPECIALIZATION"]
        average_all = []
        for session_name in body['selected_session']:
            markstable = generate_session_table_name(
                "StudentUniversityMarks_", session_name)
            average_qry = markstable.objects.filter(subject_id__sem__dept__course__in=body['selected_course'],
                                                    subject_id__sem__dept__in=body['selected_branch'],
                                                    subject_id__sem__sem__in=body['selected_sem'],
                                                    subject_id__subject_type__value__in=subject_type,
                                                    uniq_id__section__section=param).exclude(external_marks__isnull=True).aggregate(avg_obt=Sum("external_marks"), avg_total=Sum("subject_id__max_university_marks"))
            per = average_calculation(average_qry)
            average_all.append(per)
        return average_all
# param=sub
# average:sub
    if(type_request == "univ_avg_sub"):
        average_all = []
        subject_type = ["THEORY", "ELECTIVE/SPECIALIZATION"]
        for session_name in body['selected_session']:
            markstable = generate_session_table_name(
                "StudentUniversityMarks_", session_name)
            qry1 = markstable.objects.filter(subject_id__sem__dept__course__in=body['selected_course'],
                                             subject_id__sem__dept__in=body['selected_branch'],
                                             subject_id__sem__sem__in=body['selected_sem'],
                                             uniq_id__sem_id__sem__in=body['selected_sem'], subject_id=param).exclude(external_marks__isnull=True)
            # if(qry1.values_list("subject_id__sub_name",flat=True)=="PYTHON PROGRAMMING"):
            average_qry = qry1.aggregate(avg_obt=Sum(
                "external_marks"), avg_total=Sum("subject_id__max_university_marks"))
            per = average_calculation(average_qry)
            average_all.append(per)
        return average_all
# param =sub
# average=sub_sectionwise###returns section wise subject performanace
    if(type_request == "univ_subject_sectionwise"):
        average_all = []
        subject_type = ["THEORY", "ELECTIVE/SPECIALIZATION"]
        for session_name in body['selected_session']:
            markstable = generate_session_table_name(
                "StudentUniversityMarks_", session_name)
            average_qry = markstable.objects.filter(subject_id__sem__dept__course__in=body['selected_course'],
                                                    subject_id__sem__dept__in=body['selected_branch'],
                                                    subject_id__sem__sem__in=body['selected_sem'],
                                                    subject_id__subject_type__value__in=subject_type,
                                                    uniq_id__section__section__in=body['selected_section'],
                                                    subject_id=param).exclude(external_marks__isnull=True).aggregate(avg_obt=Sum("external_marks"), avg_total=Sum("subject_id__max_university_marks"))
            per = average_calculation(average_qry)
            average_all.append(per)
        return average_all
# param=sec
# average=sec_subjectwise###returns subject wise section performanace
    if(type_request == "univ_section_subjectwise"):
        average_all = []
        subject_type = ["THEORY", "ELECTIVE/SPECIALIZATION"]
        for session_name in body['selected_session']:
            markstable = generate_session_table_name(
                "StudentUniversityMarks_", session_name)
            average_qry = markstable.objects.filter(subject_id__sem__dept__course__in=body['selected_course'],
                                                    subject_id__sem__dept__in=body['selected_branch'],
                                                    subject_id__sem__sem__in=body['selected_sem'],
                                                    subject_id__subject_type__value__in=subject_type,
                                                    subject_id__in=body["selected_subject"],
                                                    uniq_id__section__section=param).exclude(external_marks__isnull=True).aggregate(avg_obt=Sum("external_marks"), avg_total=Sum("subject_id__max_university_marks"))
            per = average_calculation(average_qry)
            average_all.append(per)
        return average_all
    else:
        return -1


def external_marks_analyser(request):
    if checkpermission(request, [rolesCheck.ROLE_MARKS_ANALYSIS_CORDINATOR]) == statusCodes.STATUS_SUCCESS:
        if (requestMethod.GET_REQUEST(request)):
            if(requestType.custom_request_type(request.GET, 'univmarks_get__course')):
                response_values = {}
                session_range = list(Semtiming.objects.filter(
                    sem_start__gte="2018-06-01").values('uid', 'session', 'session_name'))
                response_values['session_range'] = session_range
                response_values['courses'] = get_course()
                return functions.RESPONSE(response_values, statusCodes.STATUS_SUCCESS)
            else:
                return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
##
#############################################################################################################################################################################################################################################
        if (requestMethod.POST_REQUEST(request)):
            body = json.loads(request.body)
            if (body['type_request'] == 'univ_avg'):
                response_values = [[['course']], [['course']], [
                    {'selected_session': "", 'selected_course': "", "selected_branch": "", "sem": "", "sub": "", "sec": ""}], [body]]
                type_request = body["type_request"]
                row = 0
                for session in body['selected_session']:
                    response_values[0][0].append(session)
                    response_values[1][0].append(session)

                response_values[2][0]['selected_session'] += ", ".join(
                    body['selected_session'])
                for course in body['selected_course']:
                    row += 1
                    course_name = list(CourseDetail.objects.filter(course=course).values(
                        "course__value", "course__sno").order_by("course__value").distinct())
                    response_values[0].append(
                        [course_name[0]['course__value']])
                    response_values[1].append([course_name[0]['course__sno']])
                    type_request = 'univ_avg'
                    average_all = average_function(course, body, type_request)
                    for avg in average_all:
                        response_values[0][row].append(avg)
                        response_values[1][row].append(avg)

                return functions.RESPONSE(response_values, statusCodes.STATUS_SUCCESS)
###
#############################################################################################################################################################################################################################################
            if(body["type_request"] == "univ_avg_branch"):
                row = 0
                response_values = [[['branch']], [['branch']], [
                    {'selected_session': "", 'selected_course': "", "selected_branch": "", "sem": "", "sub": "", "sec": ""}], [body]]
                type_request = body["type_request"]
                branch_list = get_branch(body['selected_course'])
                course_name = list(CourseDetail.objects.filter(course=body['selected_course'][0]).values(
                    "course__value", "course__sno").order_by("course__value").distinct())

                response_values[2][0]['selected_session'] += ", ".join(
                    body['selected_session'])
                response_values[2][0]['selected_course'] += str(
                    course_name[0]["course__value"])

                for session in body['selected_session']:
                    response_values[0][0].append(session)
                    response_values[1][0].append(session)
                for branch in range(len(branch_list)):
                    row += 1
                    branch_name = list(CourseDetail.objects.filter(uid=branch_list[branch]['uid']).values(
                        "dept__value").order_by("dept__value").distinct())     # 'uniq_id__uniq_id__dept_detail__dept__value'
                    response_values[0].append([branch_name[0]['dept__value']])
                    response_values[1].append([branch_list[branch]['uid']])
                    average_all = average_function(
                        branch_list[branch]['uid'], body, type_request)
                    for avg in average_all:
                        response_values[0][row].append(avg)
                        response_values[1][row].append(avg)
                return functions.RESPONSE(response_values, statusCodes.STATUS_SUCCESS)
##
#############################################################################################################################################################################################################################################
            if (body['type_request'] == 'univ_avg_semester'):
                row = 0
                response_values = [[['semester']], [['semester']], [
                    {'selected_session': "", 'selected_course': "", "selected_branch": "", "sem": "", "sub": "", "sec": ""}], [body]]
                type_request = body["type_request"]
                sem = get_semester(body['selected_branch'][0])
                sem_list = []
                course_name = list(CourseDetail.objects.filter(course=body['selected_course'][0]).values(
                    "course__value", "course__sno").order_by("course__value").distinct())
                response_values[2][0]['selected_session'] += ", ".join(
                    body['selected_session'])
                response_values[2][0]['selected_course'] += str(
                    course_name[0]["course__value"])
                branch_name = list(CourseDetail.objects.filter(uid=body['selected_branch'][0]).values(
                    "dept__value").order_by("dept__value").distinct())
                response_values[2][0]['selected_branch'] += branch_name[0]["dept__value"]
                for session in body['selected_session']:
                    if(body['selected_branch'][0] != 59):
                        if(session[-1] == "e"):
                            response_values[0][0].append(session)
                            response_values[1][0].append(session)
                            for index in range(len(sem)):
                                if(int(sem[index]['sem']) % 2 == 0 and sem[index]['sem'] not in sem_list and int(sem[index]['sem']) != 2):
                                    sem_list.append(sem[index]['sem'])
                        else:
                            response_values[0][0].append(session)
                            response_values[1][0].append(session)
                            for index in range(len(sem)):
                                if(int(sem[index]['sem']) % 2 != 0 and sem[index]['sem'] not in sem_list and int(sem[index]['sem']) != 1):
                                    sem_list.append(sem[index]['sem'])
                    else:
                        response_values[0][0].append(session)
                        response_values[1][0].append(session)
                        for index in range(len(sem)):
                            if(sem[index]['sem'] not in sem_list):
                                sem_list.append(sem[index]['sem'])
                for sem in sem_list:
                    row += 1
                    response_values[0].append(["Semester- "+str(sem)])
                    response_values[1].append([sem])
                    average_all = average_function(sem, body, type_request)
                    for avg in average_all:
                        response_values[0][row].append(avg)
                        response_values[1][row].append(avg)
                return functions.RESPONSE(response_values, statusCodes.STATUS_SUCCESS)
##
#############################################################################################################################################################################################################################################
            if (body['type_request'] == 'univ_avg_section'):
                response_values = [[['section']], [['section']], [
                    {'selected_session': "", 'selected_course': "", "selected_branch": "", "sem": "", "sub": "", "sec": ""}], [body]]
                row = 0
                type_request = body["type_request"]
                # {'sec':["A","B"]}
                sec_list = get_sec_(
                    body['selected_branch'], body['selected_sem'])
                course_name = list(CourseDetail.objects.filter(course=body['selected_course'][0]).values(
                    "course__value", "course__sno").order_by("course__value").distinct())
                response_values[2][0]['selected_session'] += ", ".join(
                    body['selected_session'])
                response_values[2][0]['selected_course'] += str(
                    course_name[0]["course__value"])
                branch_name = list(CourseDetail.objects.filter(uid=body['selected_branch'][0]).values(
                    "dept__value").order_by("dept__value").distinct())
                response_values[2][0]['selected_branch'] += branch_name[0]["dept__value"]
                response_values[2][0]['sem'] += str(body['selected_sem'][0])
                for session in body['selected_session']:
                    response_values[0][0].append(session)
                    response_values[1][0].append(session)
                for section in range(len(sec_list['sec'])):
                    row += 1
                    response_values[0].append([sec_list['sec'][section]])
                    response_values[1].append([sec_list['sec'][section]])
                    average_all = average_function(
                        sec_list['sec'][section], body, type_request)
                    for avg in average_all:
                        response_values[0][row].append(avg)
                        response_values[1][row].append(avg)
                return functions.RESPONSE(response_values, statusCodes.STATUS_SUCCESS)
##
#############################################################################################################################################################################################################################################
            if (body['type_request'] == 'univ_avg_sub'):
                response_values = [[['subject']], [['subject']], [
                    {'selected_session': "", 'selected_course': "", "selected_branch": "", "sem": "", "sub": "", "sec": ""}], [body]]
                row = 0
                type_request = body["type_request"]
                total_sub_list = {}
                overall_sub_list = []
                course_name = list(CourseDetail.objects.filter(course=body['selected_course'][0]).values(
                    "course__value", "course__sno").order_by("course__value").distinct())
                response_values[2][0]['selected_session'] += ", ".join(
                    body['selected_session'])
                response_values[2][0]['selected_course'] += str(
                    course_name[0]["course__value"])
                branch_name = list(CourseDetail.objects.filter(uid=body['selected_branch'][0]).values(
                    "dept__value").order_by("dept__value").distinct())
                response_values[2][0]['selected_branch'] += branch_name[0]["dept__value"]
                response_values[2][0]['sem'] += str(body['selected_sem'][0])
                row = 0
                type_request = body["type_request"]
                # total_sub_list={}
                # total_sub_name=list()
                # for session in body['selected_session']:
                #     response_values[0][0].append(session)
                #     response_values[1][0].append(session)
                #     subject_list=get_subjects(body['selected_sem'][0],body["selected_branch"][0],session)
                #     for index in range(len(subject_list)):
                #         if(subject_list[index]['sub_name'] not in total_sub_name):
                #             total_sub_name.append(subject_list[index]['sub_name'])
                # for subject_name in total_sub_name:
                #     row+=1
                #     response_values[0].append([subject_name])
                #     response_values[1].append([subject_name])
                #     average_all=average_function(subject_name,body,type_request)
                #     for avg in average_all:
                #         response_values[0][row].append(avg)
                #         response_values[1][row].append(avg)

                total_sub_list = {'sub_id': [], 'sub': []}
                for session in body['selected_session']:
                    response_values[0][0].append(session)
                    response_values[1][0].append(session)
                    subject_list = get_subjects(
                        body['selected_sem'][0], body["selected_branch"][0], session)
                    for index in range(len(subject_list)):
                        total_sub_list['sub_id'].append(
                            subject_list[index]['id'])
                        total_sub_list['sub'].append(
                            subject_list[index]['sub_name']+' ( '+subject_list[index]['sub_alpha_code']+" "+subject_list[index]['sub_num_code']+' )')
                for subject in range(len(total_sub_list['sub_id'])):
                    row += 1
                    response_values[0].append([total_sub_list['sub'][subject]])
                    response_values[1].append(
                        [total_sub_list['sub_id'][subject]])
                    average_all = average_function(
                        total_sub_list['sub_id'][subject], body, type_request)
                    for avg in average_all:
                        response_values[0][row].append(avg)
                        response_values[1][row].append(avg)

                return functions.RESPONSE(response_values, statusCodes.STATUS_SUCCESS)
##
############################################################################################################################################################################################################################
            if(body['type_request'] == "univ_subject_sectionwise"):
                response_values = [[['section-subject']], [], [
                    {'selected_session': "", 'selected_course': "", "selected_branch": "", "sem": "", "sub": "", "sec": ""}], [body]]
                row = 0
                type_request = body["type_request"]
                course_name = list(CourseDetail.objects.filter(course=body['selected_course'][0]).values(
                    "course__value", "course__sno").order_by("course__value").distinct())
                response_values[2][0]['selected_session'] += ", ".join(
                    body['selected_session'])
                response_values[2][0]['selected_course'] += str(
                    course_name[0]["course__value"])
                branch_name = list(CourseDetail.objects.filter(uid=body['selected_branch'][0]).values(
                    "dept__value").order_by("dept__value").distinct())
                response_values[2][0]['selected_branch'] += branch_name[0]["dept__value"]
                response_values[2][0]['sem'] += str(body['selected_sem'][0])
                response_values[2][0]['sec'] += str(
                    body['selected_section'][0])
                # total_sub_name=list()

                total_sub_list = {'sub_id': [], 'sub': []}

                # for session in body['selected_session']:
                #     response_values[0][0].append(session)
                #     # response_values[1][0].append(session)
                #     subject_list=get_subjects(body['selected_sem'][0],body["selected_branch"][0],session)
                #     for index in range(len(subject_list)):
                #         if(subject_list[index]['sub_name'] not in total_sub_name):
                #             total_sub_name.append(subject_list[index]['sub_name'])
                # for subject_name in total_sub_name:
                #     row+=1
                #     response_values[0].append([subject_name])
                #     # response_values[1].append([subject_name])
                #     average_all=average_function(subject_name,body,type_request)
                #     for avg in average_all:
                #         response_values[0][row].append(avg)
                #         # response_values[1][row].append(avg)

                for session in body['selected_session']:
                    response_values[0][0].append(session)
                    # response_values[1][0].append(session)
                    subject_list = get_subjects(
                        body['selected_sem'][0], body["selected_branch"][0], session)
                    for index in range(len(subject_list)):
                        total_sub_list['sub_id'].append(
                            subject_list[index]['id'])
                        total_sub_list['sub'].append(
                            subject_list[index]['sub_name']+' ( '+subject_list[index]['sub_alpha_code']+" "+subject_list[index]['sub_num_code']+' )')
                for subject in range(len(total_sub_list['sub_id'])):
                    row += 1
                    response_values[0].append([total_sub_list['sub'][subject]])
                    # response_values[1].append([total_sub_list['sub_id'][subject]])
                    average_all = average_function(
                        total_sub_list['sub_id'][subject], body, type_request)
                    for avg in average_all:
                        response_values[0][row].append(avg)
                        # response_values[1][row].append(avg)

                return functions.RESPONSE(response_values, statusCodes.STATUS_SUCCESS)
###
########################################################################################################################################################################################
            if (body['type_request'] == 'univ_section_subjectwise'):
                response_values = [[['subject-section']], [], [
                    {'selected_session': "", 'selected_course': "", "selected_branch": "", "sem": "", "sub": "", "sec": ""}], [body]]
                row = 0
                type_request = body["type_request"]
                sec_list = get_sec_(
                    body['selected_branch'], body['selected_sem'])
                course_name = list(CourseDetail.objects.filter(course=body['selected_course'][0]).values(
                    "course__value", "course__sno").order_by("course__value").distinct())
                response_values[2][0]['selected_session'] += ", ".join(
                    body['selected_session'])
                response_values[2][0]['selected_course'] += str(
                    course_name[0]["course__value"])
                branch_name = list(CourseDetail.objects.filter(uid=body['selected_branch'][0]).values(
                    "dept__value").order_by("dept__value").distinct())
                response_values[2][0]['selected_branch'] += branch_name[0]["dept__value"]
                response_values[2][0]['sem'] += str(body['selected_sem'][0])
                # for session in body['selected_session']:
                response_values[0][0].append(body['selected_session'][0])
                # sub=get_sub(body["selected_subject"][0],body['selected_session'][0])
                selected_sub = get_sub(body["selected_sem"][0], body["selected_branch"]
                                       [0], body["selected_session"][0], body['selected_subject'][0])[0]
                response_values[2][0]['sub'] += selected_sub['sub_name'] + \
                    " ( "+selected_sub['sub_alpha_code'] + \
                    " "+selected_sub['sub_num_code']+" )"
                # response_values[2][0]['sub']+=

                for section in range(len(sec_list['sec'])):
                    row += 1
                    response_values[0].append([sec_list['sec'][section]])
                    # response_values[1].append([sec_list['sec'][section]])
                    average_all = average_function(
                        sec_list['sec'][section], body, type_request)
                    for avg in average_all:
                        response_values[0][row].append(avg)
                        # response_values[1][row].append(avg)
                return functions.RESPONSE(response_values, statusCodes.STATUS_SUCCESS)
##
##########################################################################################################################################################################################
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


