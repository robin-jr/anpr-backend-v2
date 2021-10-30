from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.db import connection
import io
from PIL import Image
import xlsxwriter
import json
from .models import LicensePlatesRlvd as LicensePlates
from .models import EvidenceCamImg, Violation, ViolationRef, AnprCamera
from rlvd.models import AnprCamera
import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from django.views.decorators.csrf import csrf_exempt


from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

import csv

HOST_STATIC_FOLDER_URL = "http://localhost:8001/static/"

@api_view(['GET', ])
# @permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
@permission_classes([])
@authentication_classes([])
def sample(request):
    return Response("good")

# django_dir = os.environ['DJANGOPATH']#"/home/user/Django_Anpr-master/" # Directory containing Django manage.py
# logs_dir = os.environ['LOGSPATH']#"/home/"+str(os.environ.get('USER'))+"/logs/"# Directory to store log files and the log file format
# if not os.path.exists(logs_dir):# Create Directory if it doesn't exist
#     os.makedirs(logs_dir)
# logging.basicConfig(filename=logs_dir+"django.log", level=logging.INFO,
#     format=("%(asctime)s - %(levelname)s:%(process)d:%(processName)s:%(filename)s - Function Name:%(funcName)s - Line No:%(lineno)d - %(message)s  "))
#logging.info("STARTED DJANGO SERVER")

def getViolations(id):
    violations = Violation.objects.filter(object_id=id)
    d=[]
    for e in violations:
        temp={}
        temp["pk"]= e.pk
        temp["violation_id"]=e.violation_id
        d.append(temp)
    return d

def getViolationNames(id):
    violations = Violation.objects.filter(object_id=id)
    refs= getViolationRefs()
    d=[]
    for e in violations:
        for ele in refs:
            if(ele["pk"]==e.violation_id):
                d.append(ele["violation_name"])
                break
    return d

def getEvidenceImages(id):
    evidenceImages = EvidenceCamImg.objects.filter(object_id=id)
    d=[]
    for e in evidenceImages:
        d.append(e.evidence_image)
    return d

def getEvidenceImagesWithHostUrl(id):
    evidenceImages = EvidenceCamImg.objects.filter(object_id=id)
    d=[]
    for e in evidenceImages:
        d.append(HOST_STATIC_FOLDER_URL + e.evidence_image)
    return d

def getViolationRefs():
    violationRefs=ViolationRef.objects.all()
    d=[]
    for e in violationRefs:
        temp={}
        temp["pk"]= e.pk
        temp["violation_name"]=e.violation_name
        d.append(temp)
    return d

def getCameras():
    cameraQuerySet = AnprCamera.objects.all()
    cameras = []
    for cam in cameraQuerySet:
        temp={}
        temp["camera_name"]=cam.camera_name
        temp["junction_name"]=cam.junction_name
        cameras.append(temp)
        # cameras.append(cam.camera_name)
    return cameras

def getJuctionsAndCameras():
    cameraQuerySet = AnprCamera.objects.all()
    cameras=[]
    junctions_and_cameras = []
    unique_junctions=set()
    for cam in cameraQuerySet:
        unique_junctions.add(cam.junction_name)
        temp={}
        temp["camera_name"]=cam.camera_name
        temp["junction_name"]=cam.junction_name
        cameras.append(temp)
    unique_junctions=list(unique_junctions)
    for e in unique_junctions:
        junctions_and_cameras.append({"junction_name":e,"cameras":list(map(lambda x:x["camera_name"],filter(lambda x:x["junction_name"]==e,cameras)))})
    return junctions_and_cameras


@api_view(['GET', ])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def index(request):
    # cameras=getCameras();
    junctions_and_cameras=getJuctionsAndCameras()
    violationRefs=getViolationRefs()

    response = HttpResponse(
        json.dumps( {
            "junctions_and_cameras": junctions_and_cameras, 
            "violationRefs":violationRefs,
        },),content_type="application/json"
        ,headers={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"*"}
    )
    return response


