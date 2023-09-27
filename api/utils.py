import os


def upload_image_path(instance, filename):
    return os.path.join('chat-gpt-images', filename)