import uuid
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet

class Conversation(models.Model):
    """Conversation model to track exchanges between users and the agent"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Message(models.Model):
    """Message model with encrypted content"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=50)  # 'user' or 'agent'
    _encrypted_content = models.TextField(db_column='content')  # Encrypted content stored in DB
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    @property
    def content(self):
        """Decrypt the content when accessed"""
        if not self._encrypted_content:
            return None
        key = settings.ENCRYPTION_KEY.encode()
        f = Fernet(key)
        return f.decrypt(self._encrypted_content.encode()).decode()
    
    @content.setter
    def content(self, value):
        """Encrypt the content when set"""
        if value is None:
            self._encrypted_content = None
        else:
            key = settings.ENCRYPTION_KEY.encode()
            f = Fernet(key)
            self._encrypted_content = f.encrypt(str(value).encode()).decode()
    
    def __str__(self):
        return f"{self.role} message in {self.conversation_id}"
