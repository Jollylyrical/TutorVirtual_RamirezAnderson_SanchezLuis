from django.db import transaction
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.knowledge.mongo_repository import get_repository

from .ai_gateway import AIGateway, AIGatewayError
from .models import Conversation, Message
from .prompts import build_prompt
from .serializers import AskSerializer, ConversationSerializer


class AskTutorView(APIView):
    def post(self, request):
        serializer = AskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data['question']
        conversation_id = serializer.validated_data.get('conversation_id')

        if conversation_id:
            conversation = Conversation.objects.filter(id=conversation_id, user=request.user).first()
            if conversation is None:
                return Response({'detail': 'Conversación no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            conversation = Conversation.objects.create(user=request.user, title=question[:80])

        repository = get_repository()
        search_results = repository.search(question, limit=5)
        context_chunks = [r.__dict__ for r in search_results]
        prompt = build_prompt(question, context_chunks)

        try:
            answer = AIGateway().generate(prompt)
        except AIGatewayError as exc:
            answer = f'No fue posible consultar el servicio de IA: {exc}'

        with transaction.atomic():
            Message.objects.create(
                conversation=conversation,
                role=Message.Role.USER,
                content=question,
                metadata={},
            )
            Message.objects.create(
                conversation=conversation,
                role=Message.Role.ASSISTANT,
                content=answer,
                metadata={'context': context_chunks},
            )
            conversation.save()

        return Response({
            'conversation_id': conversation.id,
            'question': question,
            'answer': answer,
            'context_used': context_chunks,
        })


class ConversationHistoryView(ListAPIView):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).prefetch_related('messages')
