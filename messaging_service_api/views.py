from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

@api_view(['POST'])
def create_conversation(request):
    participants = request.data.get('participants', [])
    conversation = Conversation.objects.create()
    conversation.participants.set(participants)
    return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def send_message(request, conversation_id):
    try:
        conversation = Conversation.objects.get(pk=conversation_id)
    except Conversation.DoesNotExist:
        return Response({'message': 'Conversation not found.'}, status=status.HTTP_404_NOT_FOUND)

    text = request.data.get('text')
    sender = request.user
    message = Message.objects.create(conversation=conversation, sender=sender, text=text)
    return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
