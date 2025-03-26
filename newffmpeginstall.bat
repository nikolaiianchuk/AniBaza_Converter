@echo off
chcp 65001 >nul
set "logFile=%~dp0install_ffmpeg.log"
set "pathChanged=0"

:: Очищаем лог перед запуском
echo. > "%logFile%" 2>&1
echo ------------------------------------ >> "%logFile%"
echo Запуск установки FFmpeg: %DATE% %TIME% >> "%logFile%"
echo ------------------------------------ >> "%logFile%"

:: Проверяем, запущен ли скрипт от имени администратора
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Запуск от имени администратора... >> "%logFile%"
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit
)

:: Установка пути к папке
set "ffmpeg_dir=C:\ffmpeg"
set "ffmpeg_bin=%ffmpeg_dir%\bin"

:: Проверяем, существует ли папка C:\ffmpeg
if exist "%ffmpeg_dir%" (
    echo Папка %ffmpeg_dir% уже существует. >> "%logFile%"
    goto check_path
)

:: Скачиваем ffmpeg, если папка не существует
echo Скачивание ffmpeg... >> "%logFile%"
curl -# -L -o ffmpeg.zip https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip >> "%logFile%" 2>&1

:: Проверяем, скачался ли файл
if not exist "ffmpeg.zip" (
    echo Ошибка: файл ffmpeg.zip не был скачан! >> "%logFile%"
    exit /b 2
)

:: Создаем папку для распаковки
mkdir "%ffmpeg_dir%" >> "%logFile%" 2>&1

:: Распаковываем ffmpeg в папку C:\ffmpeg
echo Распаковка ffmpeg... >> "%logFile%"
tar -xf ffmpeg.zip -C "%ffmpeg_dir%" --strip-components=1 >> "%logFile%" 2>&1

:: Проверяем, успешно ли распакован ffmpeg
if not exist "%ffmpeg_bin%\ffmpeg.exe" (
    echo Ошибка: ffmpeg.exe не найден после распаковки! >> "%logFile%"
    exit /b 2
)

:: Удаляем скачанный архив
del ffmpeg.zip >> "%logFile%" 2>&1

:: Добавляем папку bin в PATH, если ее там нет
:check_path
echo Проверка наличия %ffmpeg_bin% в PATH... >> "%logFile%"

echo %PATH% | findstr /I /C:"%ffmpeg_bin%" >nul
if errorlevel 1 (
    echo %ffmpeg_bin% не найден в PATH. Добавление... >> "%logFile%"
    setx PATH "%ffmpeg_bin%;%PATH%" >> "%logFile%" 2>&1
    set "pathChanged=1"
) else (
    echo %ffmpeg_bin% уже присутствует в PATH. >> "%logFile%"
)

:end
echo Установка завершена. >> "%logFile%"

:: Завершаем скрипт с кодом 1, если изменился PATH
exit /b %pathChanged%
