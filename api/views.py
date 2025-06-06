# api/views.py
import uuid

import yt_dlp
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


from .serializers import *
from rest_framework import generics, status

from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import FileResponse
from pytube import YouTube
from pytube.exceptions import RegexMatchError, VideoUnavailable, LiveStreamError
from django.http import FileResponse
from rest_framework.decorators import api_view
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pytube import YouTube
from django.http import FileResponse
import os
import uuid
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse
import yt_dlp


@api_view(["POST"])
def download_video(request):
    try:
        url = request.data.get("url")
        if not url:
            return Response({"error": "URL is required"}, status=400)

        video_dir = "media/videos"
        os.makedirs(video_dir, exist_ok=True)

        file_name = f"{uuid.uuid4()}.mp4"
        output_path = os.path.join(video_dir, file_name)

        ydl_opts = {
            'outtmpl': output_path,
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        response = FileResponse(open(output_path, 'rb'), as_attachment=True, filename=file_name)

        # Faylni o'chirish uchun callback qo'shish
        def file_cleanup(response):
            try:
                os.remove(output_path)
            except Exception as e:
                print(f"File delete error: {e}")
            return response

        response.close = lambda *args, **kwargs: file_cleanup(response)

        return response

    except Exception as e:
        return Response({"error": str(e)}, status=500)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=201)
        return Response(serializer.errors, status=400)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                }
            })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, created = Profile1.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, _ = Profile1.objects.get_or_create(user=request.user)

        data = {
            "bio": request.data.get("bio", profile.bio),
            "avatar": request.data.get("avatar", profile.avatar)
        }

        serializer = UserProfileSerializer(profile, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)