from arima_backend_v2.settings import STATIC_ROOT, STATIC_URL
# from rlvd.views import HOST_STATIC_FOLDER_URL
from .models import LicensePlatesAnpr as LicensePlates, VehicleColorRef, VehicleModelRef, VehicleMakeRef, VehicleTypeRef
from rlvd.models import AnprCamera
import math
import logging
import io
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, response
from django.shortcuts import render
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from datetime import datetime
from subprocess import Popen
import xlsxwriter
import pyudev
import psutil

import json

django_dir = "/app/" # Directory containing Django manage.py
imageLocation = "/home/user/.webapp/ARIMA-Image-Server/images/"   # Directory containing the images
liveFeedServer = "/home/user/.webapp/anpr-backend-v2/anpr/mjpg_serve.py"  # Directory containing the python server for live

# returns the list of cameras available in the database 
def getCameras():
    camQuerySet = AnprCamera.objects.only('id', 'camera_name', 'latitude', 'longitude', 'rtsp_url', 'http_port')
    cams = []
    for cam in camQuerySet:
        temp = {}
        temp["id"] = cam.id
        temp["name"] = cam.camera_name
        temp["latitude"] = str(cam.latitude)
        temp["longitude"] = str(cam.longitude)
        temp["rtsp_url"] = cam.rtsp_url
        temp["http_port"] = cam.http_port
        cams.append(temp)

    return cams

# returns the list of vechile types from the database
def getVehicleTypes():
    typesQuerySet = VehicleTypeRef.objects.all()
    types = []
    for type in typesQuerySet:
        temp = {}
        temp["id"] = type.pk
        temp["name"] = type.name
        types.append(temp)

    return types


# returns the list of vechile types from the database
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

# returns the list of vechile models from the database
def getVehicleModels():
    modelsQuerySet = VehicleModelRef.objects.select_related('type').select_related('make').all()
    models = []
    for model in modelsQuerySet:
        temp = {}
        temp['id'] = model.pk
        temp['name'] = model.name
        temp['make'] = model.make.id
        temp['type'] = model.type.id
        models.append(temp)
    return models

# returns the list of vechile colors from the database
def getVehicleColors():
    colorsQuerySet = VehicleColorRef.objects.all()
    colors = []
    for color in colorsQuerySet:
        temp = {}
        temp['id'] = color.pk
        temp['name'] = color.name
        temp['code'] = color.code
        colors.append(temp)
    return colors
    
# get the recognition count of a cameara.
def getRecognitionCountOfCamera(camera_name):
    count = LicensePlates.objects.filter(camera_name = camera_name).count()
    return count

# get the latest 5 entries of a camera
def getLatestEntriesOfCamera(camera_name):
    plateQuerySet = LicensePlates.objects.filter(camera_name = camera_name).select_related('vehicle_type').select_related('vehicle_make').select_related('vehicle_model').select_related('vehicle_color').order_by('-entry_id')[:5]
    entries = []
    for data in plateQuerySet:
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
        entries.append(temp)
    return entries



# returns the initial data to the client like cameras, vehicle type, vehicle model, vehicle colors.
# in addition to that it also sends the recongition count of the first camera and also the latest 5 entries of the camera for displaying in the database.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def initialData(request):
    try:
        cameras = getCameras()
        vehicleTypes = getVehicleTypes()
        vehicleMakes = getVehicleMakes()
        vehicleModels = getVehicleModels()
        vehicleColors = getVehicleColors()
        recognitionCount = getRecognitionCountOfCamera(cameras[0]["name"])
        entries = getLatestEntriesOfCamera(cameras[0]['name'])
        
        return HttpResponse(json.dumps({
                    "cameras":json.dumps(cameras),
                    "vehicle_types": json.dumps(vehicleTypes),
                    "vehicle_makes": json.dumps(vehicleMakes),
                    "vehicle_models": json.dumps(vehicleModels),
                    "vehicle_colors": json.dumps(vehicleColors),
                    "count":recognitionCount,
                    "entries":json.dumps(entries), 
                }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})
    
    except Exception as e:
        print("error--> ",str(e))
        return HttpResponse(json.dumps({"error":str(e)})
            ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})


