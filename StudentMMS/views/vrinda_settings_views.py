from django.shortcuts import render
from django.db.models import F
from django.db.models import Min
from django.http import HttpResponse, JsonResponse
from datetime import date, datetime
import json
from django.db.models import Q, Sum, Count, Max, F
from itertools import groupby

from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, requestMethod, functions
from StudentMMS.constants_functions import requestType

from StudentMMS.models import *
from StudentAcademics.models import *
from Registrar.models import CourseDetail, StudentSemester, Semtiming, StudentDropdown, StudentPerDetail, StudentFamilyDetails
from login.models import EmployeeDropdown
from musterroll.models import EmployeePrimdetail, EmployeePerdetail


from login.views import checkpermission, generate_session_table_name
from StudentAcademics.functions import get_subject_multi_type
from StudentAcademics.views import getComponents, check_islocked, get_attendance_type, get_section_students
from .mms_function_views import get_btlevel, get_skillsetlevel, get_verb, get_skillsetlevel_filtered, get_btleveldata, get_vis_mis, get_attempt_type, get_exam_name, new_exam_dropdown, single_student_ct_marks, internal_exam_dropdown, create_order_chooser, create_order_by_subrule_no, get_bonusrule, get_ctrule_wise_student_marks, get_batch_session_dropdown, get_student_total_ct_marks, get_student_per_ct_marks, get_single_student_internal_marks
from .harsh_views import fetch_bonus_marks
# def mms_vision(request):
#   if academicCoordCheck.isNBACoordinator(request):
#       session_name = request.session['Session_name']
#       Dept_VisMis=generate_session_table_name("Dept_VisMis_",session_name)
#       if (requestMethod.GET_REQUEST(request)):
#           emp_id=request.session['hash1']
#           if(requestType.firstrequest(request.GET)):
#               data=[]
#               vis_mis=get_vis_mis()
#               data={'data':vis_mis}
#               return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
#           elif (requestType.custom_request_type(request.GET,'on_submit')):
#               dept=request.GET['dept']
#               data={}
#               type=request.GET['type']
#               q=Dept_VisMis.objects.filter(dept=dept,type=type,status="INSERT").values_list('description',flat=True)
#               data={'data':list(q)}
#           return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
#       elif (requestMethod.POST_REQUEST(request)):
#           emp_id=request.session['hash1']
#           data1=json.loads(request.body)
#           type=data1['type']
#           dept=data1['dept']

#           qry_sections = list(Sections.objects.filter(sem_id__dept=dept).values_list('section_id',flat=True))

#           if check_islocked('HOD',qry_sections,session_name):
#               return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

#           description=data1['description']
#           q=Dept_VisMis.objects.filter(dept=dept,type=type).update(status='DELETE')
#           q1=(Dept_VisMis(dept=CourseDetail.objects.get(uid=dept),type=type,description=d,added_by=EmployeePrimdetail.objects.get(emp_id=emp_id)) for d in description)
#           q2=Dept_VisMis.objects.bulk_create(q1)
#           if q>0:
#               data=statusMessages.MESSAGE_UPDATE
#           elif len(description)!=0:
#               data=statusMessages.MESSAGE_INSERT
#           else:
#               data=statusMessages.CUSTOM_MESSAGE('Kindly Check Your Data')
#           return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

#   else:
#       return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)
def mms_vision(request):
    if academicCoordCheck.isNBACoordinator(request):
        session_name = request.session['Session_name']
        Dept_VisMis = generate_session_table_name("Dept_VisMis_", session_name)
        if (requestMethod.GET_REQUEST(request)):
            emp_id = request.session['hash1']
            if(requestType.firstrequest(request.GET)):
                data = []
                vis_mis = get_vis_mis()
                data = {'data': vis_mis}
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
            elif (requestType.custom_request_type(request.GET, 'on_submit')):
                dept = request.GET['dept']
                data = {}
                type = request.GET['type']
                q = Dept_VisMis.objects.filter(dept=dept, type=type).exclude(status="DELETE").values('description', 'id')
                print(q, 'ffffffff')
                data = {'data': list(q)}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif (requestMethod.POST_REQUEST(request)):
            SubjectPEOMIMapping = generate_session_table_name("SubjectPEOMIMapping_", session_name)
            SubjectPOPEOMapping = generate_session_table_name("SubjectPOPEOMapping_", session_name)
            emp_id = request.session['hash1']
            data1 = json.loads(request.body)
            print(data1, 'data')
            type = data1['type']
            dept = data1['dept']

            qry_sections = list(Sections.objects.filter(sem_id__dept=dept).values_list('section_id', flat=True))

            if check_islocked('HOD', qry_sections, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

            delete_create = []
            add_vis_mis = set()
            new_des = []
            description = data1['description']
            added_vis_mis = list(Dept_VisMis.objects.filter(dept=dept, type=type).exclude(status="DELETE").values_list('description', flat=True))
            added_ids = list(Dept_VisMis.objects.filter(dept=dept, type=type, description__in=added_vis_mis).exclude(status="DELETE").values_list('id', flat=True).order_by('id'))

            ### to avoid entry of same description for multiple times ###
            defined_description = []
            #############################################################
            for d in description:
                new_des.append(d['description'])
                if d['id'] != None:
                    if d['description'] not in added_vis_mis:
                        # defined_description.append()
                        previous_text = Dept_VisMis.objects.filter(id=d['id']).exclude(status="DELETE").values_list('description', flat=True)
                        delete_create.append(previous_text[0])
                        Dept_VisMis.objects.filter(id=d['id']).exclude(status="DELETE").update(description=d['description'])
                    else:
                        defined_description.append(d['description'])
                else:
                    if d['description'] not in defined_description:
                        add_vis_mis.add(d['description'])
                        defined_description.append(d['description'])
                    else:
                        data = statusMessages.CUSTOM_MESSAGE('Duplicate entries are not allowed.')
                        return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
            deleted=[]
            not_deleted=[]
            for already_added in added_vis_mis:
                if already_added not in new_des and already_added not in delete_create:
                    to_be_deleted_id = list(Dept_VisMis.objects.filter(description=already_added).exclude(status="DELETE").values_list('id', flat=True).order_by('id'))
                    SubjectPEOMIMapping_check_mission=SubjectPEOMIMapping.objects.filter(m_id__in=to_be_deleted_id).exclude(status="DELETE").values_list('id',flat=True)
                    SubjectPOPEOMapping_check_po=SubjectPOPEOMapping.objects.filter(po_id__in=to_be_deleted_id).exclude(status="DELETE").values_list('id',flat=True)
                    SubjectPEOMIMapping_check_peo=SubjectPEOMIMapping.objects.filter(peo_id__in=to_be_deleted_id).exclude(status="DELETE").values_list('id',flat=True)
                    SubjectPOPEOMapping_check_peo=SubjectPOPEOMapping.objects.filter(peo_id__in=to_be_deleted_id).exclude(status="DELETE").values_list('id',flat=True)
                    if((len(SubjectPEOMIMapping_check_mission)==0) and (len(SubjectPOPEOMapping_check_po)==0) and (len(SubjectPEOMIMapping_check_peo)==0) and (len(SubjectPOPEOMapping_check_peo)==0)):
                        Dept_VisMis.objects.filter(description=already_added).exclude(status="DELETE").update(status="DELETE")
                        deleted.append(already_added)
                    else:
                        not_deleted.append(already_added)
            q1 = (Dept_VisMis(dept=CourseDetail.objects.get(uid=dept), type=type, description=d, added_by=EmployeePrimdetail.objects.get(emp_id=emp_id), status="DELETE") for d in delete_create)
            q2 = Dept_VisMis.objects.bulk_create(q1)

            q3 = (Dept_VisMis(dept=CourseDetail.objects.get(uid=dept), type=type, description=d, added_by=EmployeePrimdetail.objects.get(emp_id=emp_id)) for d in add_vis_mis)
            q4 = Dept_VisMis.objects.bulk_create(q3)
            data={}
            data['delete']=deleted
            data['not_deleted']=not_deleted
            if len(data['delete'])==0 and len(data['not_deleted'])==0:
                data['msg'] = statusMessages.MESSAGE_INSERT                
            else:
                data['msg'] = statusMessages.MESSAGE_UPDATE
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)

# def mms_vision(request):
#     if academicCoordCheck.isNBACoordinator(request):
#         session_name = request.session['Session_name']
#         Dept_VisMis = generate_session_table_name("Dept_VisMis_", session_name)
#         if (requestMethod.GET_REQUEST(request)):
#             emp_id = request.session['hash1']
#             if(requestType.firstrequest(request.GET)):
#                 data = []
#                 vis_mis = get_vis_mis()
#                 data = {'data': vis_mis}
#                 return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
#             elif (requestType.custom_request_type(request.GET, 'on_submit')):
#                 dept = request.GET['dept']
#                 data = {}
#                 type = request.GET['type']
#                 q = Dept_VisMis.objects.filter(dept=dept, type=type).exclude(status="DELETE").values('description', 'id')
#                 print(q, 'ffffffff')
#                 data = {'data': list(q)}
#             return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

