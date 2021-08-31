from django.db import models

class LicensePlatesAnpr(models.Model):
    entry_id = models.AutoField(primary_key=True)
    camera_name = models.CharField(max_length=100)
    plate_number = models.CharField(max_length=50)
    date = models.DateTimeField()
    anpr_full_image = models.CharField(max_length=100)
    anpr_cropped_image = models.CharField(max_length=100)
    

    class Meta:
        #managed = True
        db_table = "license_plates_anpr"
