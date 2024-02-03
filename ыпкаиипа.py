from PIL import Image
import os
from pillow_heif import register_heif_opener

register_heif_opener()
from PIL import Image
import os
from datetime import datetime

def get_photo_shooting_date(file_path):
    try:
        image = Image.open(file_path)
        exif_info = image._getexif()
        if exif_info:
            # Получение даты съемки из метаданных EXIF
            date_taken = exif_info.get(36867)  # 36867 соответствует дате съемки в EXIF
            print(datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S'))
            if date_taken:
                return datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
    except (AttributeError, KeyError, IndexError, ValueError):
        pass
    return datetime.min  # Возвращаем минимальную дату, если не удалось получить дату съемки

folder_path = "z:\фото\\2024\Новая папка"
files = sorted(os.listdir(folder_path), key=lambda x: get_photo_shooting_date(os.path.join(folder_path, x)))

# Теперь files содержит список файлов, отсортированных по дате съемки фотографий
