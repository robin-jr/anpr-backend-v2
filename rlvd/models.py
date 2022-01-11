from django.db import models
from django.utils import timezone


class LicensePlatesRlvd(models.Model):
    entry_id = models.AutoField(primary_key=True)
    # object_id=models.CharField(max_length=100)
    camera_name = models.CharField(max_length=100)
    junction_name = models.CharField(max_length=100)
    evidence_camera_name = models.CharField(max_length=100)
    number_plate_number = models.CharField(max_length=50)
    date = models.DateTimeField()
    anpr_image = models.CharField(max_length=200)
    cropped_image = models.CharField(max_length=200)
    evidence_images=models.CharField(max_length=1000)
    violations=models.CharField(max_length=100)
    speed=models.DecimalField(max_digits=5,decimal_places=2)
    speed_limit=models.DecimalField(max_digits=5,decimal_places=2)
    reviewed=models.BooleanField()

    class Meta:
        #managed = True
        db_table = "license_plates_rlvd"

    def str(self):
        return self.number_plate_number

# class EvidenceCamImg(models.Model):
    # id = models.AutoField(primary_key=True)
    # # entry = models.ForeignKey(LicensePlatesRlvd, on_delete=models.CASCADE)
    # object_id = models.CharField(max_length=100)
    # evidence_image = models.CharField(max_length=100)

    # class Meta:
    #     db_table = 'evidence_cam_img'
    # def str(self):
    #     return self.evidence_image


class ViolationRef(models.Model):
    id = models.AutoField(primary_key=True)
    violation_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'violation_ref'
    def str(self):
        return self.violation_name


# class Violation(models.Model):
#     id = models.AutoField(primary_key=True)
#     # entry = models.ForeignKey(LicensePlatesRlvd, on_delete=models.CASCADE)
#     violation = models.ForeignKey(ViolationRef,on_delete=models.CASCADE)
#     # entry = models.ForeignKey(LicensePlatesRlvd, on_delete=models.CASCADE)
#     object_id = models.CharField(max_length=100)

#     class Meta:
#         db_table = 'violations'
#     def str(self):
#         return self.violation



class AnprCamera(models.Model):
    id = models.AutoField(primary_key=True)
    camera_name = models.CharField(max_length=100, help_text="Name of the Camera. AVOID SPACES IN THE NAME.")
    latitude = models.DecimalField(max_digits=10, decimal_places=7, help_text="Latitude of the Camera Location.")
    longitude = models.DecimalField(max_digits=10, decimal_places=7, help_text="Longitude of the Camera Location.")
    rtsp_url = models.CharField(max_length=400, help_text="Functioning RTSP link(rtsp://localhost:8554/ds-test) or Path to Local Video(/home/user/vid.mp4). AVOID SPACES IN THE NAME.")
    http_port = models.IntegerField()
    junction_name = models.CharField(max_length=400)
    evidence_camera_name = models.CharField(max_length=400)
    plate_model = models.CharField(max_length=100, default = "T20-FP16",help_text="Name of the Plate Model. Refer to Accuracy Benchmarking Sheet if needed.")
    char_model = models.CharField(max_length=100, default = "chars-ssd",help_text="Name of the Chars Model. Refer to Accuracy Benchmarking Sheet if needed.")
    char_model_width = models.IntegerField(default = 304, help_text="Width of the Input to Char Model. Refer to Chars Training Documentation.")
    char_model_height = models.IntegerField(default = 192, help_text="Heigth of the Input to Char Model. Refer to Chars Training Documentation.")
    vid_width = models.IntegerField(default = 1920, help_text="Width of the Video Resolution.")
    vid_height = models.IntegerField(default = 1080, help_text="Heigth of the Video Resolution.")

    char_det_model = models.CharField(max_length=100, default = "CD2-FP32",help_text="Path to an .xml file with char detection model alone. Refer to Accuracy Benchmarking Sheet if needed.")
    char_recog_model = models.CharField(max_length=100, default = "CR1",help_text="Path to an .h5 and .json file with char recognition model alone. Refer to Accuracy Benchmarking Sheet if needed.")
    char_split = models.BooleanField(default=False, help_text="Tick to turn it on. Enables char model split into detection and recognition")


    plate_threshold = models.DecimalField(max_digits=10, decimal_places=1, default=0.4, help_text="Threshold for Plate Detection.")
    character_threshold = models.DecimalField(max_digits=10, decimal_places=1, default=0.4, help_text="Threshold for Character Detection and Recognition.")
    plate_interval = models.IntegerField(default = 5, help_text="Inference Interval for Plate Detection.")
    roi_y_min = models.IntegerField(default = 0, help_text="ROI_Y Minimum value from Top. Inference will happen only in [(xmin,ymin),(xmax,ymin),(xmin,ymax),(xmax,ymax)]-(Origin at the top left corner).")
    roi_x_min = models.IntegerField(default = 0, help_text="ROI_X Minimum value from Left. Inference will happen only in [(xmin,ymin),(xmax,ymin),(xmin,ymax),(xmax,ymax)]-(Origin at the top left corner).")
    roi_y_max = models.IntegerField(default = 1080, help_text="ROI_Y Maximum value from Top. Inference will happen only in [(xmin,ymin),(xmax,ymin),(xmin,ymax),(xmax,ymax)]-(Origin at the top left corner).")
    roi_x_max = models.IntegerField(default = 1980, help_text="ROI_X Maximum value from Left. Inference will happen only in [(xmin,ymin),(xmax,ymin),(xmin,ymax),(xmax,ymax)]-(Origin at the top left corner).")
    nireq = models.IntegerField(default = 1, help_text="Number of Inference Requests for plate detection. It is usually the number of streams.")

    object_tracking = models.CharField(max_length=100, default = "short-term",help_text="short-term/zero-term/off - Enable Object Tracking.")
    post_processing_method = models.IntegerField(default = 15, help_text="Post-processing Method - 1 to 21. Refer to AB2 for details.")

    extras = models.IntegerField(default = -3, help_text="Extra pixels that we manually add to the cropped plate. Increasing this leads to coloured boundingbox in saved image. This is a potential bug - have to change gvawatermark if needed.")
    full_image_save_quality = models.IntegerField(default = 20, help_text="Cv2.Write Quaility of Image.Lesser the quality, lesser the storage space needed. Range of 0-99.")
    cropped_image_save_quality = models.IntegerField(default = 60, help_text="Cv2.Write Quaility of Image.Lesser the quality, lesser the storage space needed. Range of 0-99.")

    video_display = models.BooleanField(default=False, help_text="Tick to turn it on. Enables video display with bounding boxes and FPS for debugging purposes. Remember to disable before Deployment.")
    

    class Meta:
        #managed = True
        db_table = "anpr_cameras"

    def __str__(self):
        return self.camera_name
