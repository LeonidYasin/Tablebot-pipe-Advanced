#!/usr/bin/env python3
from PIL import Image
import os

def create_test_media():
    """Создает простые тестовые медиафайлы"""
    
    # Создаем тестовое изображение
    img = Image.new('RGB', (400, 300), color='red')
    img.save('test_image.jpg')
    print("✅ Создан test_image.jpg")
    
    # Создаем тестовый PDF
    with open('test_document.pdf', 'w') as f:
        f.write("This is a test PDF document\n")
        f.write("Test content for document testing\n")
    print("✅ Создан test_document.pdf")
    
    # Создаем тестовый видеофайл (простой текстовый файл с расширением .mp4)
    with open('test_video.mp4', 'w') as f:
        f.write("This would be a video file in real scenario\n")
    print("✅ Создан test_video.mp4 (заглушка)")

if __name__ == "__main__":
    create_test_media()