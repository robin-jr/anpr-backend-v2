from datetime import date
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.db import connection
import io
from PIL import Image
import xlsxwriter
import json
from .models import LicensePlatesRlvd as LicensePlates
from .models import ViolationRef, AnprCamera
from rlvd.models import AnprCamera
import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Q

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

imageLocation = "/home/user/.webapp/ARIMA-Image-Server/images/"


# return the list of violations.
def getViolationRefs():
    violationRefs=ViolationRef.objects.all()
    d=[]
    for e in violationRefs:
        temp={}
        temp["id"]= e.pk
        temp["name"]=e.violation_name
        d.append(temp)
    return d

# returns the list of cameras.
def getCameras():
    cameraQuerySet = AnprCamera.objects.all()
    cameras = []
    for cam in cameraQuerySet:
        temp={}
        temp["camera_name"]=cam.camera_name
        temp["junction_name"]=cam.junction_name
        cameras.append(temp)
    return cameras

# return the list of map containing the junctions and the respective cameras in the junction.
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


# return the junctions, cameras and violations refs to the client.
@api_view(['GET', ])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def getInitialData(request):
    try:
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
    except Exception as e:
        print("error--> ",str(e))
        return HttpResponse(json.dumps({"error":str(e)})
            ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})


# get an entry and convert to dictionary.       
def getDictValue(e):
    temp={}
    temp['id']=e.entry_id
    temp["plate"]=e.number_plate_number
    temp["anpr_image"]=e.anpr_image
    temp["cropped_image"]=e.cropped_image
    temp["violations"]=e.violations.split(',') if len(e.violations)>0 else []
    temp["evidence_images"]=list(map(lambda x: x.strip(), e.evidence_images.split(','))) if len(e.evidence_images)>0 else []
    temp["junction_name"]=e.junction_name
    temp["camera_name"]=e.camera_name
    temp["evidence_camera_name"]=e.evidence_camera_name
    temp['speed']=str(e.speed)
    temp['speed_limit']=str(e.speed_limit)
    temp['date_time']=e.date.strftime('%d/%m/%Y %H:%M:%S')
    temp['reviewed']=True if e.reviewed else False
    return temp

# update the violation and status of an entry.
@api_view(['POST', ])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_violations(request):
    if request.method=="POST":
        form_data = request.POST
        try:
            id=form_data["id"] # id of the particular entry 
            violations=form_data["violations"] #[1,2,3]
            new_plate=form_data["new_plate"] 
            old_plate=form_data["old_plate"] 
            if new_plate != old_plate:
                LicensePlates.objects.filter(pk=id).update(number_plate_number=new_plate)

            LicensePlates.objects.filter(pk=id).update(violations=violations,reviewed=1)
            e=LicensePlates.objects.filter(pk=id).first()
            temp=getDictValue(e)
            return HttpResponse(json.dumps({
            "entry":temp,
            }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})

        except Exception as e:
            print("<---error--> ",e)
            return HttpResponse(json.dumps({"error":"error"})
                ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})


# return the queryset from the form data
def getQueryFromFormData(form_data):
    vehicle_no= form_data["vehicle_number"] #can be empty 
    cameras = form_data["camera_names"] #can be empty
    junction_names =form_data["junction_names"] #can be empty
    start_date_time=form_data["start_date_time"] #can be empty. format: 2021-08-18T07:08  yyyy-mm-ddThh:mm
    end_date_time=form_data["end_date_time"] #can be empty
    violations=form_data["violations"] #can be empty [1,2,3,4]

    if cameras!="":
        cameras=cameras.split(',')
    if junction_names!="":
        junction_names=junction_names.split(',')
    if violations!="":
        violations = list(map(lambda x: int(x), violations.split(',')))

    query = LicensePlates.objects.all()
    if len(vehicle_no)>0:
        query = query.filter(number_plate_number__contains=vehicle_no)
    if len(junction_names)>0:
        query = query.filter(junction_name__in=junction_names)
    if len(cameras)>0:
        query = query.filter(camera_name__in=cameras)
    if start_date_time != "":
        query = query.filter(date__gte=start_date_time)
    if end_date_time != "":
        query = query.filter(date__lte=end_date_time)
    if len(violations)>0 :
        if violations[0] == 4:
            q = Q(speed__gt = F('speed_limit'))
        else:
            q = Q(violations__contains = violations[0])
        violations.remove(violations[0])
        if 1 in violations:
            q.add(Q(violations__contains = 1), Q.OR)
        if 2 in violations:
            q.add(Q(violations__contains = 2), Q.OR)
        if 3 in violations:
            q.add(Q(violations__contains = 3), Q.OR)
        if 4 in violations:
            q.add(Q(speed__gt = F('speed_limit')), Q.OR)
        query = query.filter(q)
    return query

