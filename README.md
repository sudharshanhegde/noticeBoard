# Notice Board System

A web-based notice board management system built with Perl CGI, featuring admin authentication and XML-based data storage.

## 🚀 Features

- **Admin Authentication**: Secure login system with session management
- **Notice Management**: Add, view, and archive notices
- **Branch Filtering**: Filter notices by department/branch
- **Importance Levels**: Categorize notices by urgency (Low, Medium, High, Urgent, Critical)
- **Responsive Design**: Works on desktop and mobile devices
- **XML Storage**: Lightweight file-based data storage

## 📋 Requirements

- **XAMPP**: Web server with Apache
- **Strawberry Perl**: Perl interpreter for Windows
- **Perl Modules**: CGI, CGI::Session, XML::LibXML

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
4. **Logout**: Click the logout link in the admin panel

### Public Access

- **View Notices**: `http://localhost/NoticeBoard/view_notices.cgi`
- **Filter by Branch**: Use the dropdown to filter notices
- **Search**: Use the search box to find specific notices

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
├── archive_notices.cgi     # Archive management
├── notices.xml             # Active notices database
├── admin_style.css         # Styling
├── setup_xampp.bat         # Automated setup script
└── README.md              # This file
```

## 🛠️ Configuration

### Change Admin Password

Edit `admin_login.cgi` and modify:
```perl
my $ADMIN_PASSWORD = "your_secure_password_here";
```

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
