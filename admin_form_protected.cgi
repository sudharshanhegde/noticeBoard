#!C:\Strawberry\perl\bin\perl.exe

use strict;
use warnings;
use CGI;
use CGI::Session;

# Configuration
my $SESSION_TIMEOUT = 3600;  # Session timeout in seconds (1 hour)

# Create CGI object
my $cgi = CGI->new;

# Initialize session
my $session = CGI::Session->new("driver:File", $cgi, {Directory=>'/tmp'});

# Check authentication
unless (is_authenticated($session)) {
    # Not authenticated, redirect to login
    print $cgi->redirect(-uri => 'admin_login.cgi');
    exit;
}

# If we get here, user is authenticated
# Print the admin form HTML
print $cgi->header(-type => 'text/html', -charset => 'UTF-8');

print qq{
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notice Board Admin - Add Notice</title>
    <link rel="stylesheet" href="admin_style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Notice Board Administration</h1>
            <p>Add New Notice</p>
            <div style="text-align: right; margin-top: 10px;">
                <a href="admin_login.cgi?action=logout" style="color: #dc3545; text-decoration: none; font-weight: 500;">
                    🔓 Logout
                </a>
            </div>
        </header>

        <main>
            <form id="noticeForm" action="add_notice.cgi" method="POST" class="notice-form">
                <div class="form-group">
                    <label for="title">Notice Title *</label>
                    <input type="text" id="title" name="title" required maxlength="100" 
                           placeholder="Enter notice title">
                </div>

                <div class="form-group">
                    <label for="date">Notice Date *</label>
                    <input type="date" id="date" name="date" required>
                </div>

                <div class="form-group">
                    <label for="description">Description *</label>
                    <textarea id="description" name="description" required rows="6" 
                              placeholder="Enter detailed description of the notice"></textarea>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="branch">Branch *</label>
                        <select id="branch" name="branch" required>
                            <option value="">Select Branch</option>
                            <option value="cse">Computer Science & Engineering (CSE)</option>
                            <option value="ai">Artificial Intelligence (AI)</option>
                            <option value="ise">Information Science & Engineering (ISE)</option>
                            <option value="mechanical">Mechanical Engineering</option>
                            <option value="civil">Civil Engineering</option>
                            <option value="ece">Electronics & Communication Engineering (ECE)</option>
                            <option value="eee">Electrical & Electronics Engineering (EEE)</option>
                            <option value="all_branches">All Branches</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="importance">Importance Level *</label>
                        <select id="importance" name="importance" required>
                            <option value="">Select Importance</option>
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                            <option value="urgent">Urgent</option>
                            <option value="critical">Critical</option>
                        </select>
                    </div>
                </div>

                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">
                        <span>📋</span> Add Notice
                    </button>
                    <button type="reset" class="btn btn-secondary">
                        <span>🔄</span> Reset Form
                    </button>
                    <button type="button" class="btn btn-cancel" onclick="window.location.href='view_notices.cgi'">
                        <span>👀</span> View Notices
                    </button>
                </div>
            </form>
        </main>

        <footer>
            <p>&copy; 2025 UVCE</p>
        </footer>
    </div>

    <script>
        // Set default date to today
        document.getElementById('date').valueAsDate = new Date();
        
        // Form validation
        document.getElementById('noticeForm').addEventListener('submit', function(e) {
            const title = document.getElementById('title').value.trim();
            const description = document.getElementById('description').value.trim();
            const branch = document.getElementById('branch').value;
            const importance = document.getElementById('importance').value;
            
            if (!title || !description || !branch || !importance) {
                e.preventDefault();
                alert('Please fill in all required fields.');
                return false;
            }
            
            if (title.length < 3) {
                e.preventDefault();
                alert('Title must be at least 3 characters long.');
                return false;
            }
            
            if (description.length < 10) {
                e.preventDefault();
                alert('Description must be at least 10 characters long.');
                return false;
            }
            
            return confirm('Are you sure you want to add this notice?');
        });
    </script>
</body>
</html>
};

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
