@echo off
chcp 65001 >nul
set "logFile=%~dp0install_fonts.log"
echo. > "%logFile%" 2>&1

:: Функция логирования
echo ------------------------------------ >> "%logFile%"
echo Запуск: %DATE% %TIME% >> "%logFile%"
echo ------------------------------------ >> "%logFile%"

:: Проверяем, запущен ли скрипт от имени администратора
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Запуск от имени администратора... >> "%logFile%"
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit
)

:: Устанавливаем переменную для папки с шрифтами
set "fontDir=%~dp0fonts"

:: Проверяем, существует ли папка с шрифтами
if not exist "%fontDir%" (
    echo Папка "fonts" не найдена! >> "%logFile%"
    exit /b 2
)

:: Копирование и регистрация шрифтов
set "fontRegPath=HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
set "fontsCopied=0"
set "fontsRegistered=0"

echo Проверка и установка шрифтов... >> "%logFile%"

for %%f in ("%fontDir%\*.ttf" "%fontDir%\*.otf") do (
    set "fontName=%%~nf"
    set "fontFile=%%~nxf"

    :: Проверяем, зарегистрирован ли шрифт в реестре
    reg query "%fontRegPath%" /v "%%~nf (TrueType)" >nul 2>&1
    if %errorLevel% neq 0 (
        echo Регистрируем %%~nf... >> "%logFile%"
        reg add "%fontRegPath%" /v "%%~nf (TrueType)" /t REG_SZ /d "%%~nxf" /f >> "%logFile%" 2>&1
        set /a fontsRegistered+=1
    ) else (
        echo Шрифт %%~nf уже зарегистрирован. >> "%logFile%"
    )

    :: Проверяем, скопирован ли шрифт в системную папку
    if not exist "%WINDIR%\Fonts\%%~nxf" (
        echo Копируем %%~nf... >> "%logFile%"
        copy /Y "%%f" "%WINDIR%\Fonts\" >> "%logFile%" 2>&1
        set /a fontsCopied+=1
    ) else (
        echo Шрифт %%~nf уже установлен. >> "%logFile%"
    )
)

echo Установлено новых шрифтов: %fontsCopied% >> "%logFile%"
echo Зарегистрировано новых шрифтов: %fontsRegistered% >> "%logFile%"

if %fontsCopied% equ 0 if %fontsRegistered% equ 0 (
    echo Все шрифты уже установлены и зарегистрированы. Перезапуск не требуется. >> "%logFile%"
    set "statusCode=0"
) else (
    echo Установка завершена! Возможно, потребуется перезагрузка системы. >> "%logFile%"
    set "statusCode=1"
)

exit /b %statusCode%
