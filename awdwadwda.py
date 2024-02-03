from datetime import datetime, timezone

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
from pillow_heif import register_heif_opener

def get_image_creation_date(image_path):
    if image_path.lower().endswith('.heic'):
        register_heif_opener()
        img = Image.open(image_path)
        exif_data = img.getexif()

        if exif_data is not None:  # Add this check
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == "DateTime":
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S").replace(tzinfo=timezone.utc)
    if image_path.lower().endswith('.jpeg') or image_path.lower().endswith('.jpg'):
        img = Image.open(image_path)
        exif_data = img._getexif()

        if exif_data is not None:  # Add this check
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == "DateTimeOriginal":
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return datetime.fromtimestamp(os.path.getmtime(image_path)).replace(tzinfo=timezone.utc)


# Пример использования:
folder_path = "z:/фото/2023/4 поток\\03_день (тропа_доверия)"
image_files = []

for filename in os.listdir(folder_path):
    if filename.lower().endswith((".jpg", ".heic")):
        image_path = os.path.join(folder_path, filename)
        date_taken = get_image_creation_date(image_path)
        if date_taken:
            image_files.append((filename, date_taken))

# Сортируем список файлов по дате съемки
sorted_image_files = sorted(image_files, key=lambda x: x[1])
sorted_image_files = sorted(image_files, key=lambda x: x[1])

# Выводим отсортированный список
for filename, date_taken in sorted_image_files:
    print(f"Файл: {filename}, Дата съемки: {date_taken}")



import os

путь_к_папке = '/путь/к/папке'  # Замените на путь к вашей папке

# Получить список файлов в папке
список_файлов = os.listdir(путь_к_папке)

# Пройти по каждому файлу и вывести имя и дату создания
for файл in список_файлов:
    полный_путь = os.path.join(путь_к_папке, файл)
    дата_создания = os.path.getctime(полный_путь)
    print(f'Файл: {файл}, Дата создания: {дата_создания}')


list1 = [1, 2, 3, 4, 5]
list2 = [2, 4]
result = list(set(list1) - set(list2))
print(result)