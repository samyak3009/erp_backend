from Store_data . models import *
from .views import *
from Registrar.models import *
from .models import *
from login.views import checkpermission,generate_session_table_name
from erp.constants_functions.functions import *



########################################################### Divyanshu - To return the total attendanace percentage  ###################################################################################
def attendance_percentage(present,total):
    percentage = 0
    if(total != None ):
        if total >0:
            percentage = round(100*present/total)
    return percentage

def get_overall_att_percentage_of_session(type_att,value,session_name):
    Store_Attendance = generate_session_table_name("Store_Attendance_", session_name)
    percentage_overall=0
    
    if type_att=='course':
        att=Store_Attendance.objects.filter(uniq_id__sem_id__dept__course_id=value).values('uniq_id').aggregate(total=Sum('attendance_total') , present=Sum('attendance_present'))
        percentage_overall=attendance_percentage(att["present"],att["total"])
        
    elif type_att=='branch':
        att=Store_Attendance.objects.filter(uniq_id__sem_id__dept__dept_id=value).values('uniq_id').aggregate(total=Sum('attendance_total') , present=Sum('attendance_present'))
        percentage_overall=attendance_percentage(att["present"],att["total"])
      
    elif type_att=='semester':
        att=Store_Attendance.objects.filter(uniq_id__sem_id=value).values('uniq_id').aggregate(total=Sum('attendance_total') , present=Sum('attendance_present'))
        percentage_overall=attendance_percentage(att["present"],att["total"])
       
    elif type_att=='section':
        att=Store_Attendance.objects.filter(uniq_id__section_id=value).values('uniq_id').aggregate(total=Sum('attendance_total') , present=Sum('attendance_present'))
        percentage_overall=attendance_percentage(att["present"],att["total"])
       
    elif type_att=='subject':
        Store_Attendance_Total = generate_session_table_name("Store_Attendance_Total_", session_name)
        att=Store_Attendance_Total.objects.filter(subject=value).values('uniq_id').aggregate(total=Sum('attendance_total') , present=Sum('attendance_present'))
        percentage_overall=attendance_percentage(att["present"],att["total"])
    
    elif type_att=='subject_section':
        Store_Attendance_Total = generate_session_table_name("Store_Attendance_Total_", session_name)
        att=Store_Attendance_Total.objects.filter(uniq_id__section_id=value[0],subject=value[1]).values('uniq_id').aggregate(total=Sum('attendance_total') , present=Sum('attendance_present'))
        percentage_overall=attendance_percentage(att["present"],att["total"])
   
    return percentage_overall


