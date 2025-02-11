from django.db import models
import uuid

class AnalysisSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')  # pending, processing, completed

    def __str__(self):
        return f"Session {self.session_id}"

class UploadedFile(models.Model):
    session = models.ForeignKey(AnalysisSession, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    processed_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name