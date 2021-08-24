from django.db import models
from django.utils import timezone


class LicensePlatesRlvd(models.Model):
    slno = models.AutoField(primary_key=True)
    camera_number = models.CharField(max_length=100)
    junction_name = models.CharField(max_length=100)
    evidence_camera_name = models.CharField(max_length=100)
    number_plate_number = models.CharField(max_length=50)
    date = models.DateTimeField()
    anpr_image = models.CharField(max_length=100)
    # violations = models.CharField(max_length=1000) #todo
    # evidence_images = models.CharField(max_length=1000) #todo
    xmin=models.CharField(max_length=50)
    xmax=models.CharField(max_length=50)
    ymin=models.CharField(max_length=50)
    ymax=models.CharField(max_length=50)
    reviewed=models.IntegerField()

    class Meta:
        #managed = True
        db_table = "license_plates_rlvd"

    def str(self):
        return self.number_plate_number

class EvidenceCamImg(models.Model):
    id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(LicensePlatesRlvd, on_delete=models.CASCADE)
    evidence_image = models.CharField(max_length=100)

    class Meta:
        db_table = 'evidence_cam_img'
    def str(self):
        return self.evidence_image


class ViolationRef(models.Model):
    id = models.AutoField(primary_key=True)
    violation_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'violation_ref'
    def str(self):
        return self.violation_name


class Violation(models.Model):
    id = models.AutoField(primary_key=True)
    violation = models.ForeignKey(ViolationRef,on_delete=models.CASCADE)
    vehicle = models.ForeignKey(LicensePlatesRlvd, on_delete=models.CASCADE)

    class Meta:
        db_table = 'violations'
    def str(self):
        return self.violation



class Camera(models.Model):
    id = models.AutoField(primary_key=True)
    camera_number = models.CharField(max_length=100, help_text="Name of the Camera. AVOID SPACES IN THE NAME.")
    latitude = models.DecimalField(max_digits=10, decimal_places=7, help_text="Latitude of the Camera Location.")
    longitude = models.DecimalField(max_digits=10, decimal_places=7, help_text="Longitude of the Camera Location.")
    url = models.CharField(max_length=400, help_text="Functioning RTSP link(rtsp://localhost:8554/ds-test) or Path to Local Video(/home/user/vid.mp4). AVOID SPACES IN THE NAME.")
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
    cluster_end = models.IntegerField(default = 30, help_text="Y-axis value beyond which we delcare that vehicle has passed and the cluster has ended. 0 means end of ROI- but then full image of vehicle will be missed. So a value of 20-60 is ideal i.e, save image when plate is at 20 pixels away from top x-axis. This is the same as RLVD. Set it to 0 to disable this.")
    cluster_end_vehicle = models.IntegerField(default = 10, help_text="Number of plates in a vehicle cluster beyond which we declare that the cluster has ended and start post-processing. This feature is EXPERIMENTAL and was added to handle STATIC VEHICLES. A value of 10 means, if 10 plates are detected in a vehicle cluster, then plate detection is stopped and post-processing starts. Set it to a high value(100) to disable. Both cluster_end and cluster_end_vehicle are used to end clusters.")
    no_of_active_vehicles = models.IntegerField(default = 3, help_text="Number of vehilces in the done_tracking_ids at a time. Rest will be popped to clear repetition of ids. This parameter was added to counter choppiness.")


    extras = models.IntegerField(default = -3, help_text="Extra pixels that we manually add to the cropped plate. Increasing this leads to coloured boundingbox in saved image. This is a potential bug - have to change gvawatermark if needed.")
    full_image_save_quality = models.IntegerField(default = 20, help_text="Cv2.Write Quaility of Image.Lesser the quality, lesser the storage space needed. Range of 0-99.")
    cropped_image_save_quality = models.IntegerField(default = 60, help_text="Cv2.Write Quaility of Image.Lesser the quality, lesser the storage space needed. Range of 0-99.")

    video_display = models.BooleanField(default=False, help_text="Tick to turn it on. Enables video display with bounding boxes and FPS for debugging purposes. Remember to disable before Deployment.")
    

    class Meta:
        #managed = True
        db_table = "camera_config"

    def __str__(self):
        return self.camera_number
