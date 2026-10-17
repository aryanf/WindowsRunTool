
!c::
{
	HideProjectOverlayNow()
    ;Run "cmd.exe /c p cut"
	;Run "C:\code\WindowsRunTool\portable_open_source_apps\ShareX\ShareX.exe -PinToScreenFromScreen"
	;Run 'cmd.exe /c start "" "C:\code\WindowsRunTool\portable_open_source_apps\ShareX\ShareX.exe" -PinToScreenFromScreen',, "Hide"
    Run "cmd.exe /c p cut",, "Hide"
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
	HideProjectOverlayNow()
	Run "cmd.exe /c p shot"
	;Run "C:\code\WindowsRunTool\portable_open_source_apps\ShareX\ShareX.exe -RectangleRegion"
}

!r::
{
	Run "cmd.exe /c p record"
}

!q::
{
	Run "cmd.exe /c e"
	;Run "C:\code\WindowsRunTool\portable_open_source_apps\Q-Dir\Q-Dir_x64.exe"
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
	;Run "cmd.exe /c p fix"
	Send "{NumpadAdd}"
}


#HotIf WinActive("ahk_exe chrome.exe") or WinActive("ahk_exe msedge.exe")
!Down::
{
    Send "^+{Space}"
}
#HotIf

; VS Code - Use default Alt+Down behavior (pass through)
#HotIf WinActive("ahk_exe Code.exe")
!Down::Send "!{Down}"
#HotIf

#Down::WinMinimize("A")

; Ctrl+Shift+Click: Open link in Edge (non-default browser)
#HotIf WinActive("ahk_exe chrome.exe") or WinActive("ahk_exe msedge.exe")
^+LButton::
{
    ClipSaved := A_Clipboard
    A_Clipboard := ""

    ; Release modifier keys so context menu is normal
    Send "{Ctrl up}{Shift up}"
    Sleep 50

    Click "Right"
    Sleep 200
    Send "e"  ; "Copy link address" accelerator in Chromium context menus
    
    if ClipWait(1) {
        LinkURL := A_Clipboard
        A_Clipboard := ClipSaved
        if (SubStr(LinkURL, 1, 4) = "http") {
            Run 'msedge.exe "' LinkURL '"'
            return
        }
    }

    A_Clipboard := ClipSaved
}
#HotIf

; Get monitor center and move mouse
DllCall("SetProcessDpiAwarenessContext", "ptr", -4)
CoordMode("Mouse", "Screen")

; =========================
; USER MAPPING (EDIT THIS)
; =========================
; Key = what YOU think (numpad)
; Value = actual Windows monitor number
monitorMap := Map(
    1, 2,   ; Numpad1 -> Windows monitor 2
    2, 1,   ; Numpad2 -> Windows monitor 1
    3, 3    ; Numpad3 -> Windows monitor 3
)

MoveMouseToMonitor(mappedNumber) {
    MonitorGetWorkArea(mappedNumber, &left, &top, &right, &bottom)

    centerX := left + (right - left) // 2
    centerY := top + (bottom - top) // 2

    if (centerX = "" || centerY = "")
        return

    DllCall("SetCursorPos", "int", centerX, "int", centerY)
}

MoveMouseMapped(userNumber) {
    global monitorMap

    if (!monitorMap.Has(userNumber))
        return

    MoveMouseToMonitor(monitorMap[userNumber])
}

; Ctrl + Numpad
^Numpad1::MoveMouseMapped(1)
^Numpad2::MoveMouseMapped(2)
^Numpad3::MoveMouseMapped(3)

; Alt + Numpad
!Numpad1::MoveMouseMapped(1)
!Numpad2::MoveMouseMapped(2)
!Numpad3::MoveMouseMapped(3)

; WinKey + Numpad
#Numpad1::MoveMouseMapped(1)
#Numpad2::MoveMouseMapped(2)
#Numpad3::MoveMouseMapped(3)

; Alt + number row (left hand)
!1::MoveMouseMapped(1)
!2::MoveMouseMapped(2)
!3::MoveMouseMapped(3)



; ============================================================
; VS Code project overlay
; When you switch to a different VS Code window, flash a big,
; centered overlay with the project name for a couple of seconds
; so you can tell at a glance which project it is.
; ============================================================
global _lastActiveHwnd := 0
global _projectOverlayGui := 0

