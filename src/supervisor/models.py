from django.db import models
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

class AgentConversation(models.Model):
    """
    Model to track agent conversations
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Conversation {self.id} - {'Anonymous' if self.user is None else self.user.username}"
    
    class Meta:
        ordering = ['-updated_at']

class AgentMessage(models.Model):
    """
    Model to store messages in a conversation
    """
    MESSAGE_TYPE_CHOICES = (
        ('user', 'User'),
        ('agent', 'Agent'),
        ('system', 'System'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(AgentConversation, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.message_type} message in {self.conversation}"
    
    class Meta:
        ordering = ['timestamp']
