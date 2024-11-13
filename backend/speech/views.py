import os
from django.conf import settings
from rest_framework.response import Response
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework import status

from google.cloud import texttospeech, speech
from google.oauth2 import service_account

# Create your views here.
class SpeechToText(APIView):
    def post(self, request):
        try:
            credentials = service_account.Credentials.from_service_account_file(settings.GOOGLE_APPLICATION_CREDENTIALS)
            client = speech.SpeechClient(credentials=credentials)
            audio_file = request.FILES.get('audio_file')
            content = audio_file.read()
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code="en-US",
                model="video"
            )
            response = client.recognize(config=config, audio=audio)
            voicetext = response.results[0].alternatives[0].transcript
            return Response({"text": voicetext}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TextToSpeech(APIView):
    def post(self, request):
        try:
            credentials = service_account.Credentials.from_service_account_file(settings.GOOGLE_APPLICATION_CREDENTIALS)
            client = texttospeech.TextToSpeechClient(credentials=credentials)
            text = request.data["text"]
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Studio-O"
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                effects_profile_id=["small-bluetooth-speaker-class-device"],
                speaking_rate=1,
                pitch=1
            )
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            with open('./speech.mp3', 'wb') as audio_file:
                audio_file.write(response.audio_content)

            audio_file_path = os.path.join('./speech.mp3')
            response = FileResponse(open(audio_file_path, 'rb'), content_type='audio/mpeg')
            response['Content-Disposition'] = 'inline; filename="audio.mp3"'
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