SetTimer(WatchActiveWindowForOverlay, 250)

WatchActiveWindowForOverlay()
{
    global _lastActiveHwnd
    hwnd := WinExist("A")
    if (!hwnd || hwnd == _lastActiveHwnd)
        return
    _lastActiveHwnd := hwnd

    ; Only react to VS Code windows
    try proc := WinGetProcessName(hwnd)
    catch
        return
    if (proc != "Code.exe")
        return

    try title := WinGetTitle(hwnd)
    catch
        return
    if (title == "")
        return

    ShowProjectOverlay(GetProjectNameFromTitle(title), hwnd)
}

GetProjectNameFromTitle(title)
{
    t := Trim(title)
    ; Drop the trailing app name (Visual Studio Code / Cursor)
    t := RegExReplace(t, "\s*[-\x{2014}]\s*(Visual Studio Code|Cursor)$", "")
    ; The VS Code title format is "<file> - <project> - Visual Studio Code",
    ; so the last remaining " - " segment is the project/folder name.
    parts := StrSplit(t, " - ")
    name := Trim(parts[parts.Length])
    ; Remove any leading unsaved indicators
    name := Trim(RegExReplace(name, "^[\x{25CF}\x{2022}\*]+\s*", ""))
    if (name == "")
        name := t
    ; Replace a trailing WSL remote tag, e.g. "[WSL: Ubuntu-22.04]", with "wsl"
    name := Trim(RegExReplace(name, "\s*\[WSL:[^\]]*\]\s*$", " wsl"))
    ; Trim common repo prefixes
    name := RegExReplace(name, "^(mdm-me-svc-|en-g-)", "")
    return name
}

ShowProjectOverlay(name, hwnd := 0)
{
    global _projectOverlayGui

    if (_projectOverlayGui)
    {
        try _projectOverlayGui.Destroy()
        _projectOverlayGui := 0
    }

    g := Gui("+AlwaysOnTop -Caption +ToolWindow +E0x20 +E0x80000 +E0x8000000")
    g.BackColor := "202020"
    g.MarginX := 48
    g.MarginY := 28
    g.SetFont("s48 bold", "Segoe UI")
    g.AddText("cF5F5F5 Center", name)

    ; Size the overlay first (kept hidden), then place it near the bottom
    ; (about 15% up from the bottom edge) of the monitor that holds the
    ; target VS Code window, horizontally centered.
    g.Show("NoActivate AutoSize Hide")
    g.GetPos(, , &gw, &gh)
    GetMonitorWorkAreaForWindow(hwnd, &wl, &wt, &wr, &wb)
    cx := (wl + wr) // 2
    tx := cx - (gw // 2)
    ty := Round(wt + (wb - wt) * 0.85) - (gh // 2)
    g.Show("NoActivate x" tx " y" ty)
    WinSetTransparent(235, g)

    _projectOverlayGui := g
    SetTimer(HideProjectOverlay, -350)
}

GetMonitorWorkAreaForWindow(hwnd, &wl, &wt, &wr, &wb)
{
    ; Default to the primary monitor's work area as a fallback
    MonitorGetWorkArea(MonitorGetPrimary(), &wl, &wt, &wr, &wb)

    if (!hwnd)
        return
    try WinGetPos(&wx, &wy, &ww, &wh, hwnd)
    catch
        return

    winCx := wx + (ww // 2)
    winCy := wy + (wh // 2)

    Loop MonitorGetCount()
    {
        MonitorGet(A_Index, &ml, &mt, &mr, &mb)
        if (winCx >= ml && winCx < mr && winCy >= mt && winCy < mb)
        {
            MonitorGetWorkArea(A_Index, &wl, &wt, &wr, &wb)
            return
        }
    }
}

HideProjectOverlay()
{
    global _projectOverlayGui
    if (_projectOverlayGui)
    {
        try _projectOverlayGui.Hide()
    }
}

HideProjectOverlayNow()
{
    global _projectOverlayGui
    if (_projectOverlayGui)
    {
        try _projectOverlayGui.Destroy()
        _projectOverlayGui := 0
    }
    SetTimer(HideProjectOverlay, 0)  ; cancel any pending hide timer
}

; Win + R launches Windows Terminal
#r::Run "sr.exe"