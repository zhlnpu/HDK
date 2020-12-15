@echo off
echo.

REM
REM This .bat file programs Watchman firmware onto the MCU (SAMG55) 
REM or radio (nRF52), using a Segger J-Link.
REM
REM It requires:
REM . J-Link Serial Number
REM . Firmware binary filename
REM
REM example:
REM
REM   C:\> flash_radio.bat 59304899 watchman_v3_cm_radio.bin
REM

SET SEGGER_PATH=c:\Program Files (x86)\SEGGER\JLink_V600i

rem settings for the Radio J-Link
SET RADIO_SN=%1
SET RADIO_FILENAME=%2
SET RADIO_DEVICE=NRF52832_XXAA
SET RADIO_INTERFACE=SWD
SET RADIO_SPEED=5000
SET RADIO_ERASE_CMDFILE=radio_erase.jlink
SET RADIO_FLASH_CMDFILE=radio_flash.jlink
SET RADIO_VERIFY_CMDFILE=radio_verify.jlink

echo tools path: %SEGGER_PATH%

rem J-Link serial number is required
IF [%RADIO_SN%] EQU [] (
    echo error, no jlink serial number provided
    echo flash_mcu.bat ^<j-link serial-number^> ^<binary^>
    exit /b -2
)

rem Path to MCU binary is required
IF [%RADIO_FILENAME%] EQU [] (
    echo error, no path to MCU binary provided
    echo flash_mcu.bat ^<j-link serial-number^> ^<binary^>
    exit /b -3
)

rem we are creating the cmdfile dyamically so delete the old one
IF exist %RADIO_FLASH_CMDFILE% (
    echo found stale cmdfile "%RADIO_FLASH_CMDFILE%", deleting
    del /f %RADIO_FLASH_CMDFILE%
)
IF exist %RADIO_VERIFY_CMDFILE% (
    echo found stale cmdfile "%RADIO_VERIFY_CMDFILE%", deleting
    del /f %RADIO_VERIFY_CMDFILE%
)

rem build the flash cmdfile
echo generating flash cmdfile
echo h >> %RADIO_FLASH_CMDFILE%
echo loadfile %RADIO_FILENAME% >> %RADIO_FLASH_CMDFILE%
echo h >> %RADIO_FLASH_CMDFILE%
echo q >> %RADIO_FLASH_CMDFILE%

rem build the verify cmdfile
echo generating verify cmdfile
echo h >> %RADIO_VERIFY_CMDFILE%
echo verify %RADIO_FILENAME% >> %RADIO_VERIFY_CMDFILE%
echo h >> %RADIO_VERIFY_CMDFILE%
echo q >> %RADIO_VERIFY_CMDFILE%

echo connecting to device SN=%RADIO_SN%, flashing image %RADIO_FILENAME%...

rem these need to be done as two separate steps, otherwise they don't always complete successfully

echo erasing
"%SEGGER_PATH%\JLink.exe" ^
-selectemubysn %RADIO_SN% ^
-device %RADIO_DEVICE% ^
-if %RADIO_INTERFACE% ^
-speed %RADIO_SPEED% ^
-commandfile %RADIO_ERASE_CMDFILE%

echo flashing
"%SEGGER_PATH%\JLink.exe" ^
-selectemubysn %RADIO_SN% ^
-device %RADIO_DEVICE% ^
-if %RADIO_INTERFACE% ^
-speed %RADIO_SPEED% ^
-commandfile %RADIO_FLASH_CMDFILE%

echo verifying
"%SEGGER_PATH%\JLink.exe" ^
-selectemubysn %RADIO_SN% ^
-device %RADIO_DEVICE% ^
-if %RADIO_INTERFACE% ^
-speed %RADIO_SPEED% ^
-commandfile %RADIO_VERIFY_CMDFILE%

echo flash complete
echo.