# returns the total count and latest recognition of the camera
# camera name is recieved from the client
# this gets called every 5 seconds from the client for realtime data updation in the live screen page.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def getCameraLatestEntriesAndRecognitions(request):
    if request.method == "POST":
        try:
            form_data = request.POST
            camera_name = form_data["camera_name"]
            recognitionCount = LicensePlates.objects.filter(camera_name = camera_name).count()
            plateQuerySet = LicensePlates.objects.filter(camera_name = camera_name).select_related('vehicle_type').select_related('vehicle_make').select_related('vehicle_model').select_related('vehicle_color').order_by('-entry_id')[:5]
            entries = []
            for data in plateQuerySet:
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
                entries.append(temp)
            return HttpResponse(json.dumps({
                        "count":recognitionCount,
                        "entries":json.dumps(entries),
                        "filter_conditions": form_data,
                    }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})
        except Exception as e:
            print("error--> ",str(e))
            return HttpResponse(json.dumps({"error":str(e)})
                ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})
    else:
        logging.info("Latest Entries - End")
        return HttpResponseBadRequest("Bad Request!",headers={"Access-Control-Allow-Origin":"*"})

# this is used to return a queryset from the form_data sent from the client
# this is for version1
def getQueryFromFormDatav1(form_data):
    vehicle_no= form_data["vehicle_number"] #can be empty 
    cameras = form_data["camera_names"] #can be empty
    start_date_time=form_data["start_date_time"] #can be empty. format: 2021-08-18T07:08  yyyy-mm-ddThh:mm
    end_date_time=form_data["end_date_time"] #can be empty 
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

# this is used to return a queryset from the form_data sent from the client
# this is for version2
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

# retrive the data from the database and stores it in a list of dictionaries
# return the list of dictionay.
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
    return d

# this endpoint gets called during the search.
# gets the page number and number of entries from the client for paginated data
# return the paginated data and the count of total entries(all entries from the database) for further pagination.
@api_view(['POST' ])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def plate_search(request):
    form_data = request.POST
    try:
        platesQuerySet = getQueryFromFormDatav2(form_data)
        page = int(form_data["page"])
        count = int(form_data["count"])
        d = getDictFromQuery(platesQuerySet[(page) * count : (page+1) * count])
        return HttpResponse(json.dumps({
            "count":platesQuerySet.count(),
            "entries":d,
            "filter_conditions": form_data,
        }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})

    except Exception as e:
        print("error--> ",str(e))
        return HttpResponse(json.dumps({"error":str(e)})
            ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})


# create and return an excel sheet, populated with data.
# for Version 1
def createExcelv1(platesQuerySet, start, end):
    output      = io.BytesIO()
    workbook    = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    headers = ['S.No','Plate Number','Camera Name','Date','ANPR Full Image','ANPR Cropped Image']
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
        worksheet.write(row, 0, row+start, center)
        worksheet.write(row, 1, entry.plate_number, center)
        worksheet.write(row, 2, entry.camera_name, center)
        worksheet.write(row, 3, entry.date.strftime('%d/%m/%Y %H:%M:%S'), center)
        imagePath =imageLocation+entry.anpr_full_image
        try:
            with Image.open(imagePath) as img:
                width, height = img.size
                x_scale = 30/width
                y_scale = 100/height
                worksheet.insert_image(row, 4,(imagePath), {"x_scale": x_scale*7.2,
                                                    "y_scale": y_scale*1.5,
                                                    "positioning": 1})
        except Exception as e:
            imagePath = imageLocation+"noImage.jpg"
            with Image.open(imagePath) as img:
                img_width, img_height = img.size
                x_scale = 30/img_width
                y_scale = 100/img_height
                worksheet.insert_image(row,
                                    4,
                                    imagePath,
                                    {"x_scale": x_scale*7.2,
                                        "y_scale": y_scale*1.5,
                                        "positioning": 1})

        imagePath = imageLocation+entry.anpr_cropped_image
        try:
            with Image.open(imagePath) as img:
                width, height = img.size
                x_scale = 30/width
                y_scale = 100/height
                worksheet.insert_image(row, 5,imagePath, {"x_scale": x_scale*7.2,
                                                    "y_scale": y_scale*1.5,
                                                    "positioning": 1})
        except Exception as e:
            imagePath = imageLocation+"noImage.jpg"
            with Image.open(imagePath) as img:
                img_width, img_height = img.size
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