# @csrf_exempt
@api_view(['POST', ])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_violations(request):
    if request.method=="POST":
        form_data = request.POST
        print("form_data", form_data)

        try:
            object_id=form_data["object_id"] # id of the particular entry ##have to change name to object_id in frontend
            old_violations=json.loads(form_data["old_violations"]) #[{pk:1,violation_id:2},{pk:2,violation_id:3}]
            new_violations=json.loads(form_data["new_violations"]) #[1,2,3]
            new_plate=form_data["new_plate"] 
            old_plate=form_data["old_plate"] 
            print("decrypted form data--> ",object_id,old_plate,new_plate,old_violations,new_violations)
            if new_plate != old_plate:
                LicensePlates.objects.filter(object_id=object_id).update(number_plate_number=new_plate)

            # return HttpResponse(form_data)
            # object_id=1
            # old_violations=[{"pk": 1, "violation_id": 1}, {"pk": 2, "violation_id": 2}]
            # new_violations=[1,3]

            toRemove=[]
            for e in old_violations:
                if e["violation_id"] in new_violations:
                    new_violations.remove(e["violation_id"])
                else:   
                    toRemove.append(e["pk"])

            Violation.objects.filter(pk__in=toRemove).delete()
            for e in new_violations:
                newV = Violation(violation=ViolationRef.objects.filter(id=e).first(),object_id=object_id)
                newV.save()
            
            LicensePlates.objects.filter(object_id=object_id).update(reviewed=1)

            e=LicensePlates.objects.filter(object_id=object_id).first()
            temp={}
            temp["id"]= e.pk
            temp["object_id"]= e.object_id
            temp["camera_name"]= e.camera_name
            temp["junction_name"]= e.junction_name
            temp["evidence_camera_name"]= e.evidence_camera_name
            temp["plate"]= e.number_plate_number
            temp["date"]= e.date.strftime('%d/%m/%Y %H:%M:%S')
            temp["anpr_image"]= e.anpr_image
            temp["cropped_image"]= e.cropped_image
            temp["violations"]= getViolations(e.object_id)
            temp["evidence_images"]=getEvidenceImages(e.object_id)
            temp["reviewed"]=e.reviewed
           
            return HttpResponse(json.dumps({
            "entry":json.dumps(temp),
            }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})

        except Exception as e:
            print("<---error--> ",e)
            return HttpResponse(json.dumps({"error":"error"})
                ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})


# @csrf_exempt
@api_view(['GET', ])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_violations(request):
    if request.method == "GET":
        form_data = request.GET
        print("form_data", form_data)
        # id=form_data["id"]
        id=1
        violations= getViolations(id)

        return HttpResponse(json.dumps({
            "violations":json.dumps(violations),
            "filter_conditions": form_data,
        }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})


