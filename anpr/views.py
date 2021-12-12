from arima_backend_v2.settings import STATIC_ROOT, STATIC_URL
from rlvd.views import HOST_STATIC_FOLDER_URL
from .models import LicensePlatesAnpr as LicensePlates, VehicleColorRef, VehicleModelRef, VehicleMakeRef, VehicleTypeRef
from rlvd.models import AnprCamera
import csv
import logging
import io
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, response
from django.shortcuts import render
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from datetime import datetime
import cv2
import xlsxwriter
import pyudev
import psutil
from django.http import StreamingHttpResponse

import json


def getCameras():
    camQuerySet = AnprCamera.objects.only('id', 'camera_name', 'latitude', 'longitude', 'rtsp_url')
    cams = []
    for cam in camQuerySet:
        temp = {}
        temp["id"] = cam.id
        temp["name"] = cam.camera_name
        temp["latitude"] = str(cam.latitude)
        temp["longitude"] = str(cam.longitude)
        temp["rtsp_url"] = cam.rtsp_url
        cams.append(temp)

    return cams

def getVehicleTypes():
    typesQuerySet = VehicleTypeRef.objects.all()
    types = []
    for type in typesQuerySet:
        temp = {}
        temp["id"] = type.pk
        temp["name"] = type.name
        types.append(temp)

    return types

def getVehicleMakes():
    makesQuerySet = VehicleMakeRef.objects.all()
    makes = []
    for make in makesQuerySet:
        temp = {}
        temp['id'] = make.pk
        temp['name'] = make.name
        temp['type'] = make.type_id
        makes.append(temp)
    return makes

def getVehicleModels():
    modelsQuerySet = VehicleModelRef.objects.select_related('type').select_related('make').all()
    models = []
    for model in modelsQuerySet:
        temp = {}
        temp['id'] = model.pk
        temp['name'] = model.name
        temp['make'] = model.make.id
        temp['type'] = model.type.id
        # print(model.type.name)
        models.append(temp)
    return models

