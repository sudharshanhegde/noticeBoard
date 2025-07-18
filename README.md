# Notice Board System

A comprehensive web-based notice board management system built with Perl CGI, featuring admin authentication, archive management, and XML-based data storage.

## 🚀 Features

### Core Functionality

- **Admin Authentication**: Secure login system with session management
- **Notice Management**: Add, view, edit, and delete notices
- **Branch Filtering**: Filter notices by department/branch
- **Importance Levels**: Categorize notices by urgency (Low, Medium, High, Urgent, Critical)
- **Search Functionality**: Search notices by title and description
- **Responsive Design**: Works on desktop and mobile devices

### Archive System

- **Automatic Archiving**: Archive notices older than specified days (default: 30 days)
- **Manual Archive**: Select specific notices to archive
- **Archive Management**: View, search, and restore archived notices
- **Data Preservation**: All original fields (branch, importance, date) preserved in archive
- **Archive Metadata**: Track when and how notices were archived

### Technical Features

- **XML Storage**: Lightweight file-based data storage
- **Session Management**: 1-hour session timeout with automatic logout
- **Data Backup**: Automatic backup creation before any modifications
- **Input Validation**: Comprehensive form validation and sanitization
- **Error Handling**: Graceful error handling and user feedback

## 📋 Requirements

- **XAMPP**: Web server with Apache
- **Strawberry Perl**: Perl interpreter for Windows
- **Perl Modules**: CGI, CGI::Session, XML::LibXML, DateTime (optional for enhanced date handling)

## ⚡ Quick Setup

### Option 1: Automated Setup (Recommended)

