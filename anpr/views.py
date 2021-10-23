from arima_backend_v2.settings import STATIC_ROOT, STATIC_URL
from rlvd.views import HOST_STATIC_FOLDER_URL
from .models import LicensePlatesAnpr as LicensePlates
from rlvd.models import AnprCamera
import csv
import logging
import io
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, response

from rest_framework.decorators import api_view,authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
import cv2
import xlsxwriter
from django.http import StreamingHttpResponse

import json

def createExcel(entries):
    path = "/app/rlvd/static/"
    output      = io.BytesIO()
    workbook    = xlsxwriter.Workbook(output)
    # workbook = xlsxwriter.Workbook(name)
    worksheet = workbook.add_worksheet()
    # worksheet.row_dimensions[1].height = 70
    bold = workbook.add_format({'bold': True, "font_size": 18, 'align': 'center'})
    worksheet.set_row(0,30)
    headers = ['Entry ID','Plate Number','Camera Name','Date','ANPR Full Image','ANPR Cropped Image']
    row = 0
    for idx, head in enumerate(headers):
        worksheet.write(row, idx, head, bold)
    row += 1
    worksheet.set_default_row(100)
    worksheet.set_column(0, len(entries), 30)
    center = workbook.add_format({"align": "center", "font_size": 15})
    for entry in entries:
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
                print(worksheet.insert_image(row,
                                    4,
                                    imagePath,
                                    {"x_scale": x_scale*7.2,
                                        "y_scale": y_scale*1.5,
                                        "positioning": 1}))

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
                print(worksheet.insert_image(row,
                                    5,
                                    imagePath,
                                    {"x_scale": x_scale*7.2,
                                        "y_scale": y_scale*1.5,
                                        "positioning": 1}))
        row += 1
    workbook.close()
    return output.getvalue()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def exportExcel(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format("ANPR entries.xlsx")
    form_data=request.POST
    print("Form Data", form_data)
    try:
        vehicle_no= form_data["vehicle_number"] #can be empty 
        cameras = form_data["camera_names"] #can be empty
        start_date_time=form_data["start_date_time"] #can be empty. format: 2021-08-18T07:08  yyyy-mm-ddThh:mm
        end_date_time=form_data["end_date_time"]
        # vehicle_no = ""
        # cameras = ""
        # start_date_time = ""
        # end_date_time = ""

        plates=LicensePlates.objects.all()
        if cameras!="":
            cameras=cameras.split(',')
            

        print("Vehicle NO: ", vehicle_no, "Cameras", cameras)
        if vehicle_no!="":
            plates = LicensePlates.objects.filter(plate_number__contains=vehicle_no)
        if len(cameras)>0:
            plates =plates.filter(camera_name__in=cameras)
        if start_date_time!="":
            plates=plates.filter(date__gte=start_date_time)
        if end_date_time!="":
            plates=plates.filter(date__lte=end_date_time)

        xlsx_data = createExcel(plates)
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
        print("streaming live feed of ",camera)
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

@api_view(['GET'])
@permission_classes([])
@authentication_classes([])
def camerafeed(request): 
        #should get rtsp url from request
    camid = request.GET.get("camid")
    rtsp = AnprCamera.objects.filter(id=camid).first().rtsp_url
    print("Rtsp  ---->  ", rtsp)
    return StreamingHttpResponse(gen(rtsp),content_type="multipart/x-mixed-replace;boundary=frame")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def initialDatas(request):
    camQuerySet = AnprCamera.objects.only('id', 'camera_name', 'latitude', 'longitude', 'rtsp_url')
    cams = []
    for cam in camQuerySet:
        temp = {}
        temp["id"] = cam.id
        temp["camera_name"] = cam.camera_name
        temp["latitude"] = str(cam.latitude)
        temp["longitude"] = str(cam.longitude)
        temp["rtsp_url"] = cam.rtsp_url
        cams.append(temp)
    return HttpResponse(json.dumps({
                "count":len(cams),
                "cameras":json.dumps(cams),
                # "filter_conditions": form_data,
            }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def getCameraLatestEntriesAndRecognitions(request):
    if request.method == "POST":
        form_data = request.POST
        print("form_data", form_data)
        camera_name = form_data["camera_name"]
        recognitionCount = LicensePlates.objects.filter(camera_name = camera_name).count()
        entriesQuerySet = LicensePlates.objects.only('entry_id', 'camera_name', 'plate_number', 'date', 'anpr_full_image', 'anpr_cropped_image').filter(camera_name = camera_name).order_by('-entry_id')[:5]
        entries = []
        for entry in entriesQuerySet:
            temp = {}
            temp["id"] = entry.entry_id
            temp["camera_name"] = entry.camera_name
            temp["plate"] = entry.plate_number
            temp["date"] = entry.date.strftime('%d/%m/%Y %H:%M:%S')
            temp["anpr_full_image"] = entry.anpr_full_image
            temp["anpr_cropped_image"] = entry.anpr_cropped_image
            entries.append(temp)
        return HttpResponse(json.dumps({
                    "count":recognitionCount,
                    "entries":json.dumps(entries),
                    "filter_conditions": form_data,
                }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})
    else:
        logging.info("Latest Entries - End")
        return HttpResponseBadRequest("Bad Request!",headers={"Access-Control-Allow-Origin":"*"})


# @csrf_exempt
@api_view(['POST' ])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def plate_search(request):

    if request.method == "POST":
        form_data = request.POST
        print("form_data", form_data)

        try:
            vehicle_no= form_data["vehicle_number"] #can be empty 
            cameras = form_data["camera_names"] #can be empty
            start_date_time=form_data["start_date_time"] #can be empty. format: 2021-08-18T07:08  yyyy-mm-ddThh:mm
            end_date_time=form_data["end_date_time"] #can be empty 

            if cameras!="":
                cameras=cameras.split(',')

            plates=LicensePlates.objects.all()
            if vehicle_no!="":
                plates = LicensePlates.objects.filter(plate_number__contains=vehicle_no)
            if len(cameras)>0:
                plates =plates.filter(camera_name__in=cameras)
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
                # temp["junction_name"]= e.junction_name
                temp["plate"]= e.plate_number
                temp["date"]= e.date.strftime('%d/%m/%Y %H:%M:%S')
                temp["anpr_full_image"]= e.anpr_full_image
                temp["anpr_cropped_image"]= e.anpr_cropped_image
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
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=export.csv'
    writer = csv.writer(response)
    head=['entry_id','plate_number','camera_name','date','anpr_full_image','anpr_cropped_image']

    # writer.writerow(field_names)
    writer.writerow(head)
    # writer.writerow(body)
    # Write data rows
    # array= [['a','b'],['c','d']]
    for row in array:
        writer.writerow(row)
    return response

# @csrf_exempt

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def export_csv(request):
    form_data=request.POST
    print("Form Data", form_data)
    try:
        vehicle_no= form_data["vehicle_number"] #can be empty 
        cameras = form_data["camera_names"] #can be empty
        start_date_time=form_data["start_date_time"] #can be empty. format: 2021-08-18T07:08  yyyy-mm-ddThh:mm
        end_date_time=form_data["end_date_time"]
        # vehicle_no = ""
        # cameras = ""
        # start_date_time = ""
        # end_date_time = ""

        plates=LicensePlates.objects.all()
        if cameras!="":
            cameras=cameras.split(',')
            

        print("Vehicle NO: ", vehicle_no, "Cameras", cameras)
        if vehicle_no!="":
            plates = LicensePlates.objects.filter(plate_number__contains=vehicle_no)
        if len(cameras)>0:
            plates =plates.filter(camera_name__in=cameras)
        if start_date_time!="":
            plates=plates.filter(date__gte=start_date_time)
        if end_date_time!="":
            plates=plates.filter(date__lte=end_date_time)

        d=[]
        for e in plates:
            temp=[]
            temp.append(e.entry_id)
            temp.append(e.plate_number)
            temp.append(e.camera_name)
            temp.append(e.date.strftime('%d/%m/%Y %H:%M:%S'))
            temp.append(HOST_STATIC_FOLDER_URL + e.anpr_full_image)
            temp.append(HOST_STATIC_FOLDER_URL + e.anpr_cropped_image)
            d.append(temp)

        # print("CSV Data", d)
        data = download_csv( request, d)
        return HttpResponse (data, content_type='text/csv')
    except Exception as e:

        print("Exxception --> ",e)
        return HttpResponse("error")