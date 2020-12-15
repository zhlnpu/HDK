@echo off
@echo.
@echo HDK Firmware Updating Script - 2017.07.10 release
@echo  - This script requires devices to be running firmware prior to the 2017.07.10 release
@echo  - It is highly recommended to back up your JSON config file prior to updating your device
@echo  - Please ensure that no other SteamVR devices are connected to the system including:
@echo      wireless dongles, head-mounted displays, or other controllers
@echo  - Please connect your HDK device to the PC via USB
@echo.
@echo This script will perform 5 sequential updates and will take approximately 75 seconds to complete
@echo.

:confirm
set /P c=Are you ready to proceed with the update? (y)es, (n)o: 
@echo.
if /I "%c%" EQU "Y" goto :runupdates
if /I "%c%" EQU "y" goto :runupdates
if /I "%c%" EQU "N" goto :stop
if /I "%c%" EQU "n" goto :stop
goto :confirm

:stop
@echo Cancelling update.
@echo.
goto :exit

:runupdates
@echo -- Updating Bootloader --
.\lighthouse_watchman_update_20170710.exe -Mw3 bootloader_updating_app.bin
timeout /nobreak /t 10

@echo -- Updating Application --
.\lighthouse_watchman_update_20170710.exe --target=application application_20170710.fw
timeout /nobreak /t 10

@echo -- Updating FPGA --
.\lighthouse_watchman_update_20170710.exe --target=ice40 ice40_20170608v1_10.fw
timeout /nobreak /t 10

@echo -- Updating Radio --
.\lighthouse_watchman_update_20170710.exe --target=nrf52 nrf52_20170117.fw
timeout /nobreak /t 10

@echo -- Updating Fuel Gauge --
.\lighthouse_watchman_update_20170710.exe --target=bq27520 bq27520_hcp902248nfc_20170519v0001.fw
timeout /nobreak /t 15

@echo.
@echo.
@echo *** Updates completed. Please power cycle your device. ***
@echo.
@echo.

:exit