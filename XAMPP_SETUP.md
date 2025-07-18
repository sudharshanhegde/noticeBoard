# XAMPP Setup and Troubleshooting Guide

## 🚀 Quick Setup Steps

### 1. Install Required Software
- **XAMPP**: Download from [https://www.apachefriends.org/](https://www.apachefriends.org/)
- **Strawberry Perl**: Download from [http://strawberryperl.com/](http://strawberryperl.com/)

### 2. Run Setup Script
1. Copy all files to your project directory
2. Run `setup_xampp.bat` as Administrator
3. Follow the prompts

### 3. Manual Setup (if script fails)

#### Copy Files to XAMPP:
```
Copy all files to: C:\xampp\htdocs\NoticeBoard\
```

#### Configure Apache:
Edit `C:\xampp\apache\conf\httpd.conf` and add:
```apache
# Enable CGI Module
LoadModule cgi_module modules/mod_cgi.so

# Add at the end of file
<Directory "C:/xampp/htdocs">
    Options +ExecCGI
    AddHandler cgi-script .cgi .pl
    AllowOverride All
</Directory>
```

#### Install Perl Modules:
```cmd
cpan install CGI CGI::Session XML::LibXML
```

## 🌐 Access URLs

- **View Notices**: `http://localhost/NoticeBoard/view_notices.cgi`
- **Admin Login**: `http://localhost/NoticeBoard/admin_login.cgi`
- **Admin Panel**: `http://localhost/NoticeBoard/admin_form_protected.cgi`

## 🔧 Common Issues and Solutions

### Issue 1: "Internal Server Error"
**Cause**: Perl path incorrect or CGI not enabled

**Solution**:
1. Check first line of .cgi files matches your Perl installation:
   ```perl
   #!C:\Strawberry\perl\bin\perl.exe
   ```
2. Verify CGI module is enabled in httpd.conf
3. Check Apache error logs: `C:\xampp\apache\logs\error.log`

### Issue 2: "Perl module not found"
**Cause**: Required modules not installed

**Solution**:
```cmd
# Open Command Prompt as Administrator
cpan install CGI CGI::Session XML::LibXML

# If cpan doesn't work, try:
ppm install CGI CGI-Session XML-LibXML
```

### Issue 3: "Permission denied" or "Access forbidden"
**Cause**: Directory permissions

**Solution**:
1. Ensure files are in `C:\xampp\htdocs\NoticeBoard\`
2. Check httpd.conf has correct Directory configuration
3. Restart Apache

### Issue 4: "Session doesn't work"
**Cause**: Cannot write to session directory

**Solution**:
1. Create directory: `C:\xampp\tmp\`
2. Or modify scripts to use Windows temp:
   ```perl
   my $session = CGI::Session->new("driver:File", undef, {Directory=>'C:/xampp/tmp'});
   ```

### Issue 5: "XML file not found"
**Cause**: File permissions or path issues

**Solution**:
1. Ensure `notices.xml` is in the same directory as CGI files
2. Check file permissions (should be readable/writable)
3. Run Apache as Administrator if needed

## 🔍 Testing Your Setup

### 1. Test Perl Installation
```cmd
perl -v
```

### 2. Test CGI Basic Functionality
Create test file `C:\xampp\htdocs\test.cgi`:
```perl
#!C:\Strawberry\perl\bin\perl.exe
print "Content-type: text/html\n\n";
print "Hello, Perl CGI works!";
```

Access: `http://localhost/test.cgi`

### 3. Test Required Modules
```cmd
perl -MCGI -e "print 'CGI OK'"
perl -MCGI::Session -e "print 'Session OK'"
perl -MXML::LibXML -e "print 'XML OK'"
```

## 📁 Directory Structure
```
C:\xampp\htdocs\NoticeBoard\
├── admin_login.cgi           # Login page
├── admin_form_protected.cgi  # Admin form (protected)
├── add_notice.cgi           # Add notice processor
├── view_notices.cgi         # View notices (public)
├── archive_notices.cgi      # Archive old notices
├── admin_form.html          # Original form (bypassed)
├── admin_style.css          # Styling
├── notices.xml              # Active notices
├── archive.xml              # Archived notices (auto-created)
└── README.md               # Documentation
```

## 🔐 Security Notes

- Default password: `admin123`
- Sessions stored in: `C:\xampp\tmp\` (or system temp)
- Change password in `admin_login.cgi`
- Session timeout: 1 hour

## 🚨 Troubleshooting Commands

```cmd
# Check Apache status
netstat -an | findstr :80

# View Apache processes
tasklist | findstr httpd

# Check Perl path
where perl

# Test module installation
perl -MCGI -e "print CGI->VERSION"

# View Apache error log
type C:\xampp\apache\logs\error.log
```

## 📞 Getting Help

If you encounter issues:
1. Check Apache error logs
2. Verify Perl installation and modules
3. Ensure correct file permissions
4. Test with simple CGI script first
5. Check XAMPP documentation

## 🎯 Production Tips

- Use proper error handling
- Set appropriate file permissions
- Regular backup of XML files
- Monitor Apache logs
- Consider using mod_perl for better performance
