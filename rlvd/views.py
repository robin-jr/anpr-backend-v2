from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models.functions import Length
from django.db.models import Count
import json
import os
import xlsxwriter
import PIL.Image as Image
from .models import LicensePlatesRlvd as LicensePlates
from .models import EvidenceCamImg, Violation, ViolationRef
from rlvd.models import Camera
# from .common.validators import is_valid, get_status_date_time
# from .common.functional_utils import get_filtered_data
# from .common.file_utils import create_excel
# from subprocess import Popen
# global camname
from datetime import datetime
import logging
from django.core import serializers
# import cv2
from django.http import StreamingHttpResponse
import time
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from django.views.decorators.csrf import csrf_exempt


from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

import csv

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
    violations = Violation.objects.filter(entry_id=id)
    d=[]
    for e in violations:
        temp={}
        temp["pk"]= e.pk
        temp["violation_id"]=e.violation_id
        d.append(temp)
    return d

def getViolationNames(id):
    violations = Violation.objects.filter(entry_id=id)
    refs= getViolationRefs()
    d=[]
    for e in violations:
        for ele in refs:
            if(ele["pk"]==e.violation_id):
                d.append(ele["violation_name"])
                break
    return d

def getEvidenceImages(id):
    evidenceImages = EvidenceCamImg.objects.filter(entry_id=id)
    d=[]
    for e in evidenceImages:
        d.append(e.evidence_image)
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
    cameraQuerySet = Camera.objects.all()
    cameras = []
    for cam in cameraQuerySet:
        cameras.append(cam.camera_name)
    return cameras


@api_view(['GET', ])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def index(request):
    cameras=getCameras();
    violationRefs=getViolationRefs()

    response = HttpResponse(
        json.dumps( {
            "cameras": cameras,
            "junction_names":[],
            "violationRefs":violationRefs,
        },),content_type="application/json"
        ,headers={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"*"}
    )
    return response


@csrf_exempt
@api_view(['POST', ])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_violations(request):
    if request.method=="POST":
        form_data = request.POST
        print("form_data", form_data)

        try:
            entry_id=form_data["entry_id"] # id of the particular entry
            old_violations=json.loads(form_data["old_violations"]) #[{pk:1,violation_id:2},{pk:2,violation_id:3}]
            new_violations=json.loads(form_data["new_violations"]) #[1,2,3]
            new_plate=form_data["new_plate"] 
            old_plate=form_data["old_plate"] 
            print("decrypted form data--> ",entry_id,old_plate,new_plate,old_violations,new_violations)
            if new_plate != old_plate:
                LicensePlates.objects.filter(pk=entry_id).update(number_plate_number=new_plate)

            # return HttpResponse(form_data)
            # entry_id=1
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
                newV = Violation(violation=ViolationRef.objects.filter(id=e).first(),entry=LicensePlates.objects.filter(pk=entry_id).first())
                newV.save()
            
            LicensePlates.objects.filter(pk=entry_id).update(reviewed=1)

            e=LicensePlates.objects.filter(pk=entry_id).first()
            temp={}
            temp["id"]= e.pk
            temp["camera_name"]= e.camera_name
            temp["junction_name"]= e.junction_name
            temp["evidence_camera_name"]= e.evidence_camera_name
            temp["plate"]= e.number_plate_number
            temp["date"]= str(e.date)
            temp["anpr_image"]= e.anpr_image
            temp["cropped_image"]= e.cropped_image
            temp["violations"]= getViolations(e.pk)
            temp["evidence_images"]=getEvidenceImages(e.pk)
            temp["reviewed"]=e.reviewed
           
            return HttpResponse(json.dumps({
            "entry":json.dumps(temp),
            }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})

        except Exception as e:
            print("<---error--> ",e)
            return HttpResponse(json.dumps({"error":"error"})
                ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})


@csrf_exempt
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


@csrf_exempt
@api_view(['POST', ])
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

            ## for now
            # vehicle_no= "1234"
            # cameras = ["SathyaShowroom Front"]
            # junction_names =["Sathya Showroom"]
            # start_date_time="2000-01-01T00:00"
            # end_date_time="2025-01-01T00:00"
            # vehicle_no= ""
            # cameras = []
            # junction_names =[]
            # start_date_time=""
            # end_date_time=""

            plates=LicensePlates.objects.all()
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
            
            
            count = plates.count()

            
            d=[]
            for e in plates:
                temp={}
                temp["id"]= e.pk
                temp["camera_name"]= e.camera_name
                temp["junction_name"]= e.junction_name
                temp["evidence_camera_name"]= e.evidence_camera_name
                temp["plate"]= e.number_plate_number
                temp["date"]= str(e.date)
                temp["anpr_image"]= e.anpr_image
                temp["cropped_image"]= e.cropped_image
                temp["violations"]= getViolations(e.pk)
                temp["evidence_images"]=getEvidenceImages(e.pk)
                temp["reviewed"]=e.reviewed
                d.append(temp)
           

            # license_plates= LicensePlates.objects.all()[:5] #temporary
            return HttpResponse(json.dumps({
                "count":count,
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
    head=['entry_id','vehicle_number','camera_name','junction_name','evidence_camera_name','date','anpr_image',
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


@csrf_exempt
def export_csv(request):
    form_data=request.POST
    try:
        vehicle_no= form_data["vehicle_number"] #can be empty 
        cameras = form_data["camera_names"] #can be empty
        junction_names =form_data["junction_names"] #can be empty
        start_date_time=form_data["start_date_time"] #can be empty. format: 2021-08-18T07:08  yyyy-mm-ddThh:mm
        end_date_time=form_data["end_date_time"]
        status_reviewed=form_data["status_reviewed"] # yes | no
        status_not_reviewed=form_data["status_not_reviewed"] # yes | no

        plates=LicensePlates.objects.all()
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
        
        
        count = plates.count()

        
        d=[]
        for e in plates:
            temp=[]
            temp.append(e.pk)
            temp.append(e.number_plate_number)
            temp.append(e.camera_name)
            temp.append(e.junction_name)
            temp.append(e.evidence_camera_name)
            temp.append(e.date.strftime('%d/%m/%Y %I:%M %p'))
            temp.append(e.anpr_image)
            temp.append(e.cropped_image)
            temp.append(getEvidenceImages(e.pk))
            temp.append(getViolationNames(e.pk))
            temp.append('yes' if e.reviewed else 'no')
            d.append(temp)

        data = download_csv( request, d)
        return HttpResponse (data, content_type='text/csv')
    except Exception as e:

        print("Exxception --> ",e);
        return HttpResponse("error")