# @csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def plate_search(request):
    if request.method == "POST":
        form_data = request.POST
        print("form_data", form_data)
        try:
            vehicle_no= form_data["vehicle_number"] #can be empty 
            cameras = form_data["camera_names"] #can be empty
            junction_names =form_data["junction_names"] #can be empty
            start_date_time=form_data["start_date_time"] #can be empty. format: 2021-08-18T07:08  yyyy-mm-ddThh:mm
            end_date_time=form_data["end_date_time"] #can be empty 

            if cameras!="":
                cameras="("+str(cameras.split(','))[1:-1]+")"
            if junction_names!="":
                junction_names="("+str(junction_names.split(','))[1:-1]+")"
            d=[]


            # #for where clause
            # condition = ""
            condition = 'where '
            # if vehicle_no != '':
            condition += 'e.number_plate_number like "%'+vehicle_no+'%" '
            if len(junction_names)>0:
                condition += 'and e.junction_name in '+str(junction_names) +' '
            if len(cameras)>0:
                condition += 'and e.camera_name in '+str(cameras) +' '
            if start_date_time != "":
                condition += 'and date >= "{}" '.format(start_date_time)
            if end_date_time != "":
                condition += 'and date <= "{}" '.format(end_date_time)
            #query + where clause
            query = 'select ec.*, group_concat(concat(v.id,",", v.violation_id)) as violations_made from ( select e.*, group_concat(c.evidence_image) as evidence_images from license_plates_rlvd as e inner join evidence_cam_img as c on c.object_id = e.object_id {}group by e.object_id) as ec inner join violations as v on v.object_id = ec.object_id group by ec.object_id order by ec.entry_id asc;'.format(condition)
            print(query)
            with connection.cursor() as cursor:
                cursor.execute("SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));")
                cursor.execute(query)
                rows = cursor.fetchall()
                cols = cursor.description #column names will be available here
                for row in rows:
                    temp = {}
                    for i in range(len(row)):
                        if cols[i][0] == "entry_id":
                            temp["id"] = row[i]
                        elif cols[i][0] == "number_plate_number":
                            temp["plate"] = row[i]
                        elif cols[i][0] == "date":
                            temp[cols[i][0]] = row[i].strftime('%d/%m/%Y %H:%M:%S')
                        elif cols[i][0] == "evidence_images":
                            imgs = row[i].split(",")
                            temp[cols[i][0]] = imgs
                        elif cols[i][0] == "violations_made":
                            temp["violations"] = []
                            vioArr = row[i].split(",")
                            i = 0
                            while i < len(vioArr):
                                temp["violations"].append({"pk": int(vioArr[i]), "violation_id": int(vioArr[i+1])})
                                i+=2
                        else:
                            temp[cols[i][0]] = row[i]
                    d.append(temp)
            return HttpResponse(json.dumps({
                "count":len(d),
                "entries":json.dumps(d),
                "filter_conditions": form_data,
            }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})
        except Exception as e:
            print("error--> ",e)
            return HttpResponse(json.dumps({"error":str(e)})
                ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})
    else:
        logging.info("Plate Search - End")
        return HttpResponseBadRequest("Bad Request!",headers={"Access-Control-Allow-Origin":"*"})


def download_csv( request, array):
    # opts = queryset.model._meta
    # model = queryset.model
    response = HttpResponse(content_type='text/csv')
    # force download.
    response['Content-Disposition'] = 'attachment;filename=export.csv'
    # the csv writer
    writer = csv.writer(response)
    # field_names = [field.name for field in opts.fields]
    # Write a first row with header information
    head=['object_id','vehicle_number','camera_name','junction_name','evidence_camera_name','date','anpr_image',
    'license_plate_image','evidence_images','violations','reviewed']

    # writer.writerow(field_names)
    writer.writerow(head)
    # writer.writerow(body)
    # Write data rows
    # array= [['a','b'],['c','d']]
    for row in array:
        writer.writerow(row)
    return response
download_csv.short_description = "Download selected as csv"


# @csrf_exempt
@api_view(['POST', ])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def export_csv(request):
    form_data=request.POST
    print("Form Data", form_data)
    try:
        vehicle_no= form_data["vehicle_number"] #can be empty 
        cameras = form_data["camera_names"] #can be empty
        junction_names =form_data["junction_names"] #can be empty
        start_date_time=form_data["start_date_time"] #can be empty. format: 2021-08-18T07:08  yyyy-mm-ddThh:mm
        end_date_time=form_data["end_date_time"]
        status_reviewed=form_data["status_reviewed"] # yes | no
        status_not_reviewed=form_data["status_not_reviewed"] # yes | no

        plates=LicensePlates.objects.all()
        if cameras!="":
            cameras=cameras.split(',')
        if junction_names!="":
            junction_names=junction_names.split(',')
            

        print("Vehicle NO: ", vehicle_no, "Cameras", cameras, "Junction Names", junction_names)
        if vehicle_no!="":
            plates = LicensePlates.objects.filter(number_plate_number__contains=vehicle_no)
        if len(cameras)>0:
            plates =plates.filter(camera_name__in=cameras)
        if len(junction_names)>0:
            plates=plates.filter(junction_name__in=junction_names)
        if start_date_time!="":
            plates=plates.filter(date__gte=start_date_time)
        if end_date_time!="":
            plates=plates.filter(date__lte=end_date_time)
        if status_reviewed =="yes" and status_not_reviewed =="no":
            plates=plates.filter(reviewed=1)
        if status_reviewed =="no" and status_not_reviewed =="yes":
            plates=plates.filter(reviewed=0)
        
        
        # count = plates.count()

        
        d=[]
        for e in plates:
            temp=[]
            temp.append(e.object_id)
            temp.append(e.number_plate_number)
            temp.append(e.camera_name)
            temp.append(e.junction_name)
            temp.append(e.evidence_camera_name)
            temp.append(e.date.strftime('%d/%m/%Y %H:%M:%S'))
            temp.append(HOST_STATIC_FOLDER_URL + e.anpr_image)
            temp.append(HOST_STATIC_FOLDER_URL + e.cropped_image)
            temp.append(getEvidenceImagesWithHostUrl(e.object_id))
            temp.append(getViolationNames(e.object_id))
            temp.append('yes' if e.reviewed else 'no')
            d.append(temp)

        # print("CSV Data", d)
        data = download_csv( request, d)
        return HttpResponse (data, content_type='text/csv')
    except Exception as e:
        print("Exxception --> ",e);
        return HttpResponse("error")

