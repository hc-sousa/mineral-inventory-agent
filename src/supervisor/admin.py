from django.contrib import admin
from .models import AgentConversation, AgentMessage

@admin.register(AgentConversation)
class AgentConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'started_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'started_at')
    search_fields = ('id', 'user__username')

@admin.register(AgentMessage)
class AgentMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'message_type', 'timestamp')
    list_filter = ('message_type', 'timestamp')
    search_fields = ('content',)
