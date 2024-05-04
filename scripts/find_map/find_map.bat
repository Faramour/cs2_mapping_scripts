:: Author: Faramour
:: Date: May 2024
::
:: Usage:
:: Script reads contents of 'publish_data.txt' inside directories of it's path and looks for string given by the user.
:: If string is found, addon ID and map name of the matched text file is returned and it's directory is opened in file explorer.
:: Script should be placed inside 'steamapps\workshop\content\730', or search_path should be changed accordingly.

@echo off

:: EDIT ME TO CHANGE SEARCH PATH
set "search_path=.\"

set /p "search_string=Enter the string to search for: "

for /d %%F in ("%search_path%\*") do (
    for /f "tokens=*" %%A in ('findstr /m /c:"%search_string%" "%%F\publish_data.txt"') do (
		set "folder_name=%%~nxF"
        echo Folder containing '%search_string%' is: %%~nxF
		for /f "usebackq tokens=1,* delims=:	" %%A in ("%%F\publish_data.txt") do (
			if %%A=="source_folder" (
				echo Source: %%B
			)
			if %%A=="title" (
				echo Title: %%B
			)
		)
		echo Opening folder...
		start "" "%%F"
		goto :found
    )
)

echo No matching folder found.
pause
goto :eof

:found

pause