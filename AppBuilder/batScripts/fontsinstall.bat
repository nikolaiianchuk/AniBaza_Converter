@echo off
chcp 65001 >nul
:: Устанавливаем переменную для папки с шрифтами
set "fontDir=%~dp0fonts"

:: Проверяем, существует ли папка с шрифтами
if not exist "%fontDir%" (
    echo Папка "fonts" не найдена!
    pause
    exit /b 1
)

:: Копируем шрифты в системную папку шрифтов
echo Копирование шрифтов в системную папку...
xcopy "%fontDir%\*.*" "%WINDIR%\Fonts" /Y

:: Регистрация шрифтов в реестре
echo Регистрация шрифтов в системе...
for %%f in ("%fontDir%\*.ttf" "%fontDir%\*.otf") do (
    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "%%~nf (TrueType)" /t REG_SZ /d "%%~nxf" /f
)

echo Установка завершена!
pause  :: Ожидаем нажатия клавиши