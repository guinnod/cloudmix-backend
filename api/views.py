from django.utils import timezone

import urllib.parse
import openai
import os
from dotenv import load_dotenv
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, JSONParser
from serpapi import GoogleSearch


from .models import Chat, Message, ChatImages
from .serializers import RegistrationSerializer, ChatSerializer, MessageSerializer, ChatImageSerializer, MessageChatSerializer

load_dotenv()


class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer


class ChatListCreateView(generics.ListCreateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def get_queryset(self):
        # Filter the queryset to include only chats where the user is equal to request.user
        return Chat.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if not request.user:
            return Response({"message": "Not authorized"})

        chat = Chat.objects.create(user=request.user, name=request.data.get("name"))
        chat.save()
        return Response({"chatId": chat.id})


class ChatGPT(APIView):
    def get(self, request, chat_id):

        chat = get_object_or_404(Chat, id=chat_id)
        messages_obj = Message.objects.filter(chat=chat)

        messages_status = messages_obj.filter(status=False)
        for m in messages_status:
            m.status = True
            m.save()

        messages = MessageSerializer(messages_obj, many=True)
        return Response(messages.data)

    def post(self, request, chat_id):
        type = request.query_params.get('type')

        msg = request.data.get("content")
        time = request.data.get("time")

        chat = get_object_or_404(Chat, id=chat_id)

        message = Message.objects.create(role="user", content=msg, time=time)
        chat.messages.add(message)

        if type == 'message':
            input_messages = [
                {"role": "system", "content": "You are a helpful assistant."},
            ]
            messages = MessageChatSerializer(Message.objects.filter(chat=chat), many=True).data
            # print(messages)
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=input_messages + messages,
                )
                assistant_reply = response.choices[0].message["content"]
            except Exception as e:
                return Response({"message": str(e)}, status=500)
        else:
            original_url = msg
            encoded_url = urllib.parse.quote(original_url, safe="")

            params = {
                "engine": "google_lens",
                "url": encoded_url,
                "api_key": os.getenv('GOOGLE_SEARCH_API_KEY')
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            matches_data, char = self._get_results_data(results)
            assistant_reply = self._get_response_data(matches_data, char)

        assistant_message = Message.objects.create(role="assistant", content=assistant_reply, time=time+100)
        chat.messages.add(assistant_message)

        return Response(MessageSerializer(assistant_message, many=False).data)

    def _get_results_data(self, results):
        try:
            return results["knowledge_graph"], 'k'
        except KeyError:
            return results["visual_matches"], 'v'

    def _get_response_data(self, result, char):
        if not result:
            return "No information about this image"
        else:
            assistant_reply = ""
            i = 1
            for item in result:
                title = item.get("title", "")
                if char == 'k':
                    data = item.get("subtitle", "")
                else:
                    data = item.get("link", "")

                combined = f"{data} - {title}"
                assistant_reply += combined + "\n"
                i += 1

                if i == 4:
                    break

            return assistant_reply


class ImageUploadAPIViewSet(mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin,
                            GenericViewSet):
    parser_classes = [MultiPartParser, JSONParser]
    queryset = ChatImages.objects.all()
    serializer_class = ChatImageSerializer


class UserDataAPIView(APIView):
    def get(self, request):
        try:
            user = request.user
            serialized_user = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
            return Response(serialized_user, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