1. **Download and install prerequisites:**

   - [XAMPP](https://www.apachefriends.org/) - Apache web server
   - [Strawberry Perl](http://strawberryperl.com/) - Perl interpreter

2. **Clone the repository:**

   ```bash
   git clone https://github.com/sudharshanhegde/noticeBoard.git
   cd noticeBoard
   ```

3. **Run the setup script as Administrator:**

   ```cmd
   setup_xampp.bat
   ```

4. **Start Apache** from XAMPP Control Panel

5. **Access the system:**
   - **View Notices**: `http://localhost/NoticeBoard/view_notices.cgi`
   - **Admin Login**: `http://localhost/NoticeBoard/admin_login.cgi`

### Option 2: Manual Setup

1. **Install XAMPP and Strawberry Perl** (see links above)

2. **Copy files** to `C:\xampp\htdocs\NoticeBoard\`

3. **Install Perl modules:**

   ```cmd
   cpan install CGI CGI::Session XML::LibXML
   ```

4. **Configure Apache** (if needed):
   - Edit `C:\xampp\apache\conf\httpd.conf`
   - Ensure CGI module is loaded and ExecCGI is enabled

## 🖥️ Usage

### Admin Access

1. **Login**: Navigate to `http://localhost/NoticeBoard/admin_login.cgi`
2. **Password**: `admin123` (change this in `admin_login.cgi`)
3. **Add Notice**: Fill out the form and submit
4. **Archive Management**: Access archive dashboard for notice lifecycle management
5. **Logout**: Click the logout link in the admin panel

### Public Access

- **View Notices**: `http://localhost/NoticeBoard/view_notices.cgi`
- **Filter by Branch**: Use the dropdown to filter notices by department
- **Filter by Importance**: Filter notices by urgency level
- **Search**: Use the search box to find specific notices

### Archive Management

#### Web Interface

- **Archive Dashboard**: `http://localhost/NoticeBoard/archive_notices.cgi`
- **View Archived**: Browse all archived notices with restore functionality
- **Auto Archive**: Automatically archive notices older than specified days
- **Manual Archive**: Select specific notices to archive
- **Restore**: Move archived notices back to active status

#### Command Line

```bash
# Run archive system test
perl test_archive.pl

# Auto-archive old notices
perl notice_archive.pl

# Manual operations (from Perl scripts)
archive_notices_by_id(1, 2, 3);          # Archive specific notices
restore_notices_from_archive(1, 2, 3);    # Restore specific notices
```

### Archive Features

#### Automatic Archiving

- **Default**: Archives notices older than 30 days
- **Configurable**: Change the day limit through web interface or configuration
- **Preserves Data**: All original fields (title, date, description, branch, importance) preserved
- **Adds Metadata**: Tracks archive date and who archived it

#### Manual Management

- **Selective Archiving**: Choose specific notices to archive
- **Bulk Operations**: Archive multiple notices at once
- **Restore Functionality**: Bring archived notices back to active status
- **Search & Filter**: Find archived notices by branch, importance, or text search

#### Data Structure

```xml
<!-- Active Notice -->
<notice id="1">
    <title>Notice Title</title>
    <date>2025-07-18</date>
    <description>Notice description</description>
    <branch>cse</branch>
    <importance>high</importance>
</notice>

<!-- Archived Notice (with additional metadata) -->
<notice id="1">
    <title>Notice Title</title>
    <date>2025-07-18</date>
    <description>Notice description</description>
    <branch>cse</branch>
    <importance>high</importance>
    <archived_date>2025-08-18 14:30:00</archived_date>
    <archived_by>admin</archived_by>
</notice>
```

## 🔐 Security

- **Session-based authentication** with 1-hour timeout
- **Password protection** for all admin functions
- **Automatic logout** functionality
- **Input validation** and sanitization

## 📁 Project Structure

```
NoticeBoard/
├── admin_login.cgi          # Login page and authentication
├── admin_form_protected.cgi # Protected admin form
├── add_notice.cgi          # Notice processing script
├── view_notices.cgi        # Public notice viewer
├── archive_notices.cgi     # Archive management system
├── notices.xml             # Active notices database
├── archive.xml             # Archived notices database
├── admin_style.css         # Styling for all pages
├── setup_xampp.bat         # Automated setup script
├── notice_archive.pl       # Archive system library
├── test_archive.pl         # Archive system test script
├── .gitignore             # Git ignore file
└── README.md              # This documentation
```

## 🔧 Configuration

### Change Admin Password

Edit `admin_login.cgi` and modify:

```perl
my $ADMIN_PASSWORD = "your_secure_password_here";
```

### Configure Archive Settings

Edit `notice_archive.pl` and modify:

```perl
my $ARCHIVE_DAYS = 30;  # Change default archive days
```

### Customize Branches

Edit the branch options in `admin_form_protected.cgi`:

```html
<option value="your_branch">Your Branch Name</option>
```

### Session Configuration

Edit session timeout in any CGI script:

```perl
my $SESSION_TIMEOUT = 3600;  # 1 hour in seconds
```

## 🧪 Testing

### Run Archive System Test

```bash
perl test_archive.pl
```

### Manual Testing URLs

- **Public View**: `http://localhost/NoticeBoard/view_notices.cgi`
- **Admin Login**: `http://localhost/NoticeBoard/admin_login.cgi`
- **Admin Panel**: `http://localhost/NoticeBoard/admin_form_protected.cgi`
- **Archive Dashboard**: `http://localhost/NoticeBoard/archive_notices.cgi`
- **View Archived**: `http://localhost/NoticeBoard/archive_notices.cgi?action=view_archived`

### Test Data

The system comes with sample notices for testing:

- 6 sample notices covering different branches and importance levels
- Dates ranging from recent to older notices
- Various content types (exams, workshops, maintenance, etc.)

## 🐛 Troubleshooting

### Common Issues

**"Internal Server Error"**

- Check if Perl is installed and in PATH
- Verify Apache CGI module is enabled
- Check Apache error logs at `C:\xampp\apache\logs\error.log`

**"Session not working"**

- Ensure `/tmp` directory exists and is writable
- Check if CGI::Session module is installed
- Clear browser cache/cookies if experiencing login issues

**"Cannot add notices"**

- Verify file permissions on `notices.xml`
- Check if XML::LibXML module is installed
- Ensure Apache has write permissions to the project directory

**"Archive system not working"**

- Check if DateTime module is installed: `cpan install DateTime`
- Verify `archive.xml` file permissions
- Check if backup files (`.bak`) are being created

### Module Installation

If you encounter missing module errors:

```bash
# Install all required modules
cpan install CGI CGI::Session XML::LibXML DateTime

# Or install individually
cpan install CGI
cpan install CGI::Session
cpan install XML::LibXML
cpan install DateTime
```

### Debug Mode

Enable debugging in CGI scripts by adding:

```perl
use CGI::Carp qw(fatalsToBrowser);
```

## 📈 Performance & Scalability

### Current Limitations

- **File-based storage**: Suitable for small to medium datasets (< 10,000 notices)
- **No indexing**: Search is linear through XML files
- **Single-user sessions**: One admin user at a time

### Performance Tips

- **Regular archiving**: Keep active notices under 1,000 for optimal performance
- **Periodic cleanup**: Remove old backup files (.bak) periodically
- **Static content**: Consider using web server for CSS/JS files

### Scaling Options

- **Database migration**: Move to MySQL/PostgreSQL for larger datasets
- **Caching**: Implement file-based caching for frequently accessed data
- **Load balancing**: Deploy multiple instances for high availability

## 🔄 Backup & Recovery

### Automatic Backups

- **XML backups**: Created automatically before any modifications
- **Location**: Same directory as original files with `.bak` extension
- **Retention**: Keep recent backups for disaster recovery

### Manual Backup

```bash
# Backup all data files
copy notices.xml notices_backup.xml
copy archive.xml archive_backup.xml

# Backup entire project
xcopy /E /I NoticeBoard NoticeBoard_backup
```

### Recovery Process

1. **Stop Apache** to prevent data corruption
2. **Restore from backup**: Copy `.bak` files to original names
3. **Verify integrity**: Check XML file structure
4. **Restart Apache** and test functionality

## 📄 License

This project is developed for educational purposes at UVCE (University Visvesvaraya College of Engineering).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow Perl best practices
- Include error handling for all functions
- Document new features in README
- Test thoroughly before submitting

## 📧 Support

For issues and questions:

- **GitHub Issues**: Open an issue on the repository
- **Documentation**: Check this README and code comments
- **Testing**: Use the provided test scripts for debugging

## 🚀 Future Enhancements

### Planned Features

- **Email notifications**: Send email alerts for new notices
- **User roles**: Different access levels (admin, editor, viewer)
- **Rich text editor**: WYSIWYG editor for notice descriptions
- **File attachments**: Support for PDF and image attachments
- **API endpoints**: RESTful API for external integrations
- **Mobile app**: Native mobile application
- **Analytics**: Usage statistics and reporting

### Technical Improvements

- **Database migration**: Move from XML to SQL database
- **Caching layer**: Implement Redis or Memcached
- **Unit tests**: Comprehensive test coverage
- **CI/CD pipeline**: Automated testing and deployment
- **Docker support**: Containerized deployment option

---

**Made with ❤️ for UVCE by the Notice Board Team**

- Dates ranging from recent to older notices
- Various content types (exams, workshops, maintenance, etc.)
  ├── notices.xml # Active notices database
  ├── admin_style.css # Styling
  ├── setup_xampp.bat # Automated setup script
  └── README.md # This file

````

## 🛠️ Configuration

### Change Admin Password

Edit `admin_login.cgi` and modify:

```perl
my $ADMIN_PASSWORD = "your_secure_password_here";
````

### Customize Branches

Edit the branch options in `admin_form_protected.cgi`:

```html
<option value="your_branch">Your Branch Name</option>
```

## 🐛 Troubleshooting

**"Internal Server Error"**

- Check if Perl is installed and in PATH
- Verify Apache CGI module is enabled
- Check Apache error logs at `C:\xampp\apache\logs\error.log`

**"Session not working"**

- Ensure `/tmp` directory exists and is writable
- Check if CGI::Session module is installed

**"Cannot add notices"**

- Verify file permissions on `notices.xml`
- Check if XML::LibXML module is installed

## 📄 License

This project is developed for educational purposes at UVCE.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues and questions, please open an issue on GitHub.
