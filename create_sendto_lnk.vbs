Set WshShell = CreateObject("WScript.Shell")
strShortcutPath = WshShell.SpecialFolders("SendTo") & "\FoxShareMyFile.lnk"
Set oShortcut = WshShell.CreateShortcut(strShortcutPath)

oShortcut.TargetPath = "C:\Program Files\FoxShareMyFile\.venv\Scripts\pythonw.exe"
oShortcut.Arguments = """C:\Program Files\FoxShareMyFile\hosting.py"""
oShortcut.Save
