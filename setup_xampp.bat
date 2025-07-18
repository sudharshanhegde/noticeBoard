@echo off
echo Setting up Notice Board System for XAMPP...
echo.

REM Check if XAMPP is installed
if not exist "C:\xampp\htdocs" (
    echo ERROR: XAMPP not found at C:\xampp\
    echo Please install XAMPP first from https://www.apachefriends.org/
    pause
    exit /b 1
)

REM Check if Perl is installed
perl -v >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Perl not found in PATH
    echo Please install Strawberry Perl from http://strawberryperl.com/
    pause
    exit /b 1
)

echo Creating project directory...
mkdir "C:\xampp\htdocs\NoticeBoard" 2>nul

echo Copying files to XAMPP htdocs...
copy "*.cgi" "C:\xampp\htdocs\NoticeBoard\" >nul 2>&1
copy "*.html" "C:\xampp\htdocs\NoticeBoard\" >nul 2>&1
copy "*.css" "C:\xampp\htdocs\NoticeBoard\" >nul 2>&1
copy "*.xml" "C:\xampp\htdocs\NoticeBoard\" >nul 2>&1
copy "*.md" "C:\xampp\htdocs\NoticeBoard\" >nul 2>&1

echo Installing required Perl modules...
echo This may take a few minutes...
cpan install CGI CGI::Session XML::LibXML

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Start Apache from XAMPP Control Panel
echo 2. Open your browser and go to: http://localhost/NoticeBoard/view_notices.cgi
echo 3. To access admin panel: http://localhost/NoticeBoard/admin_login.cgi
echo 4. Default password: admin123
echo.
echo If you encounter issues, check the Apache error logs at:
echo C:\xampp\apache\logs\error.log
echo.
pause
