from django.db import models
from django.conf import settings

class __ThrottleBucket(models.Model):
    """
    A Django model for storing rate-limiting information

    Note: in practice, using the database as a rate-limiting storage backend is an impractical choice.
    """
    zone_name = models.CharField(max_length=255, help_text="Which throttle zone does this bucket apply to?")

    bucket_timespan = models.IntegerField(help_text="Number of seconds for the entire bucket ring", editable=False)
    bucket_offset = models.IntegerField(help_text="Number of seconds for this single bucket", editable=False)
    bucket_key = models.CharField(max_length=255, db_index=True, editable=False)

    count = models.IntegerField(default=0)
    expires = models.PositiveIntegerField(editable=False)

    class Meta:
        unique_together = [('zone_name', 'bucket_timespan', 'bucket_offset', 'bucket_key',)]

# Normally, we aren't going to use this
if getattr(settings, 'THROTTLE_BACKEND', '').rpartition('.')[2] == 'ModelStore':
    ThrottleBucket = __ThrottleBucket

