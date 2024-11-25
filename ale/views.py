from django.http import HttpResponse
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import json
import datetime
import os
import wave
import speech_recognition as sr
from pydub import AudioSegment
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


def saludos(request):
    return HttpResponse("Hola esta es nuestra primera pagina django")

def sumar(request):
    res = 1 + 5
    return HttpResponse("la suma es: "+ str(res))

def damefecha(request):
    fecha_actual = datetime.datetime.now()

    return HttpResponse(fecha_actual)

def calcularEdad(request, agno):
    edad_actual=18
    periodo= agno - 2024
    edad_futura = edad_actual+ periodo
    documento = "<html><body><h2>En el año %s tendrás %s años</h2></body></html>" %(agno, edad_futura)

    return HttpResponse(documento)


from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Esto desactiva CSRF para esta vista
def mensaje(request):
    if request.method == "POST":
        try:
            # Leer el cuerpo de la solicitud y convertirlo a un diccionario Python
            data = request.body
            
            # Devolver la misma estructura JSON que recibimos
            return HttpResponse(data)
            

        except json.JSONDecodeError:
            # Si ocurre un error al procesar el JSON, respondemos con un error
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        
    else:
        # Si el método no es POST, devolvemos un error de "Método no permitido"
        return JsonResponse({"error": "Method Not Allowed"}, status=405)
    
@csrf_exempt  # Deshabilita la verificación CSRF para esta vista
def transcribir_audio(request):
    if request.method == "POST" and request.FILES.get('audio'):
        try:
            # Obtener el archivo de audio desde la solicitud POST
            audio_file = request.FILES['audio']
            
            # Guardar el archivo MP3 en el sistema temporalmente
            mp3_path = default_storage.save('temp_audio.mp3', ContentFile(audio_file.read()))
            
            # Convertir el archivo MP3 a WAV utilizando pydub
            mp3_audio = AudioSegment.from_mp3(mp3_path)
            wav_path = mp3_path.replace('.mp3', '.wav')
            mp3_audio.export(wav_path, format="wav")
            
            # Usar SpeechRecognition para transcribir el audio
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio = recognizer.record(source)  # Leer el archivo de audio completo

            # Intentar transcribir el audio a texto
            try:
                texto = recognizer.recognize_google(audio, language="es-ES")  # Reconocimiento de Google en español
                return JsonResponse({"texto": texto})
            except sr.UnknownValueError:
                return JsonResponse({"error": "No se pudo entender el audio"}, status=400)
            except sr.RequestError as e:
                return JsonResponse({"error": f"Error al conectar con el servicio de reconocimiento: {e}"}, status=500)
            
        except Exception as e:
            return JsonResponse({"error": f"Ocurrió un error: {str(e)}"}, status=500)
        
    else:
        return JsonResponse({"error": "Método o archivo no permitido"}, status=405)