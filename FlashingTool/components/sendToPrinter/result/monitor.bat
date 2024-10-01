@echo off
setlocal enabledelayedexpansion

set "folder_to_monitor=Z:"
set "printer_name=POSTEK G6000"

:loop
:: Monitor for new .png files
for %%f in ("%folder_to_monitor%\*.png") do (
    echo %%f
    if not exist "%%f.printed" (
        echo New file detected: %%~nxf
        echo Printing %%~nxf...
        echo %%f
	"E:\Program Files (x86)\postek\IrfanView\i_view64.exe" "%%f" /print="!printer_name!"

	:: Introduce a small delay to ensure IrfanView is done with the file
        timeout /t 5 /nobreak >nul
		
	:: Move the file to the archive folder
	move /Y "%%f" "%folder_to_monitor%\printed\"
	if errorlevel 1 (
            echo ERROR: Failed to move file %%~nxf
        ) else (
            echo File %%~nxf moved to printed folder
        )
    )
)

:: Sleep 10 seconds
timeout /t 10 /nobreak >nul

goto loop
