import os
import subprocess
import sys


def reproducir_alerta():
    if sys.platform == "win32":
        import winsound

        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)


def notificar_escritorio(mensaje):
    if sys.platform != "win32":
        return
    # Windows Forms muestra el aviso en el área de notificaciones.
    script = """
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$icono = New-Object System.Windows.Forms.NotifyIcon
try {
    $icono.Icon = [System.Drawing.SystemIcons]::Warning
    $icono.Visible = $true
    $icono.BalloonTipTitle = 'TerraPapu'
    $icono.BalloonTipText = $env:TERRAPAPU_AVISO
    $icono.ShowBalloonTip(4000)
    Start-Sleep -Seconds 5
} finally {
    $icono.Dispose()
}
"""
    subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        env={**os.environ, "TERRAPAPU_AVISO": mensaje},
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
