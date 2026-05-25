from rest_framework import serializers

from .models import Conversation, Message


class AskSerializer(serializers.Serializer):
    question = serializers.CharField(min_length=3)
    conversation_id = serializers.IntegerField(required=False)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'metadata', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'messages']
