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
            format = form.cleaned_data['format']
            download_path = form.cleaned_data['download_path']

            if format == 'mp4':
                stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                if stream:
                    if not download_path:
                        download_path = os.path.join('downloads')

                    if not os.path.exists(download_path):
                        os.makedirs(download_path)

                    video_title_cleaned = clean_filename(video_title)
                    download_file_path = os.path.join(download_path, f'{video_title_cleaned}.mp4')
                    stream.download(output_path=download_path, filename=video_title_cleaned)
                    file_link = download_file_path

            # Similar handling for 'mp3' format

        except Exception as e:
            print(e)

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