#         elif (requestMethod.POST_REQUEST(request)):
#             #SubjectCOPOMapping = generate_session_table_name("SubjectCOPOMapping_", session_name)
#             SubjectPEOMIMapping = generate_session_table_name("SubjectPEOMIMapping_", session_name)
#             SubjectPOPEOMapping = generate_session_table_name("SubjectPOPEOMapping_", session_name)
#             #SurveyAddQuestions = generate_session_table_name("SurveyAddQuestions_", session_name)
#             emp_id = request.session['hash1']
#             data1 = json.loads(request.body)
#             print(data1, 'data')
#             type = data1['type']
#             dept = data1['dept']

#             qry_sections = list(Sections.objects.filter(sem_id__dept=dept).values_list('section_id', flat=True))

#             if check_islocked('HOD', qry_sections, session_name):
#                 return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

#             delete_create = []
#             add_vis_mis = set()
#             new_des = []
#             description = data1['description']
#             added_vis_mis = list(Dept_VisMis.objects.filter(dept=dept, type=type).exclude(status="DELETE").values_list('description', flat=True))
#             added_ids = list(Dept_VisMis.objects.filter(dept=dept, type=type, description__in=added_vis_mis).exclude(status="DELETE").values_list('id', flat=True).order_by('id'))
#             print(description,"description")
#             print(added_vis_mis,"added_vis_mis")
#             print(added_ids,"added_ids")
#             ### to avoid entry of same description for multiple times ###
#             defined_description = []
#             #############################################################
#             for d in description:
#                 new_des.append(d['description'])
#                 if d['id'] != None:
#                     if d['description'] not in added_vis_mis:
#                         # defined_description.append()
#                         previous_text = Dept_VisMis.objects.filter(id=d['id']).exclude(status="DELETE").values_list('description', flat=True)
#                         delete_create.append(previous_text[0])
#                         Dept_VisMis.objects.filter(id=d['id']).exclude(status="DELETE").update(description=d['description'])
#                     else:
#                         defined_description.append(d['description'])
#                 else:
#                     if d['description'] not in defined_description:
#                         add_vis_mis.add(d['description'])
#                         defined_description.append(d['description'])
#                     else:
#                         data = statusMessages.CUSTOM_MESSAGE('Duplicate entries are not allowed.')
#                         return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
#             deleted=[]
#             not_deleted=[]
#             for already_added in added_vis_mis:
#                 if already_added not in new_des and already_added not in delete_create:
#                     to_be_deleted_id = list(Dept_VisMis.objects.filter(description=already_added).exclude(status="DELETE").values_list('id', flat=True).order_by('id'))
#                     SubjectPEOMIMapping_check_mission=SubjectPEOMIMapping.objects.filter(m_id__in=to_be_deleted_id).exclude(status="DELETE").values_list('id',flat=True)
#                     SubjectPOPEOMapping_check_po=SubjectPOPEOMapping.objects.filter(po_id__in=to_be_deleted_id).exclude(status="DELETE").values_list('id',flat=True)
#                     if((len(SubjectPEOMIMapping_check_mission)==0) and (len(SubjectPOPEOMapping_check_po)==0)):
#                         Dept_VisMis.objects.filter(description=already_added).exclude(status="DELETE").update(status="DELETE")
#                         deleted.append(already_added)
#                     else:
#                         not_deleted.append(already_added)
#             q1 = (Dept_VisMis(dept=CourseDetail.objects.get(uid=dept), type=type, description=d, added_by=EmployeePrimdetail.objects.get(emp_id=emp_id), status="DELETE") for d in delete_create)
#             q2 = Dept_VisMis.objects.bulk_create(q1)

#             q3 = (Dept_VisMis(dept=CourseDetail.objects.get(uid=dept), type=type, description=d, added_by=EmployeePrimdetail.objects.get(emp_id=emp_id)) for d in add_vis_mis)
#             q4 = Dept_VisMis.objects.bulk_create(q3)
#             data={}
#             data['delete']=deleted
#             data['not_deleted']=not_deleted
#             if len(data['delete'])==0 and len(data['not_deleted'])==0:
#                 data['msg'] = statusMessages.MESSAGE_INSERT                
#             else:
#                 data['msg'] = statusMessages.MESSAGE_UPDATE
#             return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

#     else:
#         return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)

def check_for_previous_format(session_name,ques_paper_id):
    QuesPaperFormat = generate_session_table_name("QuesPaperFormat_", session_name)
    QuesPaperApplicableOn = generate_session_table_name("QuesPaperApplicableOn_", session_name)
    #ques_paper_id=QuesPaperApplicableOn.objects.filter(sub_ids__in=sub_ids,sem_ids__in=sem_ids).exclude(status='DELETE').values_list('ques_paper_id',flat=True)
    query_check=QuesPaperFormat.objects.filter(id__in=ques_paper_id).exclude(status='DELETE')
    if len(query_check)>0:
        query_check=QuesPaperApplicableOn.objects.filter(ques_paper_id__in=ques_paper_id).exclude(status='DELETE')
        if len(query_check)>1:
            return False
        else:
            return True
    else:
        return True