# create and return an excel sheet, populated with data.
# for Version 2
def createExcelv2(platesQuerySet, start, end):
    output      = io.BytesIO()
    workbook    = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    headers = ['S.No','Plate Number','Camera Name','Date','ANPR Full Image','ANPR Cropped Image', 'Vehicle Type', 'Vehicle Make', 'Vehicle Model', 'Vehicle Color']
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
        worksheet.write(row, 0, row+start, center)
        worksheet.write(row, 1, entry.plate_number, center)
        worksheet.write(row, 2, entry.camera_name, center)
        worksheet.write(row, 3, entry.date.strftime('%d/%m/%Y %H:%M:%S'), center)
        imagePath =imageLocation+entry.anpr_full_image
        try:
            with Image.open(imagePath) as img:
                width, height = img.size
                x_scale = 30/width
                y_scale = 100/height
                worksheet.insert_image(row, 4,(imagePath), {"x_scale": x_scale*7.2,
                                                    "y_scale": y_scale*1.5,
                                                    "positioning": 1})
        except Exception as e:
            imagePath = imageLocation+"noImage.jpg"
            with Image.open(imagePath) as img:
                img_width, img_height = img.size
                x_scale = 30/img_width
                y_scale = 100/img_height
                worksheet.insert_image(row,
                                    4,
                                    imagePath,
                                    {"x_scale": x_scale*7.2,
                                        "y_scale": y_scale*1.5,
                                        "positioning": 1})

        imagePath = imageLocation+entry.anpr_cropped_image
        try:
            with Image.open(imagePath) as img:
                width, height = img.size
                x_scale = 30/width
                y_scale = 100/height
                worksheet.insert_image(row, 5,imagePath, {"x_scale": x_scale*7.2,
                                                    "y_scale": y_scale*1.5,
                                                    "positioning": 1})
        except Exception as e:
            imagePath = imageLocation+"noImage.jpg"
            with Image.open(imagePath) as img:
                img_width, img_height = img.size
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
        print(row)
        row += 1
    workbook.close()
    return output.getvalue()

