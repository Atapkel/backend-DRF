from storages.backends.s3boto3 import S3Boto3Storage

class ClubLogoStorage(S3Boto3Storage):
    location = 'club_logo'
    file_overwrite = False

class RoomImageStorage(S3Boto3Storage):
    location = 'room_images'
    file_overwrite = False

class EventImageStorage(S3Boto3Storage):
    location = 'event_images'
    file_overwrite = False