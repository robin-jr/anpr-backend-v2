from django.views.decorators.csrf import csrf_exempt
from .models import LicensePlatesAnpr as LicensePlates
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
import json




# @api_view(['GET'])
def say_hello(request):
    return HttpResponse("Hello")


@csrf_exempt
# @api_view(['GET', ])
@api_view(['POST', 'GET' ])
# @permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
@permission_classes([])
@authentication_classes([])
def plate_search(request):

    if request.method == "POST" or request.method == "GET" :
        # form_data = request.POST
        # print("form_data", form_data)

        try:
            # vehicle_no= form_data["vehicle_number"] #can be empty 
            # cameras = form_data["camera_names"] #can be empty
            # # junction_names =form_data["junction_names"] #can be empty
            # start_date_time=form_data["start_date_time"] #can be empty. format: 2021-08-18T07:08  yyyy-mm-ddThh:mm
            # end_date_time=form_data["end_date_time"] #can be empty 

            # if cameras!="":
            #     cameras=cameras.split(',')
            # if junction_names!="":
            #     junction_names=junction_names.split(',')
            
            ## for now
            # vehicle_no= ""
            # cameras = ["No2_Nathamuni"]
            # # junction_names =["Sathya Showroom"]
            # start_date_time="2020-01-01T00:00"
            # end_date_time="2020-01-01T23:00"
            vehicle_no= ""
            cameras = []
            junction_names =[]
            start_date_time=""
            end_date_time=""

            plates=LicensePlates.objects.all()
            if vehicle_no!="":
                plates = LicensePlates.objects.filter(plate_number__contains=vehicle_no)
            if len(cameras)>0:
                plates =plates.filter(camera_name__in=cameras)
            # if len(junction_names)>0:
            #     plates=plates.filter(junction_name__in=junction_names)
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
                # "filter_conditions": form_data,
            }),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})

        except Exception as e:
            print("error--> ",e)
            return HttpResponse(json.dumps({"error":str(e)})
                ,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})
    else:
        logging.info("Plate Search - End")
        return HttpResponseBadRequest("Bad Request!",headers={"Access-Control-Allow-Origin":"*"})