def getVehicleColors():
    colorsQuerySet = VehicleColorRef.objects.all()
    colors = []
    for color in colorsQuerySet:
        temp = {}
        temp['id'] = color.pk
        temp['name'] = color.name
        temp['code'] = color.code
        colors.append(temp)

    # print("Colors: ", colors)
    return colors

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def initialData(request):
    cameras = getCameras()
    vehicleTypes = getVehicleTypes()
    vehicleMakes = getVehicleMakes()
    vehicleModels = getVehicleModels()
    vehicleColors = getVehicleColors()
    
    return HttpResponse(json.dumps({
                "cameras":json.dumps(cameras),
                "vehicle_types": json.dumps(vehicleTypes),
                "vehicle_makes": json.dumps(vehicleMakes),
                "vehicle_models": json.dumps(vehicleModels),
                "vehicle_colors": json.dumps(vehicleColors)
                # "filter_conditions": form_data,
            }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def getCameraLatestEntriesAndRecognitions(request):
    if request.method == "POST":
        form_data = request.POST
        # print("form_data", form_data)
        camera_name = form_data["camera_name"]
        recognitionCount = LicensePlates.objects.filter(camera_name = camera_name).count()
        plateQuerySet = LicensePlates.objects.filter(camera_name = camera_name).select_related('vehicle_type').select_related('vehicle_make').select_related('vehicle_model').select_related('vehicle_color').order_by('-entry_id')[:5]
        entries = []
        for data in plateQuerySet:
            temp={}
            temp["id"]= data.pk
            temp["camera_name"]= data.camera_name
            # temp["junction_name"]= e.junction_name
            temp["plate"]= data.plate_number
            temp["date"]= data.date.strftime('%d/%m/%Y %H:%M:%S')
            temp["anpr_full_image"]= data.anpr_full_image
            temp["anpr_cropped_image"]= data.anpr_cropped_image
            temp["vehicle_type"] = data.vehicle_type.name
            temp["vehicle_make"] = data.vehicle_make.name
            temp["vehicle_model"] = data.vehicle_model.name
            temp["vehicle_color_name"] = data.vehicle_color.name
            temp["vehicle_color_code"] = data.vehicle_color.code
            entries.append(temp)
        return HttpResponse(json.dumps({
                    "count":recognitionCount,
                    "entries":json.dumps(entries),
                    "filter_conditions": form_data,
                }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})
    else:
        logging.info("Latest Entries - End")
        return HttpResponseBadRequest("Bad Request!",headers={"Access-Control-Allow-Origin":"*"})

def getQueryFromFormDatav1(form_data):
    vehicle_no= form_data["vehicle_number"] #can be empty 
    cameras = form_data["camera_names"] #can be empty
    start_date_time=form_data["start_date_time"] #can be empty. format: 2021-08-18T07:08  yyyy-mm-ddThh:mm
    end_date_time=form_data["end_date_time"] #can be empty 


    # # dummy Data
    # vehicle_no = ""
    # cameras = ""
    # start_date_time = ""
    # end_date_time = ""


    if cameras!="":
        cameras=cameras.split(',')



    platesQuerySet=LicensePlates.objects.all()

    if vehicle_no!="":
        platesQuerySet = platesQuerySet.filter(plate_number__contains=vehicle_no)
    if len(cameras)>0:
        platesQuerySet =platesQuerySet.filter(camera_name__in=cameras)
    if start_date_time!="":
        platesQuerySet=platesQuerySet.filter(date__gte=start_date_time)
    if end_date_time!="":
        platesQuerySet=platesQuerySet.filter(date__lte=end_date_time)
    
    

    platesQuerySet = platesQuerySet.select_related('vehicle_type').select_related('vehicle_make').select_related('vehicle_model').select_related('vehicle_color')
    return platesQuerySet

def getQueryFromFormDatav2(form_data):
    vehicle_no= form_data["vehicle_number"] #can be empty 
    cameras = form_data["camera_names"] #can be empty
    start_date_time=form_data["start_date_time"] #can be empty. format: 2021-08-18T07:08  yyyy-mm-ddThh:mm
    end_date_time=form_data["end_date_time"] #can be empty 
    vehicle_type = form_data["vehicle_type"]#can be empty
    vehicle_make = form_data["vehicle_make"]#can be empty
    vehicle_model = form_data["vehicle_model"]#can be empty
    vehicle_color = form_data["vehicle_color"]#can be empty

    if cameras!="":
        cameras=cameras.split(',')
    if vehicle_type!="":
        vehicle_type = list(map(lambda x: int(x), list(vehicle_type.split(','))))
    if vehicle_make!="":
        vehicle_make = list(map(lambda x: int(x), list(vehicle_make.split(','))))
    if vehicle_model!="":
        vehicle_model = list(map(lambda x: int(x), list(vehicle_model.split(','))))
    if vehicle_color!="":
        vehicle_color = list(map(lambda x: int(x), list(vehicle_color.split(','))))



    platesQuerySet=LicensePlates.objects.all()

    if vehicle_no!="":
        platesQuerySet = platesQuerySet.filter(plate_number__contains=vehicle_no)
    if len(cameras)>0:
        platesQuerySet =platesQuerySet.filter(camera_name__in=cameras)
    if start_date_time!="":
        platesQuerySet=platesQuerySet.filter(date__gte=start_date_time)
    if end_date_time!="":
        platesQuerySet=platesQuerySet.filter(date__lte=end_date_time)
    if len(vehicle_type)>0:
        platesQuerySet = platesQuerySet.filter(vehicle_type__in=vehicle_type)
    if len(vehicle_make)>0:
        platesQuerySet = platesQuerySet.filter(vehicle_make__in=vehicle_make)
    if len(vehicle_model)>0:
        platesQuerySet = platesQuerySet.filter(vehicle_model__in=vehicle_model)
    if len(vehicle_color)>0:
        platesQuerySet = platesQuerySet.filter(vehicle_color__in=vehicle_color)
    

    platesQuerySet = platesQuerySet.select_related('vehicle_type').select_related('vehicle_make').select_related('vehicle_model').select_related('vehicle_color')
    return platesQuerySet


def getDictFromQuery(platesQuerySet):
    d=[]
    for data in platesQuerySet:
        temp={}
        temp["id"]= data.pk
        temp["camera_name"]= data.camera_name
        temp["plate"]= data.plate_number
        temp["date"]= data.date.strftime('%d/%m/%Y %H:%M:%S')
        temp["anpr_full_image"]= data.anpr_full_image
        temp["anpr_cropped_image"]= data.anpr_cropped_image
        temp["vehicle_type"] = data.vehicle_type.name
        temp["vehicle_make"] = data.vehicle_make.name
        temp["vehicle_model"] = data.vehicle_model.name
        temp["vehicle_color_name"] = data.vehicle_color.name
        temp["vehicle_color_code"] = data.vehicle_color.code
        d.append(temp)
    # print(d)
    return d

@api_view(['POST' ])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def plate_search(request):
    form_data = request.POST
    # print(form_data)
    try:
        platesQuerySet = getQueryFromFormDatav2(form_data)
        d = getDictFromQuery(platesQuerySet)
        return HttpResponse(json.dumps({
            "count":platesQuerySet.count(),
            "entries":d,
            "filter_conditions": form_data,
        }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})

    except Exception as e:
        print("error--> ",str(e))
        return HttpResponse(json.dumps({"error":str(e)})
            ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})


def createExcelv1(platesQuerySet, start, end):
    path = "/app/rlvd/static/"
    output      = io.BytesIO()
    workbook    = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    headers = ['Entry ID','Plate Number','Camera Name','Date','ANPR Full Image','ANPR Cropped Image']
    bold = workbook.add_format({'bold': True, "font_size": 18, 'align': 'center'})
    center = workbook.add_format({"align": "center", "font_size": 15})
    worksheet.set_row(0,30)
    worksheet.set_default_row(100)
    worksheet.set_column(0, len(headers), 30)
    row = 0
    for idx, head in enumerate(headers):
        worksheet.write(row, idx, head, bold)
    row += 1
    
    for entry in platesQuerySet[start: end]:
        worksheet.write(row, 0, entry.entry_id, center)
        worksheet.write(row, 1, entry.plate_number, center)
        worksheet.write(row, 2, entry.camera_name, center)
        worksheet.write(row, 3, entry.date.strftime('%d/%m/%Y %H:%M:%S'), center)
        imagePath =path+entry.anpr_full_image
        try:
            with Image.open(imagePath) as img:
                width, height = img.size
                x_scale = 30/width
                y_scale = 100/height
                worksheet.insert_image(row, 4,(imagePath), {"x_scale": x_scale*7.2,
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
                                    4,
                                    imagePath,
                                    {"x_scale": x_scale*7.2,
                                        "y_scale": y_scale*1.5,
                                        "positioning": 1})

        imagePath = path+entry.anpr_cropped_image
        try:
            with Image.open(imagePath) as img:
                width, height = img.size
                x_scale = 30/width
                y_scale = 100/height
                worksheet.insert_image(row, 5,imagePath, {"x_scale": x_scale*7.2,
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
                                    5,
                                    imagePath,
                                    {"x_scale": x_scale*7.2,
                                        "y_scale": y_scale*1.5,
                                        "positioning": 1})

        row += 1
    workbook.close()
    return output.getvalue()


def createExcelv2(platesQuerySet, start, end):
    path = "/app/rlvd/static/"
    output      = io.BytesIO()
    workbook    = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    headers = ['Entry ID','Plate Number','Camera Name','Date','ANPR Full Image','ANPR Cropped Image', 'Vehicle Type', 'Vehicle Make', 'Vehicle Model', 'Vehicle Color']
    bold = workbook.add_format({'bold': True, "font_size": 18, 'align': 'center'})
    center = workbook.add_format({"align": "center", "font_size": 15})
    worksheet.set_row(0,30)
    worksheet.set_default_row(100)
    worksheet.set_column(0, len(headers), 30)
    row = 0
    for idx, head in enumerate(headers):
        worksheet.write(row, idx, head, bold)
    row += 1
    
    for entry in platesQuerySet[start: end]:
        worksheet.write(row, 0, entry.entry_id, center)
        worksheet.write(row, 1, entry.plate_number, center)
        worksheet.write(row, 2, entry.camera_name, center)
        worksheet.write(row, 3, entry.date.strftime('%d/%m/%Y %H:%M:%S'), center)
        imagePath =path+entry.anpr_full_image
        try:
            with Image.open(imagePath) as img:
                width, height = img.size
                x_scale = 30/width
                y_scale = 100/height
                worksheet.insert_image(row, 4,(imagePath), {"x_scale": x_scale*7.2,
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
                                    4,
                                    imagePath,
                                    {"x_scale": x_scale*7.2,
                                        "y_scale": y_scale*1.5,
                                        "positioning": 1})

        imagePath = path+entry.anpr_cropped_image
        try:
            with Image.open(imagePath) as img:
                width, height = img.size
                x_scale = 30/width
                y_scale = 100/height
                worksheet.insert_image(row, 5,imagePath, {"x_scale": x_scale*7.2,
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
                                    5,
                                    imagePath,
                                    {"x_scale": x_scale*7.2,
                                        "y_scale": y_scale*1.5,
                                        "positioning": 1})
        worksheet.write(row, 6, entry.vehicle_type.name, center)
        worksheet.write(row, 7, entry.vehicle_make.name, center)
        worksheet.write(row, 8, entry.vehicle_model.name, center)
        worksheet.write(row, 9, entry.vehicle_color.name, center)

        row += 1
    workbook.close()
    return output.getvalue()


def exportExcelToUsbv1(workbook, platesQuerySet):
    path = "/app/rlvd/static/"
    worksheet = workbook.add_worksheet()
    headers = ['Entry ID','Plate Number','Camera Name','Date','ANPR Full Image','ANPR Cropped Image']
    bold = workbook.add_format({'bold': True, "font_size": 18, 'align': 'center'})
    center = workbook.add_format({"align": "center", "font_size": 15})
    worksheet.set_row(0,30)
    worksheet.set_default_row(100)
    worksheet.set_column(0, len(headers), 30)
    row = 0
    for idx, head in enumerate(headers):
        worksheet.write(row, idx, head, bold)
    row += 1
    
    for entry in platesQuerySet:
        worksheet.write(row, 0, entry.entry_id, center)
        worksheet.write(row, 1, entry.plate_number, center)
        worksheet.write(row, 2, entry.camera_name, center)
        worksheet.write(row, 3, entry.date.strftime('%d/%m/%Y %H:%M:%S'), center)
        imagePath =path+entry.anpr_full_image
        try:
            with Image.open(imagePath) as img:
                width, height = img.size
                x_scale = 30/width
                y_scale = 100/height
                worksheet.insert_image(row, 4,(imagePath), {"x_scale": x_scale*7.2,
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
                                    4,
                                    imagePath,
                                    {"x_scale": x_scale*7.2,
                                        "y_scale": y_scale*1.5,
                                        "positioning": 1})

        imagePath = path+entry.anpr_cropped_image
        try:
            with Image.open(imagePath) as img:
                width, height = img.size
                x_scale = 30/width
                y_scale = 100/height
                worksheet.insert_image(row, 5,imagePath, {"x_scale": x_scale*7.2,
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
                                    5,
                                    imagePath,
                                    {"x_scale": x_scale*7.2,
                                        "y_scale": y_scale*1.5,
                                        "positioning": 1})

        row += 1
    workbook.close()


def exportExcelToUsbv2(workbook, platesQuerySet):
    path = "/app/rlvd/static/"
    worksheet = workbook.add_worksheet()
    headers = ['Entry ID','Plate Number','Camera Name','Date','ANPR Full Image','ANPR Cropped Image', 'Vehicle Type', 'Vehicle Make', 'Vehicle Model', 'Vehicle Color']
    bold = workbook.add_format({'bold': True, "font_size": 18, 'align': 'center'})
    center = workbook.add_format({"align": "center", "font_size": 15})
    worksheet.set_row(0,30)
    worksheet.set_default_row(100)
    worksheet.set_column(0, len(headers), 30)
    row = 0
    for idx, head in enumerate(headers):
        worksheet.write(row, idx, head, bold)
    row += 1
    
    for entry in platesQuerySet:
        worksheet.write(row, 0, entry.entry_id, center)
        worksheet.write(row, 1, entry.plate_number, center)
        worksheet.write(row, 2, entry.camera_name, center)
        worksheet.write(row, 3, entry.date.strftime('%d/%m/%Y %H:%M:%S'), center)
        imagePath =path+entry.anpr_full_image
        try:
            with Image.open(imagePath) as img:
                width, height = img.size
                x_scale = 30/width
                y_scale = 100/height
                worksheet.insert_image(row, 4,(imagePath), {"x_scale": x_scale*7.2,
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
                                    4,
                                    imagePath,
                                    {"x_scale": x_scale*7.2,
                                        "y_scale": y_scale*1.5,
                                        "positioning": 1})

        imagePath = path+entry.anpr_cropped_image
        try:
            with Image.open(imagePath) as img:
                width, height = img.size
                x_scale = 30/width
                y_scale = 100/height
                worksheet.insert_image(row, 5,imagePath, {"x_scale": x_scale*7.2,
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
                                    5,
                                    imagePath,
                                    {"x_scale": x_scale*7.2,
                                        "y_scale": y_scale*1.5,
                                        "positioning": 1})
        worksheet.write(row, 6, entry.vehicle_type.name, center)
        worksheet.write(row, 7, entry.vehicle_make.name, center)
        worksheet.write(row, 8, entry.vehicle_model.name, center)
        worksheet.write(row, 9, entry.vehicle_color.name, center)

        row += 1
    workbook.close()



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def getExportDataLengthv1(request):
    form_data = request.POST
    print("form_data", form_data)
    try:
        query = getQueryFromFormDatav1(form_data)
        return HttpResponse(json.dumps({
            "count":query.count(),
            "filter_conditions": form_data,
        }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})
    except Exception as e:
        print("error--> ",e)
        return HttpResponse(json.dumps({"error":str(e)})
            ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def getExportDataLengthv2(request):
    form_data = request.POST
    print("form_data", form_data)
    try:
        query = getQueryFromFormDatav2(form_data)
        return HttpResponse(json.dumps({
            "count":query.count(),
            "filter_conditions": form_data,
        }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})
    except Exception as e:
        print("error--> ",e)
        return HttpResponse(json.dumps({"error":str(e)})
            ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})

def getFilenameForExport(form_data):
    filename = "ANPR"
    start_date_time=form_data["start_date_time"] #can be empty. format: 2021-08-18T07:08  yyyy-mm-ddThh:mm
    end_date_time=form_data["end_date_time"] #can be empty 
    if(start_date_time != '' or end_date_time != ''):
        if(start_date_time != ""):
            start_date_time = datetime.strptime(start_date_time, '%Y-%m-%dT%H:%M')
            start_date_time = start_date_time.strftime('%d/%m/%Y-%H:%M')
            filename += "_" + start_date_time
        else:
            filename += "_-"
        if(end_date_time != ""):
            end_date_time = datetime.strptime(end_date_time, '%Y-%m-%dT%H:%M')
            end_date_time = end_date_time.strftime('%d/%m/%Y-%H:%M')
            filename += "_" + end_date_time
        else:
            filename +="_-"
    filename += ".xlsx"
    return filename

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def exportExcelv1(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format("ANPR entries.xlsx")
    form_data=request.POST
    print("Form Data", form_data)
    try:
        platesQuerySet = getQueryFromFormDatav1(form_data)
        start = int(form_data["start"])  # USED TO SEGMENT THE EXPORT DATA(START OF THE ENTRY - INDEX)
        end = int(form_data["end"])        #USED TO SEGMENT THE EXPORT DATA(END OF THE ENTRY - INDEX)
        xlsx_data = createExcelv1(platesQuerySet, start, end)
        response.write(xlsx_data)
        return response

    except Exception as e:
        print("error--> here",e)
        return HttpResponse(json.dumps({"error":str(e)})
                ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def exportExcelv2(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format("ANPR entries.xlsx")
    form_data=request.POST
    # print("Form Data", form_data)
    try:
        platesQuerySet = getQueryFromFormDatav2(form_data)
        start = int(form_data["start"])  # USED TO SEGMENT THE EXPORT DATA(START OF THE ENTRY - INDEX)
        end = int(form_data["end"])      # USED TO SEGMENT THE EXPORT DATA(END OF THE ENTRY - INDEX)
        xlsx_data = createExcelv2(platesQuerySet, start, end)
        response.write(xlsx_data)
        return response

    except Exception as e:
        print("error--> here",e)
        return HttpResponse(json.dumps({"error":str(e)})
                ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})


                
def gen(camera):
    video = cv2.VideoCapture()
    video.open(camera)
    # video.release()
    # print("streaming live feed of ",camera)
    while True:
        success, frame = video.read()  # read the video frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # print("frame: ", frame)
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def getRemovables(context):
    removables = []
    for device in context.list_devices(subsystem='block', DEVTYPE='disk'):# if device.attributes.asstring('removable') == "1"]
        try:
            device_parent = device.parent.device_path
            if("usb" in device_parent):
                # print(device.sys_name,device.device_type,device.time_since_initialized,device.parent.device_path)#.attributes.asstring('time_since_initialized'))#)
                removables.append(device)
        except Exception as e:
            print("Exception : ",str(e))
            continue   
    print("Removables : ", removables) 
    return removables

    

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def exportToUsbv1(request):
    context = pyudev.Context()
    form_data=request.POST
    platesQuerySet = getQueryFromFormDatav1(form_data)
    filename = getFilenameForExport(form_data)
    removables = getRemovables(context)
    if(removables):
        for device in removables:
            partitions = [device.device_node for device in context.list_devices(subsystem='block', DEVTYPE='partition', parent=device)]
            print("All removable partitions: {}".format(", ".join(partitions)))
            print("Mounted removable partitions:")
            for p in psutil.disk_partitions():
                if p.device in partitions:
                    # print("  {}: {}".format(p.device, p.mountpoint))
                    # print("Excel file saved to",str(p.mountpoint).split('/')[3])
                    # create a new excel and add a worksheet
                    workbook = xlsxwriter.Workbook(str(p.mountpoint)+"/"+ filename, {'remove_timezone': True})
                    exportExcelToUsbv1(workbook, platesQuerySet)
    
        return HttpResponse(json.dumps({"msg": "Data exported successfully"})
                ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"}) 
    else:
        print("Insert USB or Try again")
        return HttpResponseBadRequest(json.dumps({"error": "Insert USB or Try again"})
                ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"}) 



@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def exportToUsbv2(request):
    context = pyudev.Context()
    form_data=request.POST
    platesQuerySet = getQueryFromFormDatav2(form_data)
    filename = getFilenameForExport(form_data)
    removables = getRemovables(context)
    if(removables):
        for device in removables:
            partitions = [device.device_node for device in context.list_devices(subsystem='block', DEVTYPE='partition', parent=device)]
            print("All removable partitions: {}".format(", ".join(partitions)))
            print("Mounted removable partitions:")
            for p in psutil.disk_partitions():
                if p.device in partitions:
                    # print("  {}: {}".format(p.device, p.mountpoint))
                    # print("Excel file saved to",str(p.mountpoint).split('/')[3])
                    # create a new excel and add a worksheet
                    workbook = xlsxwriter.Workbook(str(p.mountpoint)+"/"+ filename, {'remove_timezone': True})
                    exportExcelToUsbv2(workbook, platesQuerySet)
    
        return HttpResponse(json.dumps({"msg": "Data exported successfully"})
                ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"}) 
    else:
        print("Insert USB or Try again")
        return HttpResponseBadRequest(json.dumps({"error": "Insert USB or Try again"})
                ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})

    

@api_view(['GET'])
@permission_classes([])
@authentication_classes([])
def camerafeed(request): 
        #should get rtsp url from request
    camid = request.GET.get("camid")
    rtsp = AnprCamera.objects.filter(id=camid).first().rtsp_url
    # print("Rtsp  ---->  ", rtsp)
    return StreamingHttpResponse(gen(rtsp),content_type="multipart/x-mixed-replace;boundary=frame")



def debug(request):
    entriesQuerySet = LicensePlates.objects.filter(camera_name = "cam1").select_related('vehicle_type').select_related('vehicle_make').select_related('vehicle_model').select_related('vehicle_color').order_by('-entry_id')[:5]
    recognitionCount = LicensePlates.objects.filter(camera_name = "cam1").count()

    d=[]
    for data in entriesQuerySet:
        print(data.camera_name)
        # temp={}
        # temp["id"]= data.pk
        # temp["camera_name"]= data.camera_name
        # # temp["junction_name"]= e.junction_name
        # temp["plate"]= data.plate_number
        # temp["date"]= data.date.strftime('%d/%m/%Y %H:%M:%S')
        # temp["anpr_full_image"]= data.anpr_full_image
        # temp["anpr_cropped_image"]= data.anpr_cropped_image
        # temp["vehicle_type"] = data.vehicle_type.name
        # temp["vehicle_make"] = data.vehicle_make.name
        # temp["vehicle_model"] = data.vehicle_model.name
        # temp["vehicle_color"] = data.vehicle_color.name
        # d.append(temp)
    print(d)
    return render(request, 'index.html')




    # def download_csv( request, array):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment;filename=export.csv'
#     writer = csv.writer(response)
#     head=['entry_id','plate_number','camera_name','date','anpr_full_image','anpr_cropped_image']

#     # writer.writerow(field_names)
#     writer.writerow(head)
#     # writer.writerow(body)
#     # Write data rows
#     # array= [['a','b'],['c','d']]
#     for row in array:
#         writer.writerow(row)
#     return response

# # @csrf_exempt

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
# def export_csv(request):
#     form_data=request.POST
#     print("Form Data", form_data)
#     try:
#         vehicle_no= form_data["vehicle_number"] #can be empty 
#         cameras = form_data["camera_names"] #can be empty
#         start_date_time=form_data["start_date_time"] #can be empty. format: 2021-08-18T07:08  yyyy-mm-ddThh:mm
#         end_date_time=form_data["end_date_time"]
#         # vehicle_no = ""
#         # cameras = ""
#         # start_date_time = ""
#         # end_date_time = ""

#         plates=LicensePlates.objects.all()
#         if cameras!="":
#             cameras=cameras.split(',')
            

#         print("Vehicle NO: ", vehicle_no, "Cameras", cameras)
#         if vehicle_no!="":
#             plates = LicensePlates.objects.filter(plate_number__contains=vehicle_no)
#         if len(cameras)>0:
#             plates =plates.filter(camera_name__in=cameras)
#         if start_date_time!="":
#             plates=plates.filter(date__gte=start_date_time)
#         if end_date_time!="":
#             plates=plates.filter(date__lte=end_date_time)

#         d=[]
#         for e in plates:
#             temp=[]
#             temp.append(e.entry_id)
#             temp.append(e.plate_number)
#             temp.append(e.camera_name)
#             temp.append(e.date.strftime('%d/%m/%Y %H:%M:%S'))
#             temp.append(HOST_STATIC_FOLDER_URL + e.anpr_full_image)
#             temp.append(HOST_STATIC_FOLDER_URL + e.anpr_cropped_image)
#             d.append(temp)

#         # print("CSV Data", d)
#         data = download_csv( request, d)
#         return HttpResponse (data, content_type='text/csv')
#     except Exception as e:

#         print("Exxception --> ",e)
#         return HttpResponse("error")