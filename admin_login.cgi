#!C:\Strawberry\perl\bin\perl.exe

use strict;
use warnings;
use CGI;
use CGI::Session;
use Digest::MD5 qw(md5_hex);

# Configuration
my $ADMIN_PASSWORD = "admin123";  # Change this to your desired password
my $SESSION_TIMEOUT = 3600;      # Session timeout in seconds (1 hour)

# Create CGI object
my $cgi = CGI->new;

# Initialize session
my $session = CGI::Session->new("driver:File", $cgi, {Directory=>'/tmp'});

# Get action parameter
my $action = $cgi->param('action') || '';

# Handle logout
if ($action eq 'logout') {
    $session->delete();
    $session->flush();
    print $cgi->redirect(-uri => 'admin_login.cgi');
    exit;
}

# Handle login attempt
if ($action eq 'login') {
    my $password = $cgi->param('password') || '';
    
    if ($password eq $ADMIN_PASSWORD) {
        # Successful login
        $session->param('authenticated', 1);
        $session->param('login_time', time());
        $session->expire($SESSION_TIMEOUT);
        
        # Set session cookie and redirect to admin form
        my $cookie = $cgi->cookie(-name => 'CGISESSID', -value => $session->id);
        print $cgi->header(-type => 'text/html', -charset => 'UTF-8', -cookie => $cookie);
        print qq{
            <html>
            <head>
                <meta http-equiv="refresh" content="1;url=admin_form_protected.cgi">
                <title>Login Successful</title>
            </head>
            <body>
                <p>Login successful! Redirecting...</p>
                <script>window.location.href = 'admin_form_protected.cgi';</script>
            </body>
            </html>
        };
        exit;
    } else {
        # Failed login
        print_login_form("Invalid password. Please try again.");
        exit;
    }
}

# Check if already authenticated
if (is_authenticated($session)) {
    # Already logged in, redirect to admin form
    print $cgi->redirect(-uri => 'admin_form_protected.cgi');
    exit;
}

# Show login form
print_login_form();

# Subroutines

sub is_authenticated {
    my $session = shift;
    
    # Check if session exists and is authenticated
    return 0 unless $session->param('authenticated');
    
    # Check if session hasn't expired
    my $login_time = $session->param('login_time') || 0;
    my $current_time = time();
    
    if ($current_time - $login_time > $SESSION_TIMEOUT) {
        # Session expired
        $session->delete();
        $session->flush();
        return 0;
    }
    
    return 1;
}

sub print_login_form {
    my $error_message = shift || '';
    
    print CGI::header(-type => 'text/html', -charset => 'UTF-8');
    
    print qq{
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - Notice Board</title>
    <link rel="stylesheet" href="admin_style.css">
    <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .login-icon {
            font-size: 4rem;
            color: #667eea;
            margin-bottom: 20px;
        }
        
        .login-title {
            color: #333;
            font-size: 1.8rem;
            margin-bottom: 10px;
        }
        
        .login-subtitle {
            color: #666;
            font-size: 1rem;
        }
        
        .login-form {
            margin-top: 30px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }
        
        .form-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e1e1;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-sizing: border-box;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .login-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        .login-btn:active {
            transform: translateY(0);
        }
        
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #f5c6cb;
            text-align: center;
            font-weight: 500;
        }
        
        .security-note {
            margin-top: 30px;
            padding: 15px;
            background: #e7f3ff;
            border: 1px solid #bee5eb;
            border-radius: 8px;
            font-size: 0.9rem;
            color: #0c5460;
        }
        
        .security-note-title {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
        
        .back-link a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        .back-link a:hover {
            text-decoration: underline;
        }
        
        /* Animation for form appearance */
        .login-container {
            animation: slideIn 0.5s ease-out;
        }
        
        \@keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Mobile responsive */
        \@media (max-width: 480px) {
            .login-container {
                margin: 50px 20px;
                padding: 30px 20px;
            }
            
            .login-title {
                font-size: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-container">
            <div class="login-header">
                <div class="login-icon">🔐</div>
                <h1 class="login-title">Admin Login</h1>
                <p class="login-subtitle">Enter password to access admin panel</p>
            </div>
    };
    
    if ($error_message) {
        print qq{
            <div class="error-message">
                ⚠️ $error_message
            </div>
        };
    }
    
    print qq{
            <form method="POST" class="login-form">
                <input type="hidden" name="action" value="login">
                
                <div class="form-group">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" id="password" name="password" class="form-input" 
                           placeholder="Enter admin password" required autofocus>
                </div>
                
                <button type="submit" class="login-btn">
                    <span>🔑</span> Login
                </button>
            </form>
            
            <div class="security-note">
                <div class="security-note-title">🛡️ Security Notice</div>
                <div>This area is restricted to authorized administrators only. 
                All login attempts are logged.</div>
            </div>
            
            <div class="back-link">
                <a href="view_notices.cgi">← Back to Notice Board</a>
            </div>
        </div>
    </div>
    
    <script>
        // Focus on password field
        document.getElementById('password').focus();
        
        // Add enter key support
        document.getElementById('password').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                document.querySelector('form').submit();
            }
        });
        
        // Add some security - clear password field on page load
        window.addEventListener('load', function() {
            document.getElementById('password').value = '';
        });
    </script>
</body>
</html>
    };
}