# return the search entries using the search condition.
# implemented pagination.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def plate_search(request):
    form_data = request.POST
    try:
        query = getQueryFromFormData(form_data)
        page = int(form_data["page"])
        count = int(form_data["count"])
        d=[]
        for e in query[(page) * count : (page+1)* count]:
            temp=getDictValue(e)
            d.append(temp)
        return HttpResponse(json.dumps({
            "count": query.count(),
            "entries":d,
            "filter_conditions": form_data,
        }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})
    except Exception as e:
        print("error--> ",e)
        return HttpResponse(json.dumps({"error":str(e)})
            ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})

# get the list of ids and return the name of the violations.
def getViolationsFromIds(ids, speed, speed_limit):
    ids = ids.split(',')
    if speed > speed_limit:
        ids.append(4)
    violations = []
    for id in ids:
        violations.append(ViolationRef.objects.get(id = id).violation_name)
    return violations

# create and return a excel sheet with the data
# for version 1
def createExcelv1(query, start, end):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    headers = ['S.No','Plate Number','Junction Name','Camera Name', 'Evidence Camera Name','Date','Full Image','Cropped Image', 'Violations', 'Reviewed']
    bold = workbook.add_format({'bold': True, "font_size": 18, 'align': 'center'})
    center = workbook.add_format({"align": "center", "font_size": 15})
    worksheet.set_row(0,30)
    worksheet.set_default_row(100)
    worksheet.set_column(0, len(headers) + 5, 30)
    row = 0
    for idx, head in enumerate(headers):
        worksheet.write(row, idx, head, bold)
    row += 1
    for data in query[start: end]:
        
        worksheet.write(row, 0, row+start, center)
        worksheet.write(row, 1, data.number_plate_number, center)        
        worksheet.write(row, 2, data.junction_name, center)
        worksheet.write(row, 3, data.camera_name, center)
        worksheet.write(row, 4, data.evidence_camera_name, center)       
        worksheet.write(row, 5, str(data.date.strftime('%d/%m/%Y %H:%M:%S')), center)
        imagePath =imageLocation+data.anpr_image
        try:
            with Image.open(imagePath) as img:
                width, height = img.size
                x_scale = 30/width
                y_scale = 100/height
                worksheet.insert_image(row, 6,imagePath, {"x_scale": x_scale*7.2,
                                                    "y_scale": y_scale*1.5,
                                                    "positioning": 1})
        except Exception as e:
            imagePath = imageLocation+"noImage.jpg"
            with Image.open(imagePath) as img:
                img_width, img_height = img.size
                x_scale = 30/img_width
                y_scale = 100/img_height
                worksheet.insert_image(row,
                                    6,
                                    imagePath,
                                    {"x_scale": x_scale*7.2,
                                        "y_scale": y_scale*1.5,
                                        "positioning": 1})

        imagePath = imageLocation+data.cropped_image
        try:
            with Image.open(imagePath) as img:
                width, height = img.size
                x_scale = 30/width
                y_scale = 100/height
                worksheet.insert_image(row, 7,imagePath, {"x_scale": x_scale*7.2,
                                                    "y_scale": y_scale*1.5,
                                                    "positioning": 1})
        except Exception as e:
            imagePath = imageLocation+"noImage.jpg"
            with Image.open(imagePath) as img:
                img_width, img_height = img.size
                x_scale = 30/img_width
                y_scale = 100/img_height
                worksheet.insert_image(row,
                                    7,
                                    imagePath,
                                    {"x_scale": x_scale*7.2,
                                        "y_scale": y_scale*1.5,
                                        "positioning": 1})
        violations = getViolationsFromIds(data.violations, 0, 0)
        worksheet.write(row, 8, str(violations), center) 
        worksheet.write(row, 9, "Yes" if data.reviewed else "No", center)
        row += 1
    workbook.close()
    return output.getvalue()

