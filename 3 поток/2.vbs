set WshShell = WScript.CreateObject("WScript.Shell" )
set oShellLink = WshShell.CreateShortcut("d:\������� ����\Shortcut.lnk" ) ' ��� ���������
oShellLink.TargetPath = WScript.Arguments.Item(0) ' ������
oShellLink.Arguments = "" ' ��������� �������
oShellLink.WindowStyle = 1 ' ����� ����: 1-�������; 3-����������; 7-��������
oShellLink.Description = WScript.Arguments.Item(1) '  �����������
oShellLink.WorkingDirectory = WScript.Arguments.Item(0)
oShellLink.Save