def createExcel(rows, cols):
    path = "/app/rlvd/static/"
    output      = io.BytesIO()
    workbook    = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True, "font_size": 18, 'align': 'center'})
    worksheet.set_row(0,30)
    headers = ['Entry ID','Object ID','Plate Number','Junction Name','Camera Name', 'Evidence Camera Name','Date','Full Image','Cropped Image', 'Violations', 'Reviewed', 'Evidence Image 1', 'Evidence Image 2', 'Evidence Image 3', 'Evidence Image 4', 'Evidence Image 5', 'Evidence Image 6']
    row = 0
    # for col in cols:
    #     print(col[0])
    for idx, head in enumerate(headers):
        worksheet.write(row, idx, head, bold)
    row += 1
    if(len(rows)>0):
        worksheet.set_default_row(100)
        worksheet.set_column(0, len(rows[0]) + 5, 30)
        center = workbook.add_format({"align": "center", "font_size": 15})
        
        for data in rows:
            worksheet.write(row, 0, data[0], center)
            worksheet.write(row, 1, data[1], center)        
            worksheet.write(row, 2, data[5], center)
            worksheet.write(row, 3, data[3], center)
            worksheet.write(row, 4, data[2], center)       
            worksheet.write(row, 5, data[4], center)        
            worksheet.write(row, 6, str(data[6].strftime('%d/%m/%Y %H:%M:%S')), center)              
            worksheet.write(row, 9, data[11], center)
            worksheet.write(row, 10, "Yes" if data[9] else "No", center)
            imagePath =path+data[7]
            try:
                with Image.open(imagePath) as img:
                    width, height = img.size
                    x_scale = 30/width
                    y_scale = 100/height
                    worksheet.insert_image(row, 7,imagePath, {"x_scale": x_scale*7.2,
                                                        "y_scale": y_scale*1.5,
                                                        "positioning": 1})
            except Exception as e:
                imagePath = path+"images/results/noImage.png"
                with Image.open(imagePath) as img:
                    img_width, img_height = img.size
                    #print("path",path,"img_width", img_width, "img_height", img_height)
                    x_scale = 30/img_width
                    y_scale = 100/img_height
                    worksheet.insert_image(row,
                                        7,
                                        imagePath,
                                        {"x_scale": x_scale*7.2,
                                            "y_scale": y_scale*1.5,
                                            "positioning": 1})

            imagePath = path+data[8]
            try:
                with Image.open(imagePath) as img:
                    width, height = img.size
                    x_scale = 30/width
                    y_scale = 100/height
                    worksheet.insert_image(row, 8,imagePath, {"x_scale": x_scale*7.2,
                                                        "y_scale": y_scale*1.5,
                                                        "positioning": 1})
            except Exception as e:
                imagePath = path+"images/results/noImage.png"
                with Image.open(imagePath) as img:
                    img_width, img_height = img.size
                    #print("path",path,"img_width", img_width, "img_height", img_height)
                    x_scale = 30/img_width
                    y_scale = 100/img_height
                    worksheet.insert_image(row,
                                        8,
                                        imagePath,
                                        {"x_scale": x_scale*7.2,
                                            "y_scale": y_scale*1.5,
                                            "positioning": 1})
            evidenceImages = data[10].split(',')
            for i in range(6):
                try:
                    imagePath = path+evidenceImages[i]
                    with Image.open(imagePath) as img:
                        width, height = img.size
                        x_scale = 30/width
                        y_scale = 100/height
                        worksheet.insert_image(row, 11 + i,imagePath, {"x_scale": x_scale*7.2,
                                                            "y_scale": y_scale*1.5,
                                                            "positioning": 1})
                except Exception as e:
                    imagePath = path+"images/results/noImage.png"
                    with Image.open(imagePath) as img:
                        img_width, img_height = img.size
                        #print("path",path,"img_width", img_width, "img_height", img_height)
                        x_scale = 30/img_width
                        y_scale = 100/img_height
                        worksheet.insert_image(row,
                                            11 + i,
                                            imagePath,
                                            {"x_scale": x_scale*7.2,
                                                "y_scale": y_scale*1.5,
                                                "positioning": 1})
            row += 1
    workbook.close()
    return output.getvalue()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def exportExcel(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format("RLVD entries.xlsx")
    form_data=request.POST
    print("Form Data", form_data)
    try:
        vehicle_no= form_data["vehicle_number"] #can be empty 
        cameras = form_data["camera_names"] #can be empty
        junction_names = form_data["junction_names"]
        start_date_time=form_data["start_date_time"] #can be empty. format: 2021-08-18T07:08  yyyy-mm-ddThh:mm
        end_date_time=form_data["end_date_time"]
        status_reviewed=form_data["status_reviewed"] # yes | no
        status_not_reviewed=form_data["status_not_reviewed"] # yes | no
        # status_reviewed = "no"
        # status_not_reviewed = "no"
        # vehicle_no = ""
        # cameras = ""
        # junction_names = ""
        # start_date_time = ""
        # end_date_time = ""
        if cameras!="":
                cameras="("+str(cameras.split(','))[1:-1]+")"
        if junction_names!="":
            junction_names="("+str(junction_names.split(','))[1:-1]+")"
        # #for where clause
        # condition = ""
        condition = 'where '
        # if vehicle_no != '':
        condition += 'e.number_plate_number like "%'+vehicle_no+'%" '
        # condition += 'e.number_plate_number like "%TN05AB%" '

        if len(junction_names)>0:
            condition += 'and e.junction_name in '+str(junction_names) +' '
        if len(cameras)>0:
            condition += 'and e.camera_name in '+str(cameras) +' '
        if start_date_time != "":
            condition += 'and e.date >= "{}" '.format(start_date_time)
        if end_date_time != "":
            condition += 'and e.date <= "{}" '.format(end_date_time)
        if status_reviewed =="yes" and status_not_reviewed =="no":
            condition += 'and e.reviewed = 1 '
        if status_reviewed =="no" and status_not_reviewed =="yes":
            condition += 'and e.reviewed = 0 '
        #query + where clause
        query = 'select ec.*, vvr.violations_made from ( select e.*,group_concat(c.evidence_image) as evidence_images from license_plates_rlvd as e inner join evidence_cam_img as c on c.object_id = e.object_id {}group by e.object_id) as ec inner join (select v.object_id, group_concat(violation_name) as violations_made from violations as v inner join violation_ref as vr on v.violation_id = vr.id group by v.object_id) as vvr on vvr.object_id = ec.object_id order by ec.entry_id asc;'.format(condition)
        print(query)
        with connection.cursor() as cursor:
            # cursor.execute("SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));")
            cursor.execute(query)
            rows = cursor.fetchall()
            cols = cursor.description #column names will be available here
            xlsx_data = createExcel(rows, cols)
            response.write(xlsx_data)
            return response
    except Exception as e:
        print("this one throws error--> ",str(e))
        return HttpResponse(json.dumps({"error":str(e)})
            ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})

        