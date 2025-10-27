import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .forms import AudioFileForm
from .predictor import predict_genre # Assuming predictor.py is in the same app directory


def upload_audio(request):
    if request.method == 'POST':
        form = AudioFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['audio_file']
            # Save the file temporarily
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            temp_file_path = os.path.join(fs.location, filename)

            # Predict the genre
            predicted_genre = predict_genre(temp_file_path)

            # Delete the temporary file
            fs.delete(filename)

            return render(request, 'result.html', {'predicted_genre': predicted_genre})
        else:
            # If form is not valid, re-render the upload page with errors
            return render(request, 'upload.html', {'form': form})
    else:
        form = AudioFileForm()
    return render(request, 'upload.html', {'form': form})


@csrf_exempt
def predict_api(request):
    """API endpoint that accepts multipart/form-data with field 'file' and returns JSON { genre: str }"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    # Simple token auth: if API_TOKEN is set in settings, require header X-API-KEY
    token_required = bool(getattr(settings, 'API_TOKEN', ''))
    if token_required:
        provided = request.headers.get('X-API-KEY') or request.META.get('HTTP_X_API_KEY')
        if not provided or provided != settings.API_TOKEN:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    uploaded_file = request.FILES['file']
    fs = FileSystemStorage()
    filename = fs.save(uploaded_file.name, uploaded_file)
    temp_file_path = os.path.join(fs.location, filename)

    try:
        predicted_genre = predict_genre(temp_file_path)
        response = {'genre': predicted_genre, 'source': 'django'}
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        # cleanup
        try:
            fs.delete(filename)
        except Exception:
            pass
