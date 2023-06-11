from data_processing import config_read

album_ids = config_read()['album_ids']
folder_path = "масленица ням"

new_array = []

for album_id in album_ids:
    key = list(album_id.keys())[0]
    value = album_id[key]

    if key in folder_path:
        print(folder_path, *value)



print(new_array)
