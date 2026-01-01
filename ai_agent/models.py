from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatSession(models.Model):
    """
    Represents a chat session between a user and the AI agent.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Chat session {self.id} for {self.user.username}"

    @property
    def message_count(self):
        return self.messages.count()

    @property
    def last_message_time(self):
        last_message = self.messages.order_by('-timestamp').first()
        return last_message.timestamp if last_message else self.created_at


class ChatMessage(models.Model):
    """
    Represents a message in a chat session.
    """
    MESSAGE_TYPES = (
        ('user', 'User'),
        ('ai', 'AI'),
        ('system', 'System'),
    )

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.get_message_type_display()} message in session {self.session_id}"


class DashboardContext(models.Model):
    """
    Stores context information from the dashboard for use with the AI agent.
    This implements the Model Context Protocol (MCP) by capturing the state
    of the dashboard at a point in time.
    """
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='contexts')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Dashboard overview context
    total_products = models.IntegerField(null=True, blank=True)
    total_resources = models.IntegerField(null=True, blank=True)
    active_products = models.IntegerField(null=True, blank=True)
    completed_products = models.IntegerField(null=True, blank=True)
    
    # Current filters and view state
    current_view = models.CharField(max_length=100, blank=True)
    applied_filters = models.JSONField(default=dict, blank=True)
    
    # Visualization states
    visible_charts = models.JSONField(default=list, blank=True)
    
    # User history
    recent_actions = models.JSONField(default=list, blank=True)
    
    # KPI context
    kpi_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Dashboard context at {self.timestamp}"