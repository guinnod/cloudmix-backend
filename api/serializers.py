from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Chat, Message, ChatImages


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['role', 'content', 'time', 'status']


class MessageChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['role', 'content']


class ChatSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            message_serializer = MessageSerializer(last_message)
            return message_serializer.data
        return None

    class Meta:
        model = Chat
        fields = ['id', 'name', 'last_message']


class ChatImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatImages
        fields = '__all__'


