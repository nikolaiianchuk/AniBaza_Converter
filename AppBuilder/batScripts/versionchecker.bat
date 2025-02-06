@echo off
chcp 65001 >nul
:: Проверка наличия curl
curl --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Утилита curl не установлена. Пожалуйста, установите curl и попробуйте снова.
    pause
    exit /b
)

:: Скачивание страницы с информацией о релизах FFmpeg
curl -s https://ffmpeg.org/download.html > "%TEMP%\ffmpeg_version.html"

:: Поиск последней версии в формате "X.X" или "X.X.X was released"
for /f "tokens=1,2" %%a in ('findstr /r /c:"[0-9]\+\.[0-9]\+\(\.[0-9]\+\)\? was released" "%TEMP%\ffmpeg_version.html"') do (
    set latest_version=%%a
    goto output
)

:output
:: Вывод версии
if defined latest_version (
    echo Последняя версия FFmpeg: %latest_version%
) else (
    echo Не удалось определить последнюю версию FFmpeg.
)

:: Удаление временного файла
del "%TEMP%\ffmpeg_version.html"

pause
