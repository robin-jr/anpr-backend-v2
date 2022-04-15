from os import name
from django.db import models

# model for vehicle tye like bike, car etc.
class VehicleTypeRef(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45)

    class Meta:
        db_table = "vehicle_type_ref"

    def str(self):
        return self.name

#model for vechile make like honda, yamaha ect.
class VehicleMakeRef(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45)
    type_id = models.CharField(max_length=45)

    class Meta:
        db_table = "vehicle_make_ref"


    def str(self):
        return self.name

#model for vehicle model like honda activa, yamaha v2 etc.
class VehicleModelRef(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45)
    make = models.ForeignKey(VehicleMakeRef,to_field='id', on_delete=models.DO_NOTHING)
    type = models.ForeignKey(VehicleTypeRef, to_field='id', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "vehicle_model_ref"

    def str(self):
        return self.name

#model for vehicle color like red, green, blue etc.
class VehicleColorRef(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45)
    code = models.CharField(max_length=45)

    class Meta:
        db_table = "vehicle_color_ref"

    def str(self):
        return self.name

# model for license_plates_anpr table
# contains information about the vechile
class LicensePlatesAnpr(models.Model):
    entry_id = models.AutoField(primary_key=True)
    camera_name = models.CharField(max_length=100)
    plate_number = models.CharField(max_length=50)
    date = models.DateTimeField()
    anpr_full_image = models.CharField(max_length=100)
    anpr_cropped_image = models.CharField(max_length=100)
    vehicle_type = models.ForeignKey(VehicleTypeRef, to_field='id', on_delete= models.DO_NOTHING, default=1)
    vehicle_make = models.ForeignKey(VehicleMakeRef, to_field='id', on_delete= models.DO_NOTHING, default=1)
    vehicle_model = models.ForeignKey(VehicleModelRef, to_field='id', on_delete=models.DO_NOTHING, default=1)
    vehicle_color = models.ForeignKey(VehicleColorRef, to_field='id', on_delete=models.DO_NOTHING, default=1)

    class Meta:
        db_table = "license_plates_anpr"

    def str(self):
        return self.plate_number




