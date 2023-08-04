from django.http import JsonResponse
from django.shortcuts import render
from .forms import VideoForm
from pytube import YouTube

import os
import re


def clean_filename(filename):
    cleaned_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return cleaned_filename


def download_page(request):
    form = VideoForm(request.POST or None)
    video_url = None
    file_link = None

    if form.is_valid():
        video_url = form.cleaned_data['url']
        request.session['video_url'] = video_url.strip()

        try:
            yt = YouTube(video_url)
            video_title = clean_filename(yt.title)
            format_choice = form.cleaned_data['format']
            download_path = form.cleaned_data['download_path']

            if format_choice == 'mp4':
                stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                if stream:
                    home_dir = os.path.expanduser("~")
                    download_path = os.path.join(home_dir, 'Downloads')

                    if not os.path.exists(download_path):
                        os.makedirs(download_path)

                    video_title_cleaned = clean_filename(video_title)
                    download_file_path = os.path.join(download_path, f'{video_title_cleaned}.mp4')
                    stream.download(output_path=download_path, filename=video_title_cleaned)
                    file_link = download_file_path

            elif format_choice == 'mp3':
                audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()
                if audio_stream:
                    if not download_path:
                        home_dir = os.path.expanduser("~")
                        download_path = os.path.join(home_dir, 'Downloads')

                    if not os.path.exists(download_path):
                        os.makedirs(download_path)

                    video_title_cleaned = clean_filename(video_title)
                    download_file_path = os.path.join(download_path, f'{video_title_cleaned}.mp4')
                    audio_stream.download(output_path=download_path, filename=video_title_cleaned)

                    # Конвертация mp4 в mp3
                    from moviepy.editor import VideoFileClip
                    video_clip = VideoFileClip(download_file_path)
                    audio_clip = video_clip.audio
                    mp3_file_path = os.path.join(download_path, f'{video_title_cleaned}.mp3')
                    audio_clip.write_audiofile(mp3_file_path)
                    os.remove(download_file_path)  # Удаляем оригинальный mp4 файл

                    file_link = mp3_file_path
        except Exception as e:
            print("Произошла ошибка:", str(e))

    context = {'form': form, 'video_url': video_url, 'file_link': file_link}
    return render(request, 'download.html', context)


def get_progress(request):
    if request.method == 'GET':
        try:
            yt = YouTube(request.session['video_url'])
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

            if stream:
                total_size = stream.filesize
                downloaded_size = total_size - (
                    stream.filesize_remaining if hasattr(stream, 'filesize_remaining') else 0)
                percent = int((downloaded_size / total_size) * 100)
                finished = downloaded_size == total_size

                return JsonResponse({'percent': percent, 'finished': finished})
        except Exception as e:
            print(e)

    return JsonResponse({'percent': 0, 'finished': False})
