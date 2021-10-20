from Registrar.models import StudentPrimDetail,StudentPerDetail
def functions_tester(request):
    batch_from=2019
    qry1=list(StudentPrimDetail.objects.filter(batch_from=batch_from,admission_type=22).values('uniq_id'))
    print(qry1)
    count=0
    f= open('name_lateral.txt','w')
    f1=open('name_lateral_not.txt','w')
    for stu in qry1:
        image_path=StudentPerDetail.objects.filter(uniq_id=stu['uniq_id']).values('image_path')[0]['image_path']
        print(image_path)
        if image_path == None:
            f1.write(str(stu['uniq_id']))
            f1.write('\n')
        else:
            f.write(image_path)
            f.write('\n')
        count+=1
    print(count)
    # f.write(strng for strng in lst)
    return 0
