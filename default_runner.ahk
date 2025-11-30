
!c::
{
	;Run "cmd.exe /c p cut"
	Run "C:\code\WindowsRunTool\portable_open_source_apps\ShareX\ShareX.exe -PinToScreenFromScreen"
}

!p::
{
	;Run "cmd.exe /c p pen"
	send "^2"
}

!w::
{
	Run "cmd.exe /c p wait"
}

!s::
{
	;Run "cmd.exe /c p shot"
	Run "C:\code\WindowsRunTool\portable_open_source_apps\ShareX\ShareX.exe -RectangleRegion"
}

!r::
{
	Run "cmd.exe /c p record"
}

!q::
{
	;Run "cmd.exe /c e"
	Run "C:\code\WindowsRunTool\portable_open_source_apps\Q-Dir\Q-Dir_x64.exe"
}


!d::
{
	;Run "cmd.exe /c e"
	Run "C:\code\WindowsRunTool\portable_open_source_apps\DoubleCmd\doublecmd.exe"
}

!x::
{
	Run "cmd.exe /c p cut toggle"
}


!f::
{
	Run "cmd.exe /c p fix"
}


#HotIf WinActive("ahk_exe chrome.exe") or WinActive("ahk_exe msedge.exe")
!Down::
{
    Send "^+a"
}
#HotIf

; VS Code - Use default Alt+Down behavior (pass through)
#HotIf WinActive("ahk_exe Code.exe")
!Down::Send "!{Down}"
#HotIf

#Down::WinMinimize("A")