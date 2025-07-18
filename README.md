# Notice Board System - Password Protection

## Overview

The Notice Board system now includes password protection for admin functions. Only authorized users can access the admin panel to add notices or archive old ones.

## Default Credentials

- **Username**: No username required
- **Password**: `admin123` (Change this in the admin_login.cgi file)

## Protected Pages

- `admin_form_protected.cgi` - Add new notices (requires login)
- `add_notice.cgi` - Process form submissions (requires login)
- `archive_notices.cgi` - Archive old notices (requires login)

## Public Pages

- `view_notices.cgi` - View current notices (public access)
- `admin_login.cgi` - Login page (public access)

## Security Features

- Session-based authentication
- 1-hour session timeout
- Automatic logout functionality
- Protected admin functions
- Password field security (cleared on page load)

## Installation Requirements

Make sure you have the following Perl modules installed:

```bash
cpan install CGI CGI::Session XML::LibXML
```

## Setup Instructions

1. Make all CGI scripts executable:

   ```bash
   chmod +x *.cgi
   ```

2. Ensure your web server can execute CGI scripts and write to `/tmp` directory for sessions.

3. Change the default password in `admin_login.cgi`:
   ```perl
   my $ADMIN_PASSWORD = "your_secure_password_here";
   ```

## Usage

1. **To add notices**: Visit `admin_form_protected.cgi` (will redirect to login if not authenticated)
2. **To view notices**: Visit `view_notices.cgi` (public access)
3. **To archive notices**: Visit `archive_notices.cgi` (requires login)
4. **To logout**: Click the "Logout" link in the admin panel

## File Structure

```
admin_login.cgi          - Login page and authentication handler
admin_form_protected.cgi - Protected admin form
admin_form.html          - Original form (now bypassed)
add_notice.cgi          - Form processor (now protected)
view_notices.cgi        - Public notice viewer
archive_notices.cgi     - Archive manager (now protected)
notices.xml             - Active notices database
archive.xml             - Archived notices database
admin_style.css         - Styling for all pages
```

## Security Notes

- Sessions are stored in `/tmp` directory
- Session timeout is set to 1 hour
- All admin functions check authentication before processing
- Backup files are created before any XML modifications
- Login attempts can be logged by modifying the login script

## Troubleshooting

- If you can't log in, check that the `/tmp` directory is writable
- If sessions don't work, verify CGI::Session module is installed
- Clear browser cache/cookies if experiencing login issues
- Check web server error logs for detailed error messages