########################################################### - Attendance Analyser - ###################################################################################################################
def attendance_analyser(request):
    response_values=[{}]
    addon={}
    body={}

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if checkpermission(request, [rolesCheck.ROLE_HOD]) == statusCodes.STATUS_SUCCESS:
                if (requestMethod.GET_REQUEST(request)):
                    if(requestType.custom_request_type(request.GET, 'get_course')):
                        session_range = list(Semtiming.objects.filter(sem_start__gte="2018-06-01").values('uid', 'session', 'session_name'))
                        response_values[0]['session_range']=session_range
                        response_values[0]['courses']=get_course()
                        status=statusCodes.STATUS_SUCCESS
                    else:
                        status = statusCodes.STATUS_METHOD_NOT_ALLOWED
                
                elif (requestMethod.POST_REQUEST(request)):
                    body=json.loads(request.body)
                    addon={"request_type": body["request_type"],"session": [],"course": [],"branch": [],"semester": [],"subject": [],"section": []}#for frontend heading
                    roman_sem = ['I','II','III','IV','V','VI','VII','VIII']
                    session_range = list(Semtiming.objects.filter(uid__in=body['selected_session_ids']).order_by('uid').values('uid','session_name','sem_type'))
                    row=0
                    if (requestType.custom_request_type(body, 'course_att')):
                        response_values=[[['course']],[['course']]]
                        for session in session_range:
                            response_values[0][0].append(session["session_name"])
                            response_values[1][0].append(session["uid"])
                            addon["session"].append(session["session_name"])
                        for course in body['selected_course'] :
                            row += 1
                            course_name=list(CourseDetail.objects.filter(course=course).values("course__value","course__sno").distinct())
                            response_values[0].append([course_name[0]['course__value']])
                            response_values[1].append([course_name[0]['course__sno']])
                            addon["course"].append(course_name[0]['course__value'])
                            for session in session_range:
                                percentage=get_overall_att_percentage_of_session('course',course_name[0]['course__sno'],session["session_name"])
                                response_values[0][row].append(percentage)
                                response_values[1][row].append(percentage)
                        status=statusCodes.STATUS_SUCCESS
                        
                    elif(requestType.custom_request_type(body, 'department_att')):
                        response_values=[[['branch']],[['branch']]]
                        course_name=list(CourseDetail.objects.filter(course__in=body["selected_course"]).values("course__value","course__sno").distinct())
                        addon["course"].append(course_name[0]['course__value'])
                        for session in session_range:
                            response_values[0][0].append(session["session_name"])
                            response_values[1][0].append(session["uid"])
                            addon["session"].append(session["session_name"])
                        branch_name=list(CourseDetail.objects.filter(course_id__in=body['selected_course']).values("dept_id","dept_id__value").distinct())
                        for branch in branch_name:
                            row += 1
                            response_values[0].append([branch["dept_id__value"]])
                            response_values[1].append([branch["dept_id"]])
                            addon["branch"].append(branch["dept_id__value"])
                            for session in session_range:
                                percentage=get_overall_att_percentage_of_session('branch',branch["dept_id"],session["session_name"])
                                response_values[0][row].append(percentage)
                                response_values[1][row].append(percentage)
                        status=statusCodes.STATUS_SUCCESS
                        
                    elif(requestType.custom_request_type(body, 'semester_att')):
                        response_values=[[['semester']],[['semester']]]
                        course_name=list(CourseDetail.objects.filter(course__in=body["selected_course"]).values("course__value","course__sno").distinct())
                        addon["course"].append(course_name[0]['course__value'])
                        branch_name=list(CourseDetail.objects.filter(dept_id__in=body['selected_branch']).values("dept_id","dept_id__value").distinct())
                        addon["branch"].append(branch_name[0]["dept_id__value"])
                        get_sem = list(StudentSemester.objects.filter(dept__dept_id=body["selected_branch"][0],dept__course_id=body['selected_course'][0]).values('sem','sem_id'))
                        get_sem_ids=[]
                        odd=False
                        even=False
                        for session in session_range:
                            response_values[0][0].append(session["session_name"])
                            response_values[1][0].append(session["uid"])
                            if(session['sem_type']=="odd"):
                                odd=True
                            else:
                                even=True
                            addon["session"].append(session["session_name"])
                            #Applied Science dept__dept_id =567
                        if(body['selected_branch'][0] != 576):
                            if (odd):
                                get_sem_ids = list(StudentSemester.objects.filter(dept__dept_id=body["selected_branch"][0],dept__course_id=body['selected_course'][0]).annotate(odd=F('sem') % 2).filter(odd=True).values('sem','sem_id'))
                            else:
                                get_sem_ids = list(StudentSemester.objects.filter(dept__dept_id=body["selected_branch"][0],dept__course_id=body['selected_course'][0]).annotate(odd=F('sem') % 2).filter(odd=False).values('sem','sem_id'))
                            
                            if(body['selected_course'][0]==12):get_sem_ids = get_sem_ids[1:] #B.Tech course id = 12 
                        else:
                            if(odd):get_sem_ids.append(get_sem[0])
                            if(even):get_sem_ids.append(get_sem[1])
                        for sem in get_sem_ids:
                            row += 1
                            response_values[0].append([roman_sem[int(sem["sem"]-1)]])
                            response_values[1].append([sem["sem_id"]])
                            addon["semester"].append(roman_sem[int(sem["sem"]-1)])
                            if(body['selected_branch'][0] != 576):
                                for session in session_range:
                                    percentage=get_overall_att_percentage_of_session('semester', sem["sem_id"], session["session_name"])
                                    response_values[0][row].append(percentage)
                                    response_values[1][row].append(percentage)
                            else:
                                for session in session_range:
                                    percentage=get_overall_att_percentage_of_session('semester', sem["sem_id"], session["session_name"])
                                    response_values[0][row].append(percentage)
                                    response_values[1][row].append(percentage)
                        status=statusCodes.STATUS_SUCCESS
                        
                    elif(requestType.custom_request_type(body, 'section_att')):
                        addon["session"].append(session_range[0]["session_name"])
                        course_name=list(CourseDetail.objects.filter(course__in=body["selected_course"]).values("course__value","course__sno").distinct())
                        addon["course"].append(course_name[0]['course__value'])
                        branch_name=list(CourseDetail.objects.filter(dept_id__in=body['selected_branch']).values("dept_id","dept_id__value").distinct())
                        addon["branch"].append(branch_name[0]["dept_id__value"])
                        sem=StudentSemester.objects.filter(sem_id__in=body["selected_sem"]).values('sem','sem_id')
                        addon["semester"].append(roman_sem[int(sem[0]["sem"]-1)])
                        response_values=[[['section']],[['section']]]
                        response_values[0][0].append(session_range[0]["session_name"])
                        response_values[1][0].append(session_range[0]["uid"])
                        get_section_ids = Sections.objects.filter(sem_id__in=body["selected_sem"]).exclude(status="DELETE").values('section_id','section')
                        for sec in get_section_ids:
                            row += 1
                            response_values[0].append([sec["section"]])
                            response_values[1].append([sec["section_id"]])
                            addon["section"].append(sec["section"])
                            percentage=get_overall_att_percentage_of_session('section', sec["section_id"], session_range[0]["session_name"])
                            response_values[0][row].append(percentage)
                            response_values[1][row].append(percentage)
                        status=statusCodes.STATUS_SUCCESS
                        
                    elif(requestType.custom_request_type(body, 'subject_att')):
                        addon["session"].append(session_range[0]["session_name"])
                        course_name=list(CourseDetail.objects.filter(course__in=body["selected_course"]).values("course__value","course__sno").distinct())
                        addon["course"].append(course_name[0]['course__value'])
                        branch_name=list(CourseDetail.objects.filter(dept_id__in=body['selected_branch']).values("dept_id","dept_id__value").distinct())
                        addon["branch"].append(branch_name[0]["dept_id__value"])
                        sem=StudentSemester.objects.filter(sem_id__in=body["selected_sem"]).values('sem','sem_id')
                        addon["semester"].append(roman_sem[int(sem[0]["sem"]-1)])
                        response_values=[[['subject']],[['subject']]]
                        SubjectInfo = generate_session_table_name("SubjectInfo_", session_range[0]["session_name"])
                        query_sub = SubjectInfo.objects.filter(sem_id=body["selected_sem"][0]).exclude(status='DELETE').values( 'sub_name','id','sub_alpha_code', 'sub_num_code')
                        response_values[0][0].append(session_range[0]["session_name"])
                        response_values[1][0].append(session_range[0]["uid"])
                        for subject in query_sub:
                            row += 1
                            sub_name=[subject["sub_name"]+' ['+subject["sub_alpha_code"]+'-'+subject["sub_num_code"]+']']
                            response_values[0].append(sub_name)
                            response_values[1].append([subject["id"]])
                            addon["subject"].append(sub_name)
                            percentage=get_overall_att_percentage_of_session('subject', subject["id"], session_range[0]["session_name"])
                            response_values[0][row].append(percentage)
                            response_values[1][row].append(percentage)
                        status=statusCodes.STATUS_SUCCESS
                        
                    elif(requestType.custom_request_type(body, 'subject_sectionwise_att')):
                        addon["request_type"]=["SUBJECT SECTION"]
                        course_name=list(CourseDetail.objects.filter(course__in=body["selected_course"]).values("course__value","course__sno").distinct())
                        addon["course"].append(course_name[0]['course__value'])
                        branch_name=list(CourseDetail.objects.filter(dept_id__in=body['selected_branch']).values("dept_id","dept_id__value").distinct())
                        addon["branch"].append(branch_name[0]["dept_id__value"])
                        addon["session"].append(session_range[0]["session_name"])
                        sem=StudentSemester.objects.filter(sem_id__in=body["selected_sem"]).values('sem','sem_id')
                        addon["semester"].append(roman_sem[int(sem[0]["sem"]-1)])
                        response_values=[[['SUBJECT SECTION']],[['SUBJECT SECTION']]]
                        SubjectInfo = generate_session_table_name("SubjectInfo_", session_range[0]["session_name"])
                        subject = SubjectInfo.objects.filter(id__in=body["selected_subject"]).values( 'sub_name','id','sub_alpha_code', 'sub_num_code')
                        addon["subject"].append(subject[0]["sub_name"]+' ['+subject[0]["sub_alpha_code"]+'-'+subject[0]["sub_num_code"]+']')
                        response_values[0][0].append(session_range[0]["session_name"])
                        response_values[1][0].append(session_range[0]["uid"])
                        get_section_ids = Sections.objects.filter(sem_id__in=body["selected_sem"]).exclude(status="DELETE").values('section_id','section')
                        for sec in get_section_ids:
                            row += 1
                            response_values[0].append([sec["section"]])
                            response_values[1].append([sec["section_id"]])
                            addon["section"].append(sec["section"])
                            percentage=get_overall_att_percentage_of_session('subject_section', [sec["section_id"],body["selected_subject"][0]], session_range[0]["session_name"])
                            response_values[0][row].append(percentage)
                            response_values[1][row].append(percentage)
                        status=statusCodes.STATUS_SUCCESS
                        
                    elif(requestType.custom_request_type(body, 'section_subjectwise_att')):
                        addon["request_type"]=["SECTION SUBJECT"]
                        course_name=list(CourseDetail.objects.filter(course__in=body["selected_course"]).values("course__value","course__sno").distinct())
                        addon["course"].append(course_name[0]['course__value'])
                        branch_name=list(CourseDetail.objects.filter(dept_id__in=body['selected_branch']).values("dept_id","dept_id__value").distinct())
                        addon["branch"].append(branch_name[0]["dept_id__value"])
                        addon["session"].append(session_range[0]["session_name"])
                        sem=StudentSemester.objects.filter(sem_id__in=body["selected_sem"]).values('sem','sem_id')
                        addon["semester"].append(roman_sem[int(sem[0]["sem"]-1)])
                        sec = Sections.objects.filter(section_id__in=body["selected_section"]).exclude(status="DELETE").values('section_id','section')
                        addon["section"].append(sec[0]["section"])
                        response_values=[[['SECTION SUBJECT']],[['SECTION SUBJECT']]]
                        SubjectInfo = generate_session_table_name("SubjectInfo_", session_range[0]["session_name"])
                        query_sub = SubjectInfo.objects.filter(sem_id=body["selected_sem"][0]).exclude(status='DELETE').values( 'sub_name','id','sub_alpha_code', 'sub_num_code')
                        response_values[0][0].append(session_range[0]["session_name"])
                        response_values[1][0].append(session_range[0]["uid"])
                        get_section_ids = Sections.objects.filter(sem_id__in=body["selected_sem"]).exclude(status="DELETE").values('section_id','section')
                        for subject in query_sub:
                            row += 1
                            sub_name=[subject["sub_name"]+' ['+subject["sub_alpha_code"]+'-'+subject["sub_num_code"]+']']
                            response_values[0].append(sub_name)
                            response_values[1].append([subject["id"]])
                            addon["subject"].append(sub_name)
                            percentage=get_overall_att_percentage_of_session('subject_section',[body["selected_section"][0],subject["id"]] , session_range[0]["session_name"])
                            response_values[0][row].append(percentage)
                            response_values[1][row].append(percentage)
                        status=statusCodes.STATUS_SUCCESS
                    else:
                        status = statusCodes.STATUS_METHOD_NOT_ALLOWED
            else:
                status = statusCodes.STATUS_FORBIDDEN           
        else:
            status = statusCodes.STATUS_UNAUTHORIZED
    else:
        status = statusCodes.STATUS_SERVER_ERROR
    response_values.append(addon)
    response_values.append(body)
    # print("response_values",response_values)
    return functions.RESPONSE(response_values, status)
