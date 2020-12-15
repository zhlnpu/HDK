REM  package.bat
REM
REM  This script packages the hmd_designer_gui application along
REM  with any required binary tools into a zipped archive for
REM  distribution.
REM  It is expected that this file runs from the root of the
REM  hmd_designer_gui directory.

set year=%date:~10,4%
set month=%date:~4,2%
set day=%date:~7,2%
set foldername="hmd_designer_gui %year%-%month%-%day%"

REM Make the package directory
mkdir %foldername%

REM Required files to package
copy *.py %foldername%
copy *.ui %foldername%
copy *.scad %foldername%

xcopy /E tools %foldername%\tools\
xcopy /E documentation %foldername%\documentation\
xcopy /E before_launch %foldername%\before_launch\
xcopy /E .idea %foldername%\.idea\

REM Delete unwanted files from the package
del %foldername%\.idea\workspace.xml
