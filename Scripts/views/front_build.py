import os
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from StudentMMS.constants_functions import requestType
from erp.constants_variables import statusCodes, statusMessages, rolesCheck

def function_for_build(request):
    if requestMethod.GET_REQUEST(request):
        if(requestType.custom_request_type(request.GET, 'fbuild')):
            module=request.GET['module_name']
            module_list=['academics','accounts','employe','hostel','hr','mms','registrar','reports1','stu_acc','studentportal']
            os.chdir('/usr/local/apache2/frontend_modules/')
            if module=='ALL':
                for module_name in module_list:
                    print(module_name)
                    path=('/usr/local/apache2/frontend_modules/'+module_name+'/src/index.html')
                    FileExists = os.path.isfile(path)
                    if FileExists:
                        os.chdir('/usr/local/apache2/frontend_modules/'+module_name)
                        pull='git pull origin master'
                        os.system(pull)
                        print(os.system("npm -v"))
                        os.system('gulp clean')
                        os.system('gulp build')
                        os.chdir('/usr/local/apache2/frontend_modules/')
                data={'script_executed'}
            else:
                print(module)
                path=('/usr/local/apache2/frontend_modules/'+module+'/src/index.html')
                FileExists = os.path.isfile(path)
                if FileExists:
                    os.chdir('/usr/local/apache2/frontend_modules/'+module)
                    pull='git pull origin master'
                    os.system(pull)
                    print(os.system("npm -v"))
                    os.system('gulp clean')
                    os.system('gulp build')
                    os.chdir('/usr/local/apache2/frontend_modules/')
            data={'script_executed'}
    return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