# create the excel file in the usb and store the data.
# for version 1
def exportExcelToUsbv1(platesQuerySet, filename):
    entriesPerFile = 1000
    totalEntries = platesQuerySet.count()
    # segment the total entries in 1000's and stored them in seperate file
    # used this since export is taking much time segment the total entries in 1000's and stored them in seperate file
    # used this since export is taking much time
    exportSegments = math.ceil(totalEntries/entriesPerFile)
    
    for segement in range(exportSegments):
        tempFilename = filename + "-" + str(segement+1)+".xlsx"
        workbook = xlsxwriter.Workbook(tempFilename, {'remove_timezone': True})
        worksheet = workbook.add_worksheet()
        headers = ['S.No','Plate Number','Camera Name','Date','ANPR Full Image','ANPR Cropped Image']
        bold = workbook.add_format({'bold': True, "font_size": 18, 'align': 'center'})
        center = workbook.add_format({"align": "center", "font_size": 15})
        worksheet.set_row(0,30)
        worksheet.set_default_row(100)
        worksheet.set_column(0, len(headers), 30)
        row = 0
        for idx, head in enumerate(headers):
            worksheet.write(row, idx, head, bold)
        row += 1
        start = segement * entriesPerFile
        end = segement * entriesPerFile + entriesPerFile
        for entry in platesQuerySet[start: end]:
            worksheet.write(row, 0, start + row, center)
            worksheet.write(row, 1, entry.plate_number, center)
            worksheet.write(row, 2, entry.camera_name, center)
            worksheet.write(row, 3, entry.date.strftime('%d/%m/%Y %H:%M:%S'), center)
            imagePath =imageLocation+entry.anpr_full_image
            try:
                with Image.open(imagePath) as img:
                    width, height = img.size
                    x_scale = 30/width
                    y_scale = 100/height
                    worksheet.insert_image(row, 4,(imagePath), {"x_scale": x_scale*7.2,
                                                        "y_scale": y_scale*1.5,
                                                        "positioning": 1})
            except Exception as e:
                imagePath = imageLocation+"noImage.jpg"
                with Image.open(imagePath) as img:
                    img_width, img_height = img.size
                    x_scale = 30/img_width
                    y_scale = 100/img_height
                    worksheet.insert_image(row,
                                        4,
                                        imagePath,
                                        {"x_scale": x_scale*7.2,
                                            "y_scale": y_scale*1.5,
                                            "positioning": 1})

            imagePath = imageLocation+entry.anpr_cropped_image
            try:
                with Image.open(imagePath) as img:
                    width, height = img.size
                    x_scale = 30/width
                    y_scale = 100/height
                    worksheet.insert_image(row, 5,imagePath, {"x_scale": x_scale*7.2,
                                                        "y_scale": y_scale*1.5,
                                                        "positioning": 1})
            except Exception as e:
                imagePath = imageLocation+"noImage.jpg"
                with Image.open(imagePath) as img:
                    img_width, img_height = img.size
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

# create the excel file in the usb and store the data.
# for version 2
def exportExcelToUsbv2(platesQuerySet, filename):
    entriesPerFile = 1000
    totalEntries = platesQuerySet.count()

    # segment the total entries in 1000's and stored them in seperate file
    # used this since export is taking much time
    exportSegments = math.ceil(totalEntries/entriesPerFile)
    for segement in range(exportSegments):
        tempFilename = filename + "-" + str(segement+1)+".xlsx"
        workbook = xlsxwriter.Workbook(tempFilename, {'remove_timezone': True})
        worksheet = workbook.add_worksheet()
        headers = ['S.No','Plate Number','Camera Name','Date','ANPR Full Image','ANPR Cropped Image', 'Vehicle Type', 'Vehicle Make', 'Vehicle Model', 'Vehicle Color']
        bold = workbook.add_format({'bold': True, "font_size": 18, 'align': 'center'})
        center = workbook.add_format({"align": "center", "font_size": 15})
        worksheet.set_row(0,30)
        worksheet.set_default_row(100)
        worksheet.set_column(0, len(headers), 30)
        row = 0
        for idx, head in enumerate(headers):
            worksheet.write(row, idx, head, bold)
        row += 1

        start = segement * entriesPerFile
        end = segement * entriesPerFile + entriesPerFile
        
        for entry in platesQuerySet[start: end]:
            worksheet.write(row, 0, start + row, center)
            worksheet.write(row, 1, entry.plate_number, center)
            worksheet.write(row, 2, entry.camera_name, center)
            worksheet.write(row, 3, entry.date.strftime('%d/%m/%Y %H:%M:%S'), center)
            imagePath =imageLocation+entry.anpr_full_image
            try:
                with Image.open(imagePath) as img:
                    width, height = img.size
                    x_scale = 30/width
                    y_scale = 100/height
                    worksheet.insert_image(row, 4,(imagePath), {"x_scale": x_scale*7.2,
                                                        "y_scale": y_scale*1.5,
                                                        "positioning": 1})
            except Exception as e:
                imagePath = imageLocation+"noImage.jpg"
                with Image.open(imagePath) as img:
                    img_width, img_height = img.size
                    x_scale = 30/img_width
                    y_scale = 100/img_height
                    worksheet.insert_image(row,
                                        4,
                                        imagePath,
                                        {"x_scale": x_scale*7.2,
                                            "y_scale": y_scale*1.5,
                                            "positioning": 1})

            imagePath = imageLocation+entry.anpr_cropped_image
            try:
                with Image.open(imagePath) as img:
                    width, height = img.size
                    x_scale = 30/width
                    y_scale = 100/height
                    worksheet.insert_image(row, 5,imagePath, {"x_scale": x_scale*7.2,
                                                        "y_scale": y_scale*1.5,
                                                        "positioning": 1})
            except Exception as e:
                imagePath = imageLocation+"noImage.jpg"
                with Image.open(imagePath) as img:
                    img_width, img_height = img.size
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

