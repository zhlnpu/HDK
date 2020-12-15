@echo off

@echo -- Updating MCU --
..\..\tools\bin\win32\lighthouse_watchman_update.exe -Mw3 watchman_v3_hdk_mcu.bin

@echo -- Updating FPGA --
timeout /nobreak /t 5
..\..\tools\bin\win32\lighthouse_watchman_update.exe -fw3 watchman_v3_hdk_fpga.bin

@echo -- Updating Radio --
timeout /nobreak /t 5
..\..\tools\bin\win32\lighthouse_watchman_update.exe -rw3 watchman_v3_hdk_radio.bin

@echo 
@echo
@echo *** Please power cycle your device ***
@echo
@echo
