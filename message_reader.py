from speechkit import Session, SpeechSynthesis

oauth_token = "AQAAAAAsHJkgAAhjwXshft5QgUuRkX0Wubhjlk"
catalog_id = "b1gd129pp9ha0vnvf5g7"

# Экземпляр класса `Session` можно получать из разных данных
session = Session.from_yandex_passport_oauth_token(oauth_token, catalog_id)

# Создаем экземляр класса `SpeechSynthesis`, передавая `session`,
# который уже содержит нужный нам IAM-токен
# и другие необходимые для API реквизиты для входа
synthesizeAudio = SpeechSynthesis(session)

# Метод `.synthesize()` позволяет синтезировать речь и сохранять ее в файл
synthesizeAudio.synthesize(
    'out.wav', text='Привет мир!',
    voice='oksana', format='lpcm', sampleRateHertz='16000'
)

# `.synthesize_stream()` возвращает объект типа `io.BytesIO()` с аудиофайлом
audio_data = synthesizeAudio.synthesize_stream(
    text='Привет мир, снова!',
    voice='oksana', format='lpcm', sampleRateHertz='16000'
)