# return the length of total entries with the search conditions. 
# used for pagination in the export.
# for version 1
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def getExportDataLengthv1(request):
    form_data = request.POST
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



# return the length of total entries with the search conditions. 
# used for pagination in the export.
# for version 2
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def getExportDataLengthv2(request):
    form_data = request.POST
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

# return the filename for export using some constrains.
def getFilenameForExport(form_data):
    filename = "ANPR"
    start_date_time=form_data["start_date_time"] #can be empty. format: 2021-08-18T07:08  yyyy-mm-ddThh:mm
    end_date_time=form_data["end_date_time"] #can be empty 
    if(start_date_time != '' or end_date_time != ''):
        if(start_date_time != ""):
            start_date_time = datetime.strptime(start_date_time, '%Y-%m-%dT%H:%M')
            start_date_time = start_date_time.strftime('%d.%m.%Y-%H.%M')
            filename += "_" + start_date_time
        else:
            filename += "_-"
        if(end_date_time != ""):
            end_date_time = datetime.strptime(end_date_time, '%Y-%m-%dT%H:%M')
            end_date_time = end_date_time.strftime('%d.%m.%Y-%H.%M')
            filename += "_" + end_date_time
        else:
            filename +="_-"
    
    return filename

# return the export data to the client
# for version 1
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def exportExcelv1(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format("ANPR entries.xlsx")
    form_data=request.POST
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


# return the export data to the client.
# for version 2.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def exportExcelv2(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format("ANPR entries.xlsx")
    form_data=request.POST
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

# return the list of pendirves connected to the system.
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
    # print("Removables : ", removables) 
    return removables

    
# export the data directly to the usb
# for version 1
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
            for p in psutil.disk_partitions():
                if p.device in partitions:
                    exportExcelToUsbv1(platesQuerySet, str(p.mountpoint)+"/"+ filename)
    
        return HttpResponse(json.dumps({"msg": "Data exported successfully"})
                ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"}) 
    else:
        print("Insert USB or Try again")
        return HttpResponseBadRequest(json.dumps({"error": "Insert USB or Try again"})
                ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"}) 


# export the data directly to the usb
# for version 2.
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
            for p in psutil.disk_partitions():
                if p.device in partitions:
                    exportExcelToUsbv2(platesQuerySet,str(p.mountpoint)+"/"+ filename)
    
        return HttpResponse(json.dumps({"msg": "Data exported successfully"})
                ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"}) 
    else:
        print("Insert USB or Try again")
        return HttpResponseBadRequest(json.dumps({"error": "Insert USB or Try again"})
                ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})


# start a new live feed server.
@api_view(['GET'])
@permission_classes([])
@authentication_classes([])
def camerafeed(request): 
    camid = request.GET.get("camid")
    #camid = 1
    rtsp = AnprCamera.objects.filter(id=camid).first().rtsp_url
    try:
        pid = Popen(['python', liveFeedServer, rtsp])
        print("success")
        return HttpResponse("Success")
    except Exception as e:
        print("Exception: ", str(e))
        return HttpResponse("Error")