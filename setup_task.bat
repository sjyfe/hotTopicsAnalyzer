@echo off
echo 正在设置热点数据分析与推送系统的定时任务...

REM 创建运行脚本
echo @echo off > run_analyzer.bat
echo cd /d "%~dp0" >> run_analyzer.bat
echo python hot_topics_analyzer.py >> run_analyzer.bat

REM 设置定时任务 - 每天上午9点和下午5点运行
schtasks /create /tn "热点数据分析与推送" /tr "%~dp0run_analyzer.bat" /sc daily /st 09:00 /du 0001:00 /f
schtasks /create /tn "热点数据分析与推送(下午)" /tr "%~dp0run_analyzer.bat" /sc daily /st 17:00 /du 0001:00 /f

echo 定时任务设置完成!
echo 系统将在每天上午9点和下午5点自动运行热点数据分析与推送。
echo.
echo 您可以通过Windows任务计划程序查看和修改这些任务。
pause 