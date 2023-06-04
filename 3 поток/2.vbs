set WshShell = WScript.CreateObject("WScript.Shell" )
set oShellLink = WshShell.CreateShortcut("d:\рабочий стол\Shortcut.lnk" ) ' Где создается
oShellLink.TargetPath = WScript.Arguments.Item(0) ' Объект
oShellLink.Arguments = "" ' Аргументы запуска
oShellLink.WindowStyle = 1 ' Стиль окна: 1-Обычное; 3-Развёрнутое; 7-Свёрнутое
oShellLink.Description = WScript.Arguments.Item(1) '  Комментарий
oShellLink.WorkingDirectory = WScript.Arguments.Item(0)
oShellLink.Save