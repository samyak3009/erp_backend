from celery import shared_task
import requests


@shared_task
def call_store_ctwise_marks(sessionid,subject_id,Section_id,dept_id,sem):
    url="http://tech.kiet.edu/api/hrms/Store_data/store_ctwise_marks/?dept="+str(dept_id)+"&section="+str(Section_id)+"&sem="+str(sem)+"&subject="+str(subject_id)
    print(url)
    headers = {
  'Cookie': sessionid
}
    r = requests.get(url,headers=headers)
    print(r)
    return
