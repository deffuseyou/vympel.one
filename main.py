import yt_dlp

ydl = yt_dlp.YoutubeDL({'format': "bv*+ba/b",
                        'output': "z:\\1s"})

ydl.download("ytsearch:iowa бьет бит", )