Instructions for programming firmware via JTAG.

****
****
**** This is for power users, who need to bring up custom hardware or recover bricked hardware.
**** Do not proceed unless you know what you are doing.
**** To upgrade the firmware on your HDK, you should be using hdk_firmware_update.bat ( lightouse_watchman_update.exe ).
****
**** Backup your JSON file before every firmware update.
****
****

Download and install the latest J-Link.exe:  https://www.segger.com/downloads/jlink/JLink_Windows_V600i.zip

To flash SAMG55:
C:\> flash_mcu.bat <j-link s/n> watchman_v3_hdk_jtag.bin

To flash nRF52:
C:\> flash_radio.bat <j-link s/n> \watchman_v3_hdk_radio.bin

*****
***** Please power cycle the device after JTAG
*****

