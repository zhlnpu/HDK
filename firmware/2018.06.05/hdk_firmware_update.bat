@echo off
@echo.
@echo HDK Firmware Updating Script - 2018.06.05 release
@echo  - This script requires devices to be running releases dated 2017.07.10 or after
@echo  - It is highly recommended that you back up your JSON config file prior to updating your device
@echo  - Please ensure that no other SteamVR devices are connected to the system including:
@echo      wireless dongles, head-mounted displays, or other controllers
@echo  - Please connect your HDK device to the PC via USB
@echo.
@echo This script will perform 5 sequential updates and will take approximately 60 seconds to complete
@echo.

:confirm
set /P c=Are you ready to proceed with the update? (y)es, (n)o: 
@echo.
if /I "%c%" EQU "Y" goto :check_compatibility
if /I "%c%" EQU "y" goto :check_compatibility
if /I "%c%" EQU "N" goto :stop
if /I "%c%" EQU "n" goto :stop
goto :confirm

:check_compatibility
@echo Verifying compatibility, please wait...
@echo.
..\..\tools\bin\win32\lighthouse_watchman_update.exe -bw3 >nul 2>&1
timeout /t 5 /nobreak > nul

set version_cmd='..\..\tools\bin\win32\lighthouse_watchman_update.exe -aw3'

set /a hwid_current=0
set /a product_id_required=90000000

set /a bl_version_current=0
set /a bl_version_required=1499703706

for /F "Tokens=1,3 delims= " %%A in (%version_cmd%) do (
  if "%%A"=="Hardware" (set /a hwid_current=%%B)
  if "%%A"=="Bootloader" (set /a bl_version_current=%%B)
)

set /a "product_id_current=%hwid_current%-(%hwid_current% %% 10000000)"  
set /a "sensor_type=(%hwid_current% %% 10)"  

if %product_id_current% NEQ %product_id_required% goto :bad_hwid
if %bl_version_current% LSS %bl_version_required% goto :bad_bl_version

@echo Compatibility checks passed. Proceeding with update
@echo.

@echo -- Updating Application --
..\..\tools\bin\win32\lighthouse_watchman_update.exe --target=application application_20180605.fw
timeout /nobreak /t 4

@echo -- Updating Bootloader --
..\..\tools\bin\win32\lighthouse_watchman_update.exe --target=bootloader bootloader_20180605.fw
timeout /nobreak /t 4

@echo -- Updating FPGA --
..\..\tools\bin\win32\lighthouse_watchman_update.exe --target=ice40 ice40cm_20180123v2_19.fw
timeout /nobreak /t 4

@echo -- Updating Radio --
if %sensor_type% EQU 6 (set radio_binary=nrf52_20180215v6.fw) else (set radio_binary=nrf52_20170117.fw)
..\..\tools\bin\win32\lighthouse_watchman_update.exe --target=nrf52 %radio_binary%
timeout /nobreak /t 4

@echo -- Updating Fuel Gauge --
..\..\tools\bin\win32\lighthouse_watchman_update.exe --target=bq27520 bq27520_hcp902248nfc_20170519v0001.fw
timeout /nobreak /t 20

@echo.
@echo.
@echo *** Updates completed. Please power cycle your device. ***
@echo.
@echo.
goto :exit

:bad_hwid
@echo Invalid hardware ID! Please ensure only your target HDK device is connected (including HMDs)
goto :stop

:bad_bl_version:
@echo Bootloader version invalid or old! Please update to firmware version 2017.07.10 prior to running this script
goto :stop

:stop
@echo Cancelling update.
@echo.
..\..\tools\bin\win32\lighthouse_watchman_update.exe -Rw3 >nul 2>&1
goto :exit

:exit
pause
