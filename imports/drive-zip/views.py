import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
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
