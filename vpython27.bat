@echo off
:: Batch file to execute a python script under the official Valve Python environment.
:: This needs to work regardless of any user configuration.

:: Save off local environment variables so the changes we make here don't hose
:: any uer config
SETLOCAL

:: Clear some variables that we don't need and might screw us up.
SET PYTHON=
SET PYTHONPATH=
SET PYTHONSTARTUP=
SET PYTHONNOUSERSITE=
SET PYTHONNOUSERBASE=

:: Set PYTHONHOME by changing to the 2.7 directory using a directory
:: relative to the batch file.
:: NOTE: This might need to differ between branches!
PUSHD .
%~d0
CD "%~d0%~p0python27"
SET PYTHONHOME=%CD%
POPD
::echo PYTHONHOME=%PYTHONHOME% 

:: Shove it at the front of the path, just to make sure we always take priority over
:: any other existing python installation in case something else ends up executing
:: "python.exe" or needs to locate some DLLs
SET PATH=%PYTHONHOME%;%PATH%

:: Set the path to TCL for Matplotlib
SET TCL_LIBRARY=%PYTHONHOME%\tcl\tcl8.5
SET TK_LIBRARY=%PYTHONHOME%\tcl\tcl8.5

:: Execute Python
::echo %PYTHONHOME%\python.exe %*
"%PYTHONHOME%\python.exe" %*
