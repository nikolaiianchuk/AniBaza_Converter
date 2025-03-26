@echo off
chcp 65001 >nul
:: Проверяем, запущен ли скрипт от имени администратора
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Запуск от имени администратора...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit
)

:: Установка пути к папке
set "ffmpeg_dir=C:\ffmpeg"
set "ffmpeg_bin=%ffmpeg_dir%\bin"

:: Проверяем, существует ли папка C:\ffmpeg
if exist "%ffmpeg_dir%" (
    echo Папка %ffmpeg_dir% уже существует.
    goto check_path
)

:: Скачиваем ffmpeg, если папка не существует
echo Скачивание ffmpeg...
curl -L -o ffmpeg.zip https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

:: Создаем папку для распаковки
mkdir "%ffmpeg_dir%"

:: Распаковываем ffmpeg в папку C:\ffmpeg
echo Распаковка ffmpeg...
tar -xf ffmpeg.zip -C "%ffmpeg_dir%" --strip-components=1

:: Удаляем скачанный архив
del ffmpeg.zip

:: Добавляем папку bin в PATH, если ее там нет
:check_path
echo Проверка наличия %ffmpeg_bin% в PATH...
echo %PATH% | findstr /I /C:"%ffmpeg_bin%" >nul
if errorlevel 1 (
    echo %ffmpeg_bin% не найден в PATH. Добавление...
    setx PATH "%ffmpeg_bin%;%PATH%"
) else (
    echo %ffmpeg_bin% уже присутствует в PATH.
)

:end
echo Установка завершена.
