import datetime
from django.db import models

class AppointmentMeta(models.Model):

    id = models.IntegerField(primary_key=True)
    arrival_time = models.DateTimeField(null=True)
    start_time = models.DateTimeField(null=True)

    @property
    def wait_time(self):
        wait_time = datetime.timedelta(days=0)
        if self.arrival_time:
            if self.start_time:
                wait_time = self.start_time - self.arrival_time
            else:
                wait_time = datetime.datetime.now() - self.arrival_time    
        
        return int(wait_time.total_seconds() // 60)