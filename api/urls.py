from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import SimpleRouter

from api.views import *

chat_image_router = SimpleRouter()
chat_image_router.register(r'chat-image', ImageUploadAPIViewSet)

urlpatterns = [

    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('register/', RegistrationView.as_view(), name='registration'),
    path('chat/', ChatListCreateView.as_view(), name='chat'),
    path('chat/<int:chat_id>/', ChatGPT.as_view()),
    path('user/', UserDataAPIView.as_view()),

    path('', include(chat_image_router.urls))
]