# create and return a excel sheet with the data
# for version 2
def createExcelv2(query, start, end):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    headers = ['S.No','Plate Number','Junction Name','Camera Name', 'Evidence Camera Name','Date','Full Image','Cropped Image','Speed', 'Speed Limit', 'Violations', 'Reviewed']
    bold = workbook.add_format({'bold': True, "font_size": 18, 'align': 'center'})
    center = workbook.add_format({"align": "center", "font_size": 15})
    worksheet.set_row(0,30)
    worksheet.set_default_row(100)
    worksheet.set_column(0, len(headers) + 5, 30)
    row = 0
    for idx, head in enumerate(headers):
        worksheet.write(row, idx, head, bold)
    row += 1
    for data in query[start: end]:
        worksheet.write(row, 0, row+start, center)
        worksheet.write(row, 1, data.number_plate_number, center)        
        worksheet.write(row, 2, data.junction_name, center)
        worksheet.write(row, 3, data.camera_name, center)
        worksheet.write(row, 4, data.evidence_camera_name, center)       
        worksheet.write(row, 5, str(data.date.strftime('%d/%m/%Y %H:%M:%S')), center)
        imagePath =imageLocation+data.anpr_image
        try:
            with Image.open(imagePath) as img:
                width, height = img.size
                x_scale = 30/width
                y_scale = 100/height
                worksheet.insert_image(row, 6,imagePath, {"x_scale": x_scale*7.2,
                                                    "y_scale": y_scale*1.5,
                                                    "positioning": 1})
        except Exception as e:
            imagePath = imageLocation+"noImage.jpg"
            with Image.open(imagePath) as img:
                img_width, img_height = img.size
                x_scale = 30/img_width
                y_scale = 100/img_height
                worksheet.insert_image(row,
                                    6,
                                    imagePath,
                                    {"x_scale": x_scale*7.2,
                                        "y_scale": y_scale*1.5,
                                        "positioning": 1})

        imagePath = imageLocation+data.cropped_image
        try:
            with Image.open(imagePath) as img:
                width, height = img.size
                x_scale = 30/width
                y_scale = 100/height
                worksheet.insert_image(row, 7,imagePath, {"x_scale": x_scale*7.2,
                                                    "y_scale": y_scale*1.5,
                                                    "positioning": 1})
        except Exception as e:
            imagePath = imageLocation+"noImage.jpg"
            with Image.open(imagePath) as img:
                img_width, img_height = img.size
                x_scale = 30/img_width
                y_scale = 100/img_height
                worksheet.insert_image(row,
                                    7,
                                    imagePath,
                                    {"x_scale": x_scale*7.2,
                                        "y_scale": y_scale*1.5,
                                        "positioning": 1})       
        worksheet.write(row, 8, str(data.speed), center)              
        worksheet.write(row, 9, str(data.speed_limit), center)
        violations = getViolationsFromIds(data.violations, data.speed, data.speed_limit)
        worksheet.write(row, 10, str(violations), center) 
        worksheet.write(row, 11, "Yes" if data.reviewed else "No", center)
        row += 1
    workbook.close()
    return output.getvalue()

# return the export entries count for pagination purpose.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def getExportDataLength(request):
    form_data = request.POST
    try:
        query = getQueryFromFormData(form_data)
        status_reviewed=form_data["status_reviewed"] # yes | no
        status_not_reviewed=form_data["status_not_reviewed"] # yes | no
        if status_reviewed =="yes" and status_not_reviewed =="no":
            query=query.filter(reviewed=1)
        if status_reviewed =="no" and status_not_reviewed =="yes":
            query=query.filter(reviewed=0)
        return HttpResponse(json.dumps({
            "count":query.count(),
            "filter_conditions": form_data,
        }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})
    except Exception as e:
        print("error--> ",e)
        return HttpResponse(json.dumps({"error":str(e)})
            ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})


# export excel 
# for version 1.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def exportExcelv1(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    form_data=request.POST
    try:
        query = getQueryFromFormData(form_data)
        status_reviewed=form_data["status_reviewed"] # yes | no
        status_not_reviewed=form_data["status_not_reviewed"] # yes | no
        start = int(form_data["start"])  # USED TO SEGMENT THE EXPORT DATA(START OF THE ENTRY - INDEX)
        end = int(form_data["end"])        #USED TO SEGMENT THE EXPORT DATA(END OF THE ENTRY - INDEX)
        if status_reviewed =="yes" and status_not_reviewed =="no":
            query=query.filter(reviewed=1)
        if status_reviewed =="no" and status_not_reviewed =="yes":
            query=query.filter(reviewed=0)
        xlsx_data = createExcelv1(query, start, end)
        response.write(xlsx_data)
        return response
    except Exception as e:
        print("error--> ",e)
        return HttpResponse(json.dumps({"error":str(e)})
            ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})

# export excel 
# for version 2.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def exportExcelv2(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format("RLVD entries.xlsx")
    form_data=request.POST
    try:
        query = getQueryFromFormData(form_data)
        status_reviewed=form_data["status_reviewed"] # yes | no
        status_not_reviewed=form_data["status_not_reviewed"] # yes | no
        start = int(form_data["start"])  # USED TO SEGMENT THE EXPORT DATA(START OF THE ENTRY - INDEX)
        end = int(form_data["end"])        #USED TO SEGMENT THE EXPORT DATA(END OF THE ENTRY - INDEX)
        if status_reviewed =="yes" and status_not_reviewed =="no":
            query=query.filter(reviewed=1)
        if status_reviewed =="no" and status_not_reviewed =="yes":
            query=query.filter(reviewed=0)
        xlsx_data = createExcelv2(query, start, end)
        response.write(xlsx_data)
        return response
    except Exception as e:
        print("error--> ",e)
        return HttpResponse(json.dumps({"error":str(e)})
            ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})