def Questionpaper_format(request):
    if checkpermission(request, [rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
        session_name = request.session['Session_name']
        session = request.session['Session_id']
        QuesPaperFormat = generate_session_table_name("QuesPaperFormat_", session_name)
        QuesPaperApplicableOn = generate_session_table_name("QuesPaperApplicableOn_", session_name)
        QuesPaperSectionDetails = generate_session_table_name("QuesPaperSectionDetails_", session_name)
        QuesPaperBTAttainment = generate_session_table_name("QuesPaperBTAttainment_", session_name)
        ExamSchedule = generate_session_table_name("ExamSchedule_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

        if (requestMethod.GET_REQUEST(request)):
            if (requestType.firstrequest(request.GET)):
                bt_level = get_btlevel(session)
                data = {'data1': bt_level}
            elif (requestType.custom_request_type(request.GET, 'attempt_type')):
                exam_name = new_exam_dropdown(session)
                attempt_type = get_attempt_type()

                data = {'data1': attempt_type, 'exam_name': exam_name}
                print(data)

            elif (requestType.custom_request_type(request.GET, 'view_previous')):
                ques_format_detail1 = QuesPaperApplicableOn.objects.exclude(ques_paper_id__status='DELETE').exclude(status='DELETE').annotate(sno=F('sem__dept__course'), value=F('sem__dept__course__value'), uid=F('sem__dept'), dept__value=F('sem__dept__dept__value'), sem_id=F('sem__sem_id'),subject_id_id=F('subject_id'),subject_name=F('subject_id__sub_name')).values('sem_id', 'uid', 'sno', 'sem__sem', 'dept__value', 'value','subject_id_id','subject_name', 'ques_paper_id', 'ques_paper_id__exam_id__value', 'ques_paper_id__exam_id','status')
                #ques_format_detail1 = QuesPaperApplicableOn.objects.exclude(ques_paper_id__status='DELETE').annotate(sno=F('sem__dept__course'), value=F('sem__dept__course__value'), uid=F('sem__dept'), dept__value=F('sem__dept__dept__value'), sem_id=F('sem__sem_id')).values('sem_id', 'uid', 'sno', 'sem__sem', 'dept__value', 'value', 'ques_paper_id', 'ques_paper_id__exam_id__value', 'ques_paper_id__exam_id')
                print(ques_format_detail1)
                k = 0
                for i in ques_format_detail1:
                    print(i)
                    ques_format_detail1[k]['sem'] = ques_format_detail1[k]['sem__sem']
                    k += 1
                data = {'details': list(ques_format_detail1), 'exam_name': get_exam_name(session)}

            elif (requestType.custom_request_type(request.GET, 'view')):
                id = request.GET['id']
                view_format_detail = QuesPaperFormat.objects.filter(id=id).exclude(status='DELETE').values('time', 'exam_id__value')
                view_section_detail = QuesPaperSectionDetails.objects.filter(ques_paper_id=id).values('name', 'attempt_type', 'max_marks','min_marks_per')
                for section in view_section_detail:
                    if section['attempt_type'] == 'M':
                        section['value'] = 'Mandatory'
                    elif section['attempt_type'] == 'I':
                        section['value'] = 'Internal Choice'
                    elif section['attempt_type'] == 'O':
                        section['value'] = 'Overall Choice'

                view_bt_level_detail = QuesPaperBTAttainment.objects.filter(ques_paper_id=id).values('minimum', 'maximum', 'bt_level__value', 'bt_level__sno')
                x = len(view_bt_level_detail)
                for i in range(x):
                    view_bt_level_detail[i]['bt_level_abbr'] = "BL-" + str(i + 1)

                data = {'format': list(view_format_detail), 'section': list(view_section_detail), 'bt_level': list(view_bt_level_detail), 'attempt_type': get_attempt_type()}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif (requestMethod.POST_REQUEST(request)):
            emp_id = request.session['hash1']
            q2 = []
            sub_ids=[]
            sem_ids=[]
            data = json.loads(request.body)

            qry_sections = list(Sections.objects.values_list('section_id', flat=True))

            if check_islocked('DMS', qry_sections, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

            a = 0
            subject_id=data['subject_id']
            sem_id_sub_id = SubjectInfo.objects.filter(id__in=data['subject_id']).values('sem_id','id')
            print(sem_id_sub_id,'sem_id&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
            for i in range(len(sem_id_sub_id)):
                sem_ids.append(sem_id_sub_id[i]['sem_id'])
            for i in range(len(sem_id_sub_id)):
                sub_ids.append(sem_id_sub_id[i]['id'])
            # schedule_defined=list(ExamSchedule.objects.exclude(status='DELETE').filter(sem__in=sem_id,exam_id__in=data['exam_name']).values('id','exam_id__value','sem__sem'))

            # if schedule_defined:
            #   # data=statusMessages.CUSTOM_MESSAGE(schedule_defined[0]['exam_id__value'] + 'Exam Schedule Has Been Defined for sem'+ schedule_defined[0]['sem__sem']+ '. Question Paper Format Cannot be Changed Now')
            #   data=statusMessages.CUSTOM_MESSAGE('Exam Schedule has already been defined for this sem.Format Cannot be changed')
            #   return functions.RESPONSE(data,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
            q = QuesPaperApplicableOn.objects.filter(subject_id__in=sub_ids,sem__in=sem_ids, ques_paper_id__exam_id__in=data['exam_name'], ques_paper_id__status="INSERT").exclude(status='DELETE').values_list('ques_paper_id', flat=True)
         ###################################################################new added for -ve marking#######################
            if check_for_previuos_paper(session_name,q):

                data = {'msg':'Cannot update this as question paper already created for the defined format'}
                return functions.RESPONSE(data, statusCodes.STATUS_WARNING)

            if check_for_previous_format(session_name,q):
                QuesPaperFormat.objects.filter(id__in=list(q)).update(status="DELETE")
            else:
                QuesPaperApplicableOn.objects.filter(subject_id__in=sub_ids,sem_id__in=sem_ids).update(status='DELETE')
        ##################################################################################################################

            
            for q in data['exam_name']:
                q1 = QuesPaperFormat.objects.create(exam_id=(StudentAcademicsDropdown.objects.get(sno=data['exam_name'][a])), added_by=(EmployeePrimdetail.objects.get(emp_id=emp_id)), time=data['time'])
                a += 1
                q2.extend([q1.id])
            j = 0
            x = len(data['section']['sections'])
            qry1 = (QuesPaperSectionDetails(ques_paper_id=(QuesPaperFormat.objects.get(id=d)), name=data['section']['sections'][i]['section_name'], attempt_type=data['section']['sections'][i]['attempt'], max_marks=data['section']['sections'][i]['max_marks'] , min_marks_per=data['section']['sections'][i]['min_marks_per']) for d in q2 for i in range(x))
            qry2 = QuesPaperSectionDetails.objects.bulk_create(qry1)

            #sem_id = StudentSemester.objects.filter(dept__in=data['dept'], sem__in=data['sem']).values_list('sem_id', flat=True)
            qry1 = (QuesPaperApplicableOn(ques_paper_id=(QuesPaperFormat.objects.get(id=d)), sem=StudentSemester.objects.get(sem_id=sem_ids[i]),subject_id=SubjectInfo.objects.get(id=sub_ids[i])) for d in q2 for i in range(len(sem_ids)))
            qry2 = QuesPaperApplicableOn.objects.bulk_create(qry1)
            y = len(data['range_slider'])
            qry1 = (QuesPaperBTAttainment(ques_paper_id=(QuesPaperFormat.objects.get(id=d)), bt_level=(StudentAcademicsDropdown.objects.get(sno=data['range_slider'][j][0])), minimum=data['range_slider'][j][1], maximum=data['range_slider'][j][2]) for d in q2 for j in range(y))
            qry2 = QuesPaperBTAttainment.objects.bulk_create(qry1)

            data = statusMessages.MESSAGE_INSERT
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)

def check_for_previuos_paper(session_name,ques_paper_id):
    QuesPaperSectionDetails = generate_session_table_name("QuesPaperSectionDetails_", session_name)
    QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_", session_name)

    section_id = QuesPaperSectionDetails.objects.exclude(ques_paper_id__status='DELETE').filter(ques_paper_id__in=ques_paper_id).values_list('id',flat=True)
    qry = list(QuestionPaperQuestions.objects.exclude(status="DELETE").filter(section_id__in=section_id).values())
    if len(qry)>0:
        return True
    else:
        return False


def InternalExamSchedule(request):
    if checkpermission(request, [rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
        session_name = request.session['Session_name']
        ExamSchedule = generate_session_table_name("ExamSchedule_", session_name)
        if (requestMethod.POST_REQUEST(request)):
            emp_id = request.session['hash1']
            data = json.loads(request.body)

            qry_sections = list(Sections.objects.values_list('section_id', flat=True))

            if check_islocked('DMS', qry_sections, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

            to_date = datetime.strptime(str(data['to_date']).split('T')[0], "%Y-%m-%d").date()
            from_date = datetime.strptime(str(data['from_date']).split('T')[0], "%Y-%m-%d").date()

            sem_id = StudentSemester.objects.filter(dept__in=data['dept'], sem__in=data['sem']).values_list('sem_id', flat=True)
            id = ExamSchedule.objects.filter(exam_id=data['exam_name'], sem__in=sem_id, status="INSERT").values_list('id', flat=True)
            ExamSchedule.objects.filter(id__in=list(id)).update(status="DELETE")

            sem_id = StudentSemester.objects.filter(dept__in=data['dept'], sem__in=data['sem']).values_list('sem_id', flat=True)
            qry1 = (ExamSchedule(from_date=from_date, to_date=to_date, added_by=(EmployeePrimdetail.objects.get(emp_id=emp_id)), exam_id=(StudentAcademicsDropdown.objects.get(sno=data['exam_name'])), sem=StudentSemester.objects.get(sem_id=d1), detained_attendance=data['detained_attendance'], subject_type=StudentDropdown.objects.get(sno=sub)) for d1 in sem_id for sub in data['subject_type'])
            qry2 = ExamSchedule.objects.bulk_create(qry1)

            data = statusMessages.MESSAGE_INSERT
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif (requestMethod.GET_REQUEST(request)):
            if (requestType.firstrequest(request.GET)):
                sem_type = request.session['sem_type']
                sem_date = Semtiming.objects.filter(session_name=session_name, sem_type=sem_type).values('sem_start', 'sem_end')
                data = {'sem_date': list(sem_date)}

            elif (requestType.custom_request_type(request.GET, 'view_previous')):
                exam_schedule = ExamSchedule.objects.filter(status="INSERT").values('id', 'from_date', 'to_date', 'exam_id', 'exam_id__value', 'sem__sem', 'sem__dept', 'sem__dept__course', 'sem__dept__dept__value', 'sem__dept__course__value', 'detained_attendance', 'subject_type')

                data = {'details': list(exam_schedule)}
            elif (requestType.custom_request_type(request.GET, 'delete')):
                ExamSchedule.objects.filter(id=request.GET['id'], status="INSERT").update(status="DELETE")

                data = statusMessages.MESSAGE_DELETE
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def get_sub_type():
    query = StudentDropdown.objects.filter(field="SUBJECT TYPE").exclude(value__isnull=True).exclude(status="DELETE").values('value', 'sno')
    return list(query)


def Attendance_Marks(request):
    if checkpermission(request, [rolesCheck.ROLE_DEAN , rolesCheck.ROLE_STUDENT_REPORT]) == statusCodes.STATUS_SUCCESS:
        session_name = request.session['Session_name']
        session = request.session['Session_id']
        emp_id = request.session['hash1']
        AttMarksRule = generate_session_table_name("AttMarksRule_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

        if (requestMethod.POST_REQUEST(request)):
            data = json.loads(request.body)
            max_att_marks = data['max_att_marks']
            qry_sections = list(Sections.objects.values_list('section_id', flat=True))

            if check_islocked('DMS', qry_sections, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

            x = len(data['format']['att'])
            i = 0
            sem_id = StudentSemester.objects.filter(dept__in=data['dept'], sem__in=data['sem']).values_list('sem_id', flat=True)
            id = AttMarksRule.objects.filter(sem__in=list(sem_id), subject_type__in=data['sub_type'], max_att_marks=max_att_marks).exclude(status="DELETE").values_list('id', flat=True)
            if(id):
                qry = AttMarksRule.objects.filter(id__in=list(id)).update(status="DELETE")
            for d2 in data['sub_type']:
                qry1 = (AttMarksRule(from_att_per=data['format']['att'][i]['slider1']['min_value'], to_att_per=data['format']['att'][i]['slider1']['max_value'], marks=data['format']['att'][i]['marks'], sem=StudentSemester.objects.get(sem_id=d1), subject_type=StudentDropdown.objects.get(sno=d2), max_att_marks=max_att_marks) for d1 in sem_id for i in range(x))
                qry2 = AttMarksRule.objects.bulk_create(qry1)

            data = statusMessages.MESSAGE_INSERT
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif (requestMethod.GET_REQUEST(request)):
            data = []
            if (requestType.custom_request_type(request.GET, 'view_previous')):
                sem_id = AttMarksRule.objects.exclude(status="DELETE").values_list('sem', flat=True).distinct()
                for s in sem_id:
                    qry2 = AttMarksRule.objects.filter(sem=s).exclude(status="DELETE").values('subject_type', 'max_att_marks').distinct()
                    for sub in qry2:
                        qry = list(AttMarksRule.objects.filter(sem=s, subject_type=sub['subject_type'], max_att_marks=sub['max_att_marks']).exclude(status="DELETE").values('sem__sem', 'sem__dept', 'sem__dept__course', 'sem__dept__dept__value', 'sem__dept__course__value', 'max_att_marks').distinct())
                        qry1 = list(AttMarksRule.objects.filter(sem=s, subject_type=sub['subject_type'], max_att_marks=sub['max_att_marks']).exclude(status="DELETE").values('from_att_per', 'to_att_per', 'id', 'marks', 'subject_type', 'subject_type__value').distinct())
                        data.append({"data": qry1, "data2": qry})
                # data_values={"data":data}

            elif (requestType.custom_request_type(request.GET, 'delete')):
                qry_sections = list(Sections.objects.values_list('section_id', flat=True))

                if check_islocked('DMS', qry_sections, session_name):
                    return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

                rule_id = request.GET['id'].split(',')
                AttMarksRule.objects.filter(id__in=rule_id).exclude(status="DELETE").update(status="DELETE")

                data = statusMessages.MESSAGE_DELETE

            elif (requestType.custom_request_type(request.GET, 'max_att_marks')):
                sem_li = request.GET['sem'].split(",")
                subject_type_li = request.GET['sub_type'].split(",")

                dept_li = request.GET['dept'].split(",")

                sem_id = StudentSemester.objects.filter(sem__in=sem_li, dept__in=dept_li).values_list('sem_id', flat=True)
                att_marks = list(SubjectInfo.objects.filter(subject_type__in=subject_type_li, sem_id__in=sem_id, max_att_marks__gt=0).exclude(status='DELETE').values_list('max_att_marks', flat=True).distinct().order_by('max_att_marks'))

                print(att_marks)
                data = {'data': att_marks}
                # data=statusMessages.MESSAGE_DELETE

            elif (requestType.custom_request_type(request.GET, 'sub_type')):
                data = {'sub_type': get_sub_type()}

            elif (requestType.custom_request_type(request.GET, 'max_marks')):
                dept = request.GET['dept'].split(",")
                sem = request.GET['sem'].split(",")
                subject_type = request.GET['sub_type'].split(",")
                sem_id = StudentSemester.objects.filter(dept__in=dept, sem__in=sem).values_list('sem_id', flat=True)
                qry = SubjectInfo.objects.filter(sem__in=list(sem_id), subject_type__in=subject_type, max_att_marks__gt=0).exclude(status="DELETE").values_list('max_att_marks', flat=True)
                max_marks = qry.aggregate(Min('max_att_marks'))
                data = {'data': max_marks}
            elif requestMethod.GET_REQUEST(request):
                if (requestType.firstrequest(request.GET)):
                    data = {"exam_name": get_exam_name(session)}

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
    else:
        if (requestMethod.GET_REQUEST(request)):
            if (requestType.custom_request_type(request.GET, 'sub_type')):
                data = {'sub_type': get_sub_type()}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


# def ExtraBonus_Marks(request):
#   if checkpermission(request, [rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
#       session_name = request.session['Session_name']
#       emp_id = request.session['hash1']
#       studentSession = generate_session_table_name("studentSession_", session_name)
#       SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
#       ExtraBonus = generate_session_table_name("ExtraBonus_", session_name)
#       if (requestMethod.GET_REQUEST(request)):
#           data = []
#           if (requestType.custom_request_type(request.GET, 'get_section_students')):
#               section = request.GET['section'].split(',')
#               subjects = request.GET['subjects'].split(',')
#               for sec in section:
#                   qry1 = list(studentSession.objects.filter(section=sec).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX"))).values_list('uniq_id', flat=True).order_by('class_roll_no'))
#                   for s in qry1:
#                       qry = list(studentSession.objects.filter(uniq_id=s).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX"))).values('uniq_id', 'uniq_id__name', 'section__sem_id__sem', 'section__sem_id', 'section__section', 'year', 'section__sem_id__dept__dept__value', 'class_roll_no', 'uniq_id__uni_roll_no', 'mob', 'registration_status', 'reg_form_status', 'reg_date_time', 'fee_status', 'att_start_date', 'uniq_id__dept_detail__dept__value', 'uniq_id__dept_detail__dept__value', 'uniq_id__lib_id', 'uniq_id__gender', 'uniq_id__gender__value', 'session__sem_start', 'section').order_by('class_roll_no'))
#                       qry.append({"bonus_marks": None, "subject_id": None})
#                       q_marks = list(ExtraBonus.objects.filter(uniq_id=qry[0]['uniq_id']).exclude(status='DELETE').values('bonus_marks', 'subject_id'))
#                       array1 = []
#                       array2 = []
#                       if q_marks:
#                           j = 0
#                           for i in range(0, len(q_marks)):
#                               array1.append(q_marks[i]['bonus_marks'])
#                               array2.append(q_marks[i]['subject_id'])
#                               j = j + 1
#                           qry[1]['bonus_marks'] = array1
#                           qry[1]['subject_id'] = array2
#                       q_fname = StudentPerDetail.objects.filter(uniq_id=qry[0]['uniq_id']).values('fname')
#                       q_fmob = StudentFamilyDetails.objects.filter(uniq_id=qry[0]['uniq_id']).values('father_mob')
#                       if len(q_fname) > 0:
#                           qry[0]['fname'] = q_fname[0]['fname']
#                       else:
#                           qry[0]['fname'] = "---"
#                       if len(q_fmob) > 0:
#                           qry[0]['father_mob'] = q_fmob[0]['father_mob']
#                       else:
#                           qry[0]['fname'] = "---"

#                       ########## INTERNAL MARKS ##########
#                       qry.append({})

#                       subject_details = list(SubjectInfo.objects.exclude(status="DELETE").filter(id__in=subjects).values('max_ct_marks', 'max_ta_marks', 'sub_name', 'sub_alpha_code', 'sub_num_code', 'id', 'max_att_marks', 'subject_type', 'sem').annotate(ids=F('id')))
#                       temp_data = single_student_ct_marks(session_name, qry[0]['uniq_id'], subject_details, {})
#                       qry[2]['internal_marks'] = temp_data
#                       data.append(list(qry))
#           return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

#       if (requestMethod.POST_REQUEST(request)):
#           data = json.loads(request.body)
#           i = 0
#           qry_sections = list(Sections.objects.values_list('section_id', flat=True))

#           if check_islocked('DMS', qry_sections, session_name):
#               return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
#           for c in range(0, len(data['x'])):
#               t = 0
#               for d in data['x'][i]['marks']:
#                   qry = ExtraBonus.objects.filter(uniq_id=data['x'][i]['uniq_id'], subject_id=data['x'][i]['marks'][t]['subject_id']).exclude(status='DELETE').values_list('id', flat=True)
#                   if qry:
#                       ExtraBonus.objects.filter(id__in=list(qry)).exclude(status='DELETE').update(status='DELETE')
#                   t = t + 1
#               i = i + 1

#           j = 0
#           for c in range(0, len(data['x'])):
#               t = 0
#               for d in data['x'][j]['marks']:
#                   if data['x'][j]['marks'][t]['marks'] == None:
#                       t = t + 1
#                   else:
#                       qry_marks = ExtraBonus.objects.create(uniq_id=studentSession.objects.get(uniq_id=data['x'][j]['uniq_id']), subject_id=SubjectInfo.objects.get(id=data['x'][j]['marks'][t]['subject_id']), bonus_marks=data['x'][j]['marks'][t]['marks'], added_by=EmployeePrimdetail.objects.get(emp_id=emp_id))
#                       t = t + 1
#               j = j + 1
#           data = statusMessages.MESSAGE_INSERT
#           return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
#   else:
#       return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)

def ExtraBonus_Marks(request):
    if checkpermission(request, [rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
        session_name = request.session['Session_name']
        emp_id = request.session['hash1']
        studentSession = generate_session_table_name("studentSession_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
        ExtraBonus = generate_session_table_name("ExtraBonus_", session_name)
        if (requestMethod.GET_REQUEST(request)):
            data = []
            if (requestType.custom_request_type(request.GET, 'get_section_students')):
                section = request.GET['section'].split(',')
                subjects = request.GET['subjects'].split(',')
                if 'sem_id' in request.GET:
                    sem_id = request.GET['sem_id']
                else:
                    sem_id = None
                    sem = list(Sections.objects.filter(section_id__in=section).exclude(status="DELETE").values_list('sem_id', flat=True).distinct())
                    if len(sem) == 1:
                        sem_id = sem[0]

                session_num = int(session_name[:2])

                ### BONUS CHANGE ###
                get_all_students = list(studentSession.objects.filter(section__in=section).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX"))).values('uniq_id').order_by('class_roll_no'))
                subjects_data = list(SubjectInfo.objects.filter(id__in=subjects).exclude(status="DELETE").values('id', 'sub_name', 'sub_alpha_code', 'sub_num_code', 'max_ct_marks', 'max_att_marks', 'max_ta_marks', 'subject_type', 'subject_type__value'))
                bonus_data = fetch_bonus_marks(get_all_students, subjects_data, sem_id, session_name)
                ####################
                for sec in section:
                    qry1 = list(studentSession.objects.filter(section=sec).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX"))).values_list('uniq_id', flat=True).order_by('class_roll_no'))

                    for s in qry1:
                        marks_obt = 0
                        qry = list(studentSession.objects.filter(uniq_id=s).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX"))).values('uniq_id', 'uniq_id__name', 'section__sem_id__sem', 'section__sem_id', 'section__section', 'year', 'section__sem_id__dept__dept__value', 'class_roll_no', 'uniq_id__uni_roll_no', 'mob', 'registration_status', 'reg_form_status', 'reg_date_time', 'fee_status', 'att_start_date', 'uniq_id__dept_detail__dept__value', 'uniq_id__dept_detail__dept__value', 'uniq_id__lib_id', 'uniq_id__gender', 'uniq_id__gender__value', 'session__sem_start', 'section').order_by('class_roll_no'))
                        qry.append({"bonus_marks": None, "subject_id": None})
                        q_marks = list(ExtraBonus.objects.filter(uniq_id=qry[0]['uniq_id']).exclude(status='DELETE').values('bonus_marks', 'subject_id'))
                        array1 = []
                        array2 = []
                        if q_marks:
                            j = 0
                            for i in range(0, len(q_marks)):
                                array1.append(q_marks[i]['bonus_marks'])
                                array2.append(q_marks[i]['subject_id'])
                                j = j + 1
                            qry[1]['bonus_marks'] = array1
                            qry[1]['subject_id'] = array2
                        q_fname = StudentPerDetail.objects.filter(uniq_id=qry[0]['uniq_id']).values('fname')
                        q_fmob = StudentFamilyDetails.objects.filter(uniq_id=qry[0]['uniq_id']).values('father_mob')
                        if len(q_fname) > 0:
                            qry[0]['fname'] = q_fname[0]['fname']
                        else:
                            qry[0]['fname'] = "---"
                        if len(q_fmob) > 0:
                            qry[0]['father_mob'] = q_fmob[0]['father_mob']
                        else:
                            qry[0]['fname'] = "---"

                        ########## INTERNAL MARKS ##########
                        qry.append({})

                        subject_details = list(SubjectInfo.objects.exclude(status="DELETE").filter(id__in=subjects).values('max_ct_marks', 'max_ta_marks', 'sub_name', 'sub_alpha_code', 'sub_num_code', 'id', 'max_att_marks', 'subject_type', 'sem').annotate(ids=F('id')))
                        if session_num < 19:
                            temp_data = single_student_ct_marks(session_name, qry[0]['uniq_id'], subject_details, {})
                        else:
                            internal_marks = get_single_student_internal_marks(s, sem_id, subjects_data, session_name)
                            for int_marks in internal_marks['data']:
                                bonus_marks = 0
                                if s in bonus_data:
                                    if int_marks['subject_id'] in bonus_data[s]:
                                        for bonus in bonus_data[s][int_marks['subject_id']]['rule_data']:
                                            bonus_marks += float(bonus)
                                        marks_obt = float(int_marks['marks_obtained']) + float(bonus_marks)
                                        int_marks['marks_obtained'] = min(marks_obt, float(int_marks['total_marks']))
                            ### FOR BONUS MARKS ###
                            # if s in bonus_data:
                            #     for sub in subjects_data:
                            #         bonus_marks = 0
                            #         if sub['id'] in bonus_data[s]:
                            #             for bonus in bonus_data[s][sub['id']]['rule_data']:
                            #                 bonus_marks += float(bonus)
                            # #######################
                            #             marks_obt = float(internal_marks['data'][0]['marks_obtained']) + float(bonus_marks)
                            #             internal_marks['data'][0]['marks_obtained'] = min(marks_obt, float(internal_marks['data']['total_marks']))
                            # temp_data = {'data': internal_marks['data'], 'avg_marks_obt': marks_obt, 'avg_total_marks': internal_marks['avg_total_marks']}
                            temp_data = internal_marks
                        qry[2]['internal_marks'] = temp_data
                        data.append(list(qry))
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        if (requestMethod.POST_REQUEST(request)):
            data = json.loads(request.body)
            i = 0
            qry_sections = list(Sections.objects.values_list('section_id', flat=True))

            if check_islocked('DMS', qry_sections, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
            for c in range(0, len(data['x'])):
                t = 0
                for d in data['x'][i]['marks']:
                    qry = ExtraBonus.objects.filter(uniq_id=data['x'][i]['uniq_id'], subject_id=data['x'][i]['marks'][t]['subject_id']).exclude(status='DELETE').values_list('id', flat=True)
                    if qry:
                        ExtraBonus.objects.filter(id__in=list(qry)).exclude(status='DELETE').update(status='DELETE')
                    t = t + 1
                i = i + 1

            j = 0
            for c in range(0, len(data['x'])):
                t = 0
                for d in data['x'][j]['marks']:
                    if data['x'][j]['marks'][t]['marks'] == None:
                        t = t + 1
                    else:
                        qry_marks = ExtraBonus.objects.create(uniq_id=studentSession.objects.get(uniq_id=data['x'][j]['uniq_id']), subject_id=SubjectInfo.objects.get(id=data['x'][j]['marks'][t]['subject_id']), bonus_marks=data['x'][j]['marks'][t]['marks'], added_by=EmployeePrimdetail.objects.get(emp_id=emp_id))
                        t = t + 1
                j = j + 1
            data = statusMessages.MESSAGE_INSERT
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Bonus_Marks_AddSubRule_Updated(request):
    emp_id = request.session['hash1']
    data = {}
    if checkpermission(request, [rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
        session_name = request.session['Session_name']
        session = request.session['Session_id']

        BonusMarks_External = generate_session_table_name("BonusMarks_External_", session_name)
        BonusMarks_Internal = generate_session_table_name("BonusMarks_Internal_", session_name)
        BonusMarks_InternalExam = generate_session_table_name("BonusMarks_InternalExam_", session_name)
        BonusMarks_Attendance = generate_session_table_name("BonusMarks_Attendance_", session_name)
        BonusMarks_AttendanceAtt_type = generate_session_table_name("BonusMarks_AttendanceAtt_type_", session_name)
        BonusMarks_Subrule = generate_session_table_name("BonusMarks_Subrule_", session_name)

        if (requestMethod.GET_REQUEST(request)):
            if (requestType.firstrequest(request.GET)):
                exam_name = get_exam_name(session)
                att_type = get_attendance_type(session)
                data = {'exam_name': exam_name, 'att_type': att_type}

            elif (requestType.custom_request_type(request.GET, 'view_previous')):
                data = []
                qry = list(BonusMarks_Subrule.objects.exclude(status="DELETE").values('id', 'name', 'type', 'type_id', 'added_by', 'added_by__name', 'timestamp'))
                for q in qry:
                    q['insertion_date'] = str(q['timestamp']).split(' ')[0]
                    # print(q['date'], 'date')
                    if 'EXTERNAL' in q['type']:
                        external_data = list(BonusMarks_External.objects.filter(id=q['type_id']).exclude(status="DELETE").values('applicable_type', 'criteria', 'range_type', 'value'))
                        if len(external_data) > 0:
                            for k, v in external_data[0].items():
                                q[k] = v

                    elif 'INTERNAL' in q['type']:
                        internal_data = BonusMarks_InternalExam.objects.filter(internal_id=q['type_id']).exclude(internal_id__status="DELETE").values('exam_id', 'exam_id__value', 'internal_id', 'internal_id__min_range', 'internal_id__max_range')
                        exam_id = []
                        if len(internal_data) > 0:
                            q['internal_id__min_range'] = internal_data[0]['internal_id__min_range']
                            q['internal_id__max_range'] = internal_data[0]['internal_id__max_range']
                            for int_data in internal_data:
                                exam_id.append(int_data['exam_id__value'])
                            q['exam_id'] = exam_id

                    elif 'ATTENDANCE' in q['type']:
                        att_data = BonusMarks_AttendanceAtt_type.objects.filter(att_id=q['type_id']).exclude(att_id__status="DELETE").values('att_id', 'att_type__value', 'att_type', 'att_id__min_range', 'att_id__max_range')
                        att_id = []
                        if len(att_data) > 0:
                            q['att_id__min_range'] = att_data[0]['att_id__min_range']
                            q['att_id__max_range'] = att_data[0]['att_id__max_range']
                            for att in att_data:
                                att_id.append(att['att_type__value'])
                            q['att_id'] = att_id

                    data.append(q)

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif (requestMethod.POST_REQUEST(request)):
            received_data = json.loads(request.body)
            data1 = []
            added_by = EmployeePrimdetail.objects.get(emp_id=emp_id)
            get_name = list(BonusMarks_Subrule.objects.exclude(status="DELETE").values_list('name', flat=True))
            for data in received_data:
                subrule_type = data['type']
                name = data['name']

                #### CHECK FOR NAME ####
                if name in get_name:
                    return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Criteria name can be unique.'), statusCodes.STATUS_CONFLICT)

                ########################

                if 'EXTERNAL' in str(subrule_type):
                    applicable_type = data['applicable_type']
                    criteria = data['criteria']
                    value = data['value']
                    range_type = data['range_type']

                    qry = BonusMarks_External.objects.create(applicable_type=applicable_type, criteria=criteria, range_type=range_type, value=value)
                    data1.append({"type": subrule_type, "type_id": qry.id, "name": name, "added_by": added_by})

                elif 'INTERNAL' in str(subrule_type):
                    exam_id = data['exam_name']
                    int_min = data['int_min']
                    int_max = data['int_max']

                    qry = BonusMarks_Internal.objects.create(min_range=int_min, max_range=int_max)
                    objs = (BonusMarks_InternalExam(internal_id=BonusMarks_Internal.objects.get(id=qry.id), exam_id=StudentAcademicsDropdown.objects.get(sno=exam))for exam in exam_id)
                    query = BonusMarks_InternalExam.objects.bulk_create(objs)
                    data1.append({"type": subrule_type, "type_id": qry.id, "name": name, "added_by": added_by})

                elif 'ATTENDANCE' in str(subrule_type):
                    att_type = data['att_type']
                    att_min = data['att_min']
                    att_max = data['att_max']

                    qry = BonusMarks_Attendance.objects.create(min_range=att_min, max_range=att_max)
                    objs = (BonusMarks_AttendanceAtt_type(att_id=BonusMarks_Attendance.objects.get(id=qry.id), att_type=StudentAcademicsDropdown.objects.get(sno=att))for att in att_type)
                    query = BonusMarks_AttendanceAtt_type.objects.bulk_create(objs)
                    data1.append({"type": subrule_type, "type_id": qry.id, "name": name, "added_by": added_by})

            final_qry = (BonusMarks_Subrule(name=d['name'], type=d['type'], type_id=d['type_id'], added_by=d['added_by'])for d in data1)
            final_query = BonusMarks_Subrule.objects.bulk_create(final_qry)
            data = statusMessages.MESSAGE_INSERT
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif (requestMethod.DELETE_REQUEST(request)):
            received_data = json.loads(request.body)
            del_id = received_data['del_id']
            BonusMarks_Subrule.objects.filter(id__in=del_id).update(status="DELETE")
            data = statusMessages.MESSAGE_DELETE
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


# def Bonus_Marks_AddRule_Updated(request):
#     emp_id = request.session['hash1']
#     data = {}
#     if checkpermission(request, [rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
#         session_name = request.session['Session_name']
#         session = request.session['Session_id']

#         BonusMarks_External = generate_session_table_name("BonusMarks_External_", session_name)
#         BonusMarks_Internal = generate_session_table_name("BonusMarks_Internal_", session_name)
#         BonusMarks_InternalExam = generate_session_table_name("BonusMarks_InternalExam_", session_name)
#         BonusMarks_Attendance = generate_session_table_name("BonusMarks_Attendance_", session_name)
#         BonusMarks_AttendanceAtt_type = generate_session_table_name("BonusMarks_AttendanceAtt_type_", session_name)
#         BonusMarks_Subrule = generate_session_table_name("BonusMarks_Subrule_", session_name)
#         BonusMarks_Applicable_On = generate_session_table_name("BonusMarks_Applicable_On_", session_name)
#         BonusMarks_Rule = generate_session_table_name("BonusMarks_Rule_", session_name)
#         BonusMarks_Students = generate_session_table_name("BonusMarks_Students_", session_name)
#         BonusMarks = generate_session_table_name('BonusMarks_', session_name)
#         SubjectInfo = generate_session_table_name('SubjectInfo_', session_name)
#         studentSession = generate_session_table_name('studentSession_', session_name)

#         if (requestMethod.GET_REQUEST(request)):
#             if (requestType.custom_request_type(request.GET, 'subject_multi')):
#                 sem = request.GET['sem'].split(',')
#                 dept = request.GET['branch'].split(',')
#                 sub_type = request.GET['sub_type'].split(',')
#                 data = get_subject_multi_type(dept, sem, sub_type, session_name)

#             elif (requestType.custom_request_type(request.GET, 'get_students_multi')):
#                 data = []
#                 section_ids = list(Sections.objects.filter(dept__in=request.GET['branch'].split(','), section__in=request.GET['section'].split(','), sem_id__sem__in=request.GET['sem'].split(',')).values_list('section_id', flat=True))
#                 query = get_section_students(section_ids, {}, session_name)
#                 for q in query:
#                     data.extend(q)

#             elif (requestType.custom_request_type(request.GET, 'view_previous')):
#                 sort_by_again = ['rule_no', 'subrule_no']
#                 temp_data = BonusMarks_Rule.objects.filter().exclude(status="DELETE").values('id', 'rule_no', 'subrule_no', 'subrule_id__name', 'bonus_marks', 'max_marks_limit', 'min_range', 'max_range', 'app_id').order_by('rule_no', 'subrule_no').distinct()
#                 # print(temp_data, 'temp_datavvvvvvvvvvv')
#                 extra_filter = {'key1': 'subrule_no'}
#                 data = []
#                 for rule_no, (rule, rule_data) in enumerate(groupby(temp_data, key=lambda rule: rule['rule_no'])):
#                     data.append({})
#                     data[-1]['rule_no'] = rule
#                     temp_rule_data = list(rule_data)

#                     temp_key = sort_by_again[1]
#                     data[-1]['rule_no_set'] = create_order_chooser(temp_key)(temp_rule_data, sort_by_again[1:])
#                     app_data = BonusMarks_Rule.objects.filter(rule_no=rule).exclude(status="DELETE").values('app_id').distinct()
#                     data[-1]['course'] = set()
#                     data[-1]['branch'] = set()
#                     data[-1]['sem'] = set()
#                     data[-1]['section'] = set()
#                     data[-1]['sub_type'] = set()
#                     data[-1]['subject'] = set()
#                     data[-1]['student'] = set()
#                     for app in app_data:
#                         app_id_data = BonusMarks_Applicable_On.objects.filter(id=app['app_id']).exclude(status="DELETE").values('sem_id__sem', 'section__dept__course__value', 'section__dept__dept__value', 'section__section', 'subject__sub_name', 'subject__subject_type__value', 'subject__sub_alpha_code', 'subject__sub_num_code')
#                         if len(app_id_data) > 0:
#                             data[-1]['course'].add(app_id_data[0]['section__dept__course__value'])
#                             data[-1]['branch'].add(app_id_data[0]['section__dept__dept__value'])
#                             data[-1]['sem'].add(app_id_data[0]['sem_id__sem'])
#                             data[-1]['section'].add(app_id_data[0]['section__section'])
#                             data[-1]['sub_type'].add(app_id_data[0]['subject__subject_type__value'])
#                             subject = str(str(app_id_data[0]['subject__sub_name']) + ' (' + str(app_id_data[0]['subject__sub_alpha_code']) + '-' + str(app_id_data[0]['subject__sub_num_code']) + ')')
#                             data[-1]['subject'].add(subject)

#                     print(temp_rule_data, 'temp_rule_data')
#                     for rule_id in temp_rule_data:
#                         get_student = BonusMarks_Students.objects.filter(rule_id=rule_id['id']).exclude(status="DELETE").exclude(rule_id__status="DELETE").values('uniq_id__uniq_id__name', 'uniq_id__uniq_id__uni_roll_no')
#                         name = 'N/A'
#                         for stu in get_student:
#                             name = str(str(stu['uniq_id__uniq_id__name']) + ' (' + str(stu['uniq_id__uniq_id__uni_roll_no']) + ')')
#                             data[-1]['student'].add(name)
#                     data[-1]['course'] = list(data[-1]['course'])
#                     data[-1]['branch'] = list(data[-1]['branch'])
#                     data[-1]['sem'] = list(data[-1]['sem'])
#                     data[-1]['section'] = list(data[-1]['section'])
#                     data[-1]['sub_type'] = list(data[-1]['sub_type'])
#                     data[-1]['subject'] = list(data[-1]['subject'])
#                     data[-1]['student'] = list(data[-1]['student'])

#             return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

#         elif (requestMethod.POST_REQUEST(request)):
#             data = json.loads(request.body)
#             print(data, 'data')
#             new_rule_ids = []
#             all_atudents = []
#             last_rule_no = BonusMarks_Rule.objects.exclude(status="DELETE").values_list('rule_no', flat=True).order_by('-rule_no').distinct()
#             rule_no = 1
#             if len(last_rule_no) > 0:
#                 rule_no = last_rule_no[0] + 1
#             for i, rule in enumerate(data):
#                 current_rule_id = []

#                 course = rule['course']
#                 dept = rule['branch']
#                 sem = rule['sem']
#                 section = rule['section']
#                 sub_type = rule['subject_type']
#                 subject = rule['subject']
#                 students = rule['student']

#                 applicable_data = []
#                 sem_ids = []
#                 subject_ids = []
#                 section_ids = []
#                 get_sem_id = list(Sections.objects.filter(section__in=section, sem_id__sem__in=sem, sem_id__dept__in=dept).exclude(status="DELETE").values('sem_id', 'section_id'))
#                 for sem_id in get_sem_id:
#                     sem_ids.append(sem_id['sem_id'])
#                     section_ids.append(sem_id['section_id'])
#                     if 'ALL' not in str(subject):
#                         get_subjects = list(SubjectInfo.objects.filter(sem=sem_id['sem_id'], session=session, id__in=subject, subject_type__in=sub_type).exclude(status="DELETE").values_list('id', flat=True))
#                         subject_id = list(set(subject) & set(get_subjects))
#                     else:
#                         get_subjects = list(SubjectInfo.objects.filter(sem=sem_id['sem_id'], session=session, subject_type__in=sub_type).exclude(status="DELETE").values_list('id', flat=True))
#                         subject_id = get_subjects
#                     for sub in subject_id:
#                         subject_ids.append(sub)

#                         ### CHECK IF SEM-SECTION-SUBJECT DETAILS ALREADY INSERTED ###
#                         qry_check = BonusMarks_Applicable_On.objects.filter(sem_id=sem_id['sem_id'], section=sem_id['section_id'], subject=sub).exclude(status="DELETE").values('id')
#                         #############################################################
#                         if len(qry_check) == 0:
#                             applicable_data.append({"sem_id": sem_id['sem_id'], "section": sem_id['section_id'], "subject": sub})
#                         else:
#                             continue
#                 ###
#                 app_qry = (BonusMarks_Applicable_On(sem_id=StudentSemester.objects.get(sem_id=app['sem_id']), section=Sections.objects.get(section_id=app['section']), subject=SubjectInfo.objects.get(id=app['subject']))for app in applicable_data)
#                 app_final = BonusMarks_Applicable_On.objects.bulk_create(app_qry)

#                 get_app_ids = list(BonusMarks_Applicable_On.objects.filter(sem_id__in=sem_ids, section__in=section_ids, subject__in=subject_ids).exclude(status="DELETE").values_list('id', flat=True))

#                 subrules = rule['subrules']

#                 for j, subrule in enumerate(subrules):
#                     for app in get_app_ids:
#                         for sub_id in subrule['criteria']:
#                             rule_id = BonusMarks_Rule.objects.create(rule_no=int(rule_no), app_id=BonusMarks_Applicable_On.objects.get(id=app), subrule_no=int(j + 1), subrule_id=BonusMarks_Subrule.objects.get(id=sub_id), bonus_marks=subrule['bonus_marks'], max_marks_limit=subrule['max_limit'], min_range=subrule['min_value'], max_range=subrule['max_value'], added_by=EmployeePrimdetail.objects.get(emp_id=emp_id))
#                             current_rule_id.append(rule_id.id)
#                             new_rule_ids.append(rule_id.id)

#                     student_data = []
#                     if 'ALL' not in str(students):
#                         all_atudents.extend(students)
#                         for uniq_id in students:
#                             for rule_id in current_rule_id:
#                                 student_data.append({"uniq_id": uniq_id, "rule_id": rule_id})
#                     else:
#                         students = studentSession.objects.filter(sem_id__sem__in=sem, sem_id__dept__in=dept, section__section__in=section).values_list('uniq_id', flat=True)
#                         all_atudents.extend(students)
#                         for uniq_id in students:
#                             for rule_id in current_rule_id:
#                                 student_data.append({'uniq_id': uniq_id, 'rule_id': rule_id})
#                     ##################
#                 stu_qry = (BonusMarks_Students(uniq_id=studentSession.objects.get(uniq_id=stu['uniq_id']), rule_id=BonusMarks_Rule.objects.get(id=stu['rule_id']))for stu in student_data)
#                 BonusMarks_Students.objects.bulk_create(stu_qry)

#                 rule_no = rule_no + 1

#             ########## CHECK FOR OLD DATA ############
#             get_old_rule_ids = BonusMarks_Students.objects.filter(uniq_id__in=all_atudents).exclude(rule_id__in=new_rule_ids).values_list('rule_id', flat=True).distinct()
#             delelte_old_rule = BonusMarks_Students.objects.filter(uniq_id__in=all_atudents).exclude(rule_id__in=new_rule_ids).update(status="DELETE")
#             delete_stored_marks_for_old_ids = BonusMarks.objects.filter(uniq_id__in=all_atudents).exclude(rule_id__in=new_rule_ids).update(status="DELETE")
#             #### CHECK IF ANY STUDENT IS THERE FOR OLD RULE ID ###
#             for rule_id in get_old_rule_ids:
#                 qry_check = BonusMarks_Students.objects.filter(rule_id__id=rule_id).exclude(status="DELETE").exclude(rule_id__status="DELETE").values('uniq_id', 'rule_id')
#                 if len(qry_check) == 0:
#                     BonusMarks_Rule.objects.filter(id=rule_id).update(status="DELETE")
#             ######################################################
#             ##########################################

#             data = statusMessages.MESSAGE_INSERT
#             return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

#         else:
#             return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

#     else:
#         return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
def Bonus_Marks_AddRule_Updated(request):
    emp_id = request.session['hash1']
    data = {}
    if checkpermission(request, [rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
        session_name = request.session['Session_name']
        session = request.session['Session_id']

        BonusMarks_External = generate_session_table_name("BonusMarks_External_", session_name)
        BonusMarks_Internal = generate_session_table_name("BonusMarks_Internal_", session_name)
        BonusMarks_InternalExam = generate_session_table_name("BonusMarks_InternalExam_", session_name)
        BonusMarks_Attendance = generate_session_table_name("BonusMarks_Attendance_", session_name)
        BonusMarks_AttendanceAtt_type = generate_session_table_name("BonusMarks_AttendanceAtt_type_", session_name)
        BonusMarks_Subrule = generate_session_table_name("BonusMarks_Subrule_", session_name)
        BonusMarks_Applicable_On = generate_session_table_name("BonusMarks_Applicable_On_", session_name)
        BonusMarks_Rule = generate_session_table_name("BonusMarks_Rule_", session_name)
        BonusMarks_Students = generate_session_table_name("BonusMarks_Students_", session_name)
        BonusMarks = generate_session_table_name('BonusMarks_', session_name)
        SubjectInfo = generate_session_table_name('SubjectInfo_', session_name)
        studentSession = generate_session_table_name('studentSession_', session_name)

        if (requestMethod.GET_REQUEST(request)):
            if (requestType.custom_request_type(request.GET, 'subject_multi')):
                sem = request.GET['sem'].split(',')
                dept = request.GET['branch'].split(',')
                sub_type = request.GET['sub_type'].split(',')
                data = get_subject_multi_type(dept, sem, sub_type, session_name)

            elif (requestType.custom_request_type(request.GET, 'get_students_multi')):
                data = []
                section_ids = list(Sections.objects.filter(dept__in=request.GET['branch'].split(','), section__in=request.GET['section'].split(','), sem_id__sem__in=request.GET['sem'].split(',')).values_list('section_id', flat=True))
                query = get_section_students(section_ids, {}, session_name)
                for q in query:
                    data.extend(q)

            elif (requestType.custom_request_type(request.GET, 'view_previous')):
                sort_by_again = ['rule_no', 'subrule_no']
                temp_data = BonusMarks_Rule.objects.filter().exclude(status="DELETE").values('id', 'rule_no', 'subrule_no', 'subrule_id__name', 'bonus_marks', 'max_marks_limit', 'min_range', 'max_range', 'app_id').order_by('rule_no', 'subrule_no').distinct()
                # print(temp_data, 'temp_datavvvvvvvvvvv')
                extra_filter = {'key1': 'subrule_no'}
                data = []
                for rule_no, (rule, rule_data) in enumerate(groupby(temp_data, key=lambda rule: rule['rule_no'])):
                    data.append({})
                    data[-1]['rule_no'] = rule
                    temp_rule_data = list(rule_data)

                    temp_key = sort_by_again[1]
                    data[-1]['rule_no_set'] = create_order_chooser(temp_key)(temp_rule_data, sort_by_again[1:])
                    app_data = BonusMarks_Rule.objects.filter(rule_no=rule).exclude(status="DELETE").values('app_id').distinct()
                    data[-1]['course'] = set()
                    data[-1]['branch'] = set()
                    data[-1]['sem'] = set()
                    data[-1]['section'] = set()
                    data[-1]['sub_type'] = set()
                    data[-1]['subject'] = set()
                    data[-1]['student'] = set()
                    for app in app_data:
                        app_id_data = BonusMarks_Applicable_On.objects.filter(id=app['app_id']).exclude(status="DELETE").values('sem_id__sem', 'section__dept__course__value', 'section__dept__dept__value', 'section__section', 'subject__sub_name', 'subject__subject_type__value', 'subject__sub_alpha_code', 'subject__sub_num_code')
                        if len(app_id_data) > 0:
                            data[-1]['course'].add(app_id_data[0]['section__dept__course__value'])
                            data[-1]['branch'].add(app_id_data[0]['section__dept__dept__value'])
                            data[-1]['sem'].add(app_id_data[0]['sem_id__sem'])
                            data[-1]['section'].add(app_id_data[0]['section__section'])
                            data[-1]['sub_type'].add(app_id_data[0]['subject__subject_type__value'])
                            subject = str(str(app_id_data[0]['subject__sub_name']) + ' (' + str(app_id_data[0]['subject__sub_alpha_code']) + '-' + str(app_id_data[0]['subject__sub_num_code']) + ')')
                            data[-1]['subject'].add(subject)

                    print(temp_rule_data, 'temp_rule_data')
                    for rule_id in temp_rule_data:
                        get_student = BonusMarks_Students.objects.filter(rule_id=rule_id['id']).exclude(status="DELETE").exclude(rule_id__status="DELETE").values('uniq_id__uniq_id__name', 'uniq_id__uniq_id__uni_roll_no')
                        name = 'N/A'
                        for stu in get_student:
                            name = str(str(stu['uniq_id__uniq_id__name']) + ' (' + str(stu['uniq_id__uniq_id__uni_roll_no']) + ')')
                            data[-1]['student'].add(name)
                    data[-1]['course'] = list(data[-1]['course'])
                    data[-1]['branch'] = list(data[-1]['branch'])
                    data[-1]['sem'] = list(data[-1]['sem'])
                    data[-1]['section'] = list(data[-1]['section'])
                    data[-1]['sub_type'] = list(data[-1]['sub_type'])
                    data[-1]['subject'] = list(data[-1]['subject'])
                    data[-1]['student'] = list(data[-1]['student'])

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif (requestMethod.POST_REQUEST(request)):
            data = json.loads(request.body)
            print(data, 'data')
            new_rule_ids = []
            all_atudents = []
            last_rule_no = BonusMarks_Rule.objects.exclude(status="DELETE").values_list('rule_no', flat=True).order_by('-rule_no').distinct()
            rule_no = 1
            if len(last_rule_no) > 0:
                rule_no = last_rule_no[0] + 1
            for i, rule in enumerate(data):
                current_rule_id = []

                course = rule['course']
                dept = rule['branch']
                sem = rule['sem']
                section = rule['section']
                sub_type = rule['subject_type']
                subject = rule['subject']
                students = rule['student']

                applicable_data = []
                sem_ids = []
                subject_ids = []
                section_ids = []
                get_sem_id = list(Sections.objects.filter(section__in=section, sem_id__sem__in=sem, sem_id__dept__in=dept).exclude(status="DELETE").values('sem_id', 'section_id'))
                print(get_sem_id, 'get_sem_id')
                for sem_id in get_sem_id:
                    sem_ids.append(sem_id['sem_id'])
                    section_ids.append(sem_id['section_id'])
                    if 'ALL' not in str(subject):
                        get_subjects = list(SubjectInfo.objects.filter(sem=sem_id['sem_id'], session=session, id__in=subject, subject_type__in=sub_type).exclude(status="DELETE").values_list('id', flat=True))
                        subject_id = list(set(subject) & set(get_subjects))
                        # subject_id = subject
                    else:
                        get_subjects = list(SubjectInfo.objects.filter(sem=sem_id['sem_id'], session=session, subject_type__in=sub_type).exclude(status="DELETE").values_list('id', flat=True))
                        subject_id = get_subjects
                    for sub in subject_id:
                        subject_ids.append(sub)

                        ### CHECK IF SEM-SECTION-SUBJECT DETAILS ALREADY INSERTED ###
                        qry_check = BonusMarks_Applicable_On.objects.filter(sem_id=sem_id['sem_id'], section=sem_id['section_id'], subject=sub).exclude(status="DELETE").values('id')
                        #############################################################
                        if len(qry_check) == 0:
                            applicable_data.append({"sem_id": sem_id['sem_id'], "section": sem_id['section_id'], "subject": sub})
                        else:
                            continue
                ###
                app_qry = (BonusMarks_Applicable_On(sem_id=StudentSemester.objects.get(sem_id=app['sem_id']), section=Sections.objects.get(section_id=app['section']), subject=SubjectInfo.objects.get(id=app['subject']))for app in applicable_data)
                app_final = BonusMarks_Applicable_On.objects.bulk_create(app_qry)

                get_app_ids = list(BonusMarks_Applicable_On.objects.filter(sem_id__in=sem_ids, section__in=section_ids, subject__in=subject_ids).exclude(status="DELETE").values_list('id', flat=True))

                subrules = rule['subrules']

                for j, subrule in enumerate(subrules):
                    for app in get_app_ids:
                        for sub_id in subrule['criteria']:
                            rule_id = BonusMarks_Rule.objects.create(rule_no=int(rule_no), app_id=BonusMarks_Applicable_On.objects.get(id=app), subrule_no=int(j + 1), subrule_id=BonusMarks_Subrule.objects.get(id=sub_id), bonus_marks=subrule['bonus_marks'], max_marks_limit=subrule['max_limit'], min_range=subrule['min_value'], max_range=subrule['max_value'], added_by=EmployeePrimdetail.objects.get(emp_id=emp_id))
                            current_rule_id.append(rule_id.id)
                            new_rule_ids.append(rule_id.id)

                    student_data = []
                    if 'ALL' not in str(students):
                        all_atudents.extend(students)
                        for uniq_id in students:
                            get_data = studentSession.objects.filter(uniq_id=uniq_id).values('sem_id', 'section_id')
                            print(uniq_id, get_data, 'kkkkkkkkk')
                            if len(get_data) > 0:
                                for rule_id in current_rule_id:
                                    ### check for sem and subject ###
                                    check = BonusMarks_Rule.objects.filter(id=rule_id, app_id__sem_id=get_data[0]['sem_id']).exclude(status="DELETE").values('id')
                                    if len(check) > 0:
                                        #################################
                                        student_data.append({"uniq_id": uniq_id, "rule_id": rule_id})
                    else:
                        students = studentSession.objects.filter(sem_id__sem__in=sem, sem_id__dept__in=dept, section__section__in=section).values_list('uniq_id', flat=True)
                        all_atudents.extend(students)
                        for uniq_id in students:
                            for rule_id in current_rule_id:
                                student_data.append({'uniq_id': uniq_id, 'rule_id': rule_id})
                    ##################
                stu_qry = (BonusMarks_Students(uniq_id=studentSession.objects.get(uniq_id=stu['uniq_id']), rule_id=BonusMarks_Rule.objects.get(id=stu['rule_id']))for stu in student_data)
                BonusMarks_Students.objects.bulk_create(stu_qry)

                rule_no = rule_no + 1

            ########## CHECK FOR OLD DATA ############
            get_old_rule_ids = BonusMarks_Students.objects.filter(uniq_id__in=all_atudents).exclude(rule_id__in=new_rule_ids).values_list('rule_id', flat=True).distinct()
            delelte_old_rule = BonusMarks_Students.objects.filter(uniq_id__in=all_atudents).exclude(rule_id__in=new_rule_ids).update(status="DELETE")
            delete_stored_marks_for_old_ids = BonusMarks.objects.filter(uniq_id__in=all_atudents).exclude(rule_id__in=new_rule_ids).update(status="DELETE")
            #### CHECK IF ANY STUDENT IS THERE FOR OLD RULE ID ###
            for rule_id in get_old_rule_ids:
                qry_check = BonusMarks_Students.objects.filter(rule_id__id=rule_id).exclude(status="DELETE").exclude(rule_id__status="DELETE").values('uniq_id', 'rule_id')
                if len(qry_check) == 0:
                    BonusMarks_Rule.objects.filter(id=rule_id).update(status="DELETE")
            ######################################################
            ##########################################

            data = statusMessages.MESSAGE_INSERT
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
