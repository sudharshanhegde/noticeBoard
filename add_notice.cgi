#!C:\Strawberry\perl\bin\perl.exe

use strict;
use warnings;
use CGI;
use CGI::Session;
use XML::LibXML;
use File::Copy;
use POSIX qw(strftime);

# Configuration
my $SESSION_TIMEOUT = 3600;  # Session timeout in seconds (1 hour)

# Create CGI object
my $cgi = CGI->new;

# Initialize session and check authentication
my $session = CGI::Session->new("driver:File", $cgi, {Directory=>'/tmp'});

# Check authentication before processing
unless (is_authenticated($session)) {
    # Not authenticated, redirect to login
    print $cgi->redirect(-uri => 'admin_login.cgi');
    exit;
}

# Print HTTP header
print $cgi->header(-type => 'text/html', -charset => 'UTF-8');

# Get form parameters
my $title = $cgi->param('title') || '';
my $date = $cgi->param('date') || '';
my $description = $cgi->param('description') || '';
my $branch = $cgi->param('branch') || '';
my $importance = $cgi->param('importance') || '';

# Validate input
my @errors = ();

if (!$title || length($title) < 3) {
    push @errors, "Title must be at least 3 characters long.";
}

if (!$date || $date !~ /^\d{4}-\d{2}-\d{2}$/) {
    push @errors, "Valid date is required.";
}

if (!$description || length($description) < 10) {
    push @errors, "Description must be at least 10 characters long.";
}

if (!$branch) {
    push @errors, "Branch selection is required.";
}

if (!$importance) {
    push @errors, "Importance level is required.";
}

# If there are validation errors, display them
if (@errors) {
    print_error_page(\@errors);
    exit;
}

# Sanitize inputs
$title = sanitize_input($title);
$description = sanitize_input($description);

# Path to XML file
my $xml_file = 'notices.xml';

# Check if XML file exists
if (!-f $xml_file) {
    # Create new XML file if it doesn't exist
    create_empty_xml($xml_file);
}

# Add notice to XML
eval {
    add_notice_to_xml($xml_file, $title, $date, $description, $branch, $importance);
    print_success_page($title, $date, $branch, $importance);
};

if ($@) {
    print_error_page(["Error saving notice: $@"]);
}

# Subroutines

sub sanitize_input {
    my $input = shift;
    $input =~ s/[<>&"']//g;  # Remove potentially dangerous characters
    return $input;
}

sub create_empty_xml {
    my $filename = shift;
    open my $fh, '>', $filename or die "Cannot create XML file: $!";
    print $fh '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
    print $fh '<notices>' . "\n";
    print $fh '</notices>' . "\n";
    close $fh;
}

sub add_notice_to_xml {
    my ($xml_file, $title, $date, $description, $branch, $importance) = @_;
    
    # Create backup
    copy($xml_file, "$xml_file.bak") or die "Cannot create backup: $!";
    
    # Parse XML
    my $parser = XML::LibXML->new();
    my $doc = $parser->parse_file($xml_file);
    my $root = $doc->getDocumentElement();
    
    # Find the highest existing ID
    my @notices = $root->findnodes('//notice');
    my $max_id = 0;
    foreach my $notice (@notices) {
        my $id = $notice->getAttribute('id');
        $max_id = $id if $id > $max_id;
    }
    my $new_id = $max_id + 1;
    
    # Create new notice element
    my $notice_elem = $doc->createElement('notice');
    $notice_elem->setAttribute('id', $new_id);
    
    # Add child elements
    my $title_elem = $doc->createElement('title');
    $title_elem->appendTextNode($title);
    $notice_elem->appendChild($title_elem);
    
    my $date_elem = $doc->createElement('date');
    $date_elem->appendTextNode($date);
    $notice_elem->appendChild($date_elem);
    
    my $desc_elem = $doc->createElement('description');
    $desc_elem->appendTextNode($description);
    $notice_elem->appendChild($desc_elem);
    
    my $branch_elem = $doc->createElement('branch');
    $branch_elem->appendTextNode($branch);
    $notice_elem->appendChild($branch_elem);
    
    my $importance_elem = $doc->createElement('importance');
    $importance_elem->appendTextNode($importance);
    $notice_elem->appendChild($importance_elem);
    
    # Append to root
    $root->appendChild($notice_elem);
    
    # Save the file
    $doc->toFile($xml_file, 1);
}

sub get_branch_name {
    my $branch = shift;
    my %branch_names = (
        'cse' => 'Computer Science & Engineering (CSE)',
        'ai' => 'Artificial Intelligence (AI)',
        'ise' => 'Information Science & Engineering (ISE)',
        'mechanical' => 'Mechanical Engineering',
        'civil' => 'Civil Engineering',
        'ece' => 'Electronics & Communication Engineering (ECE)',
        'eee' => 'Electrical & Electronics Engineering (EEE)',
        'all_branches' => 'All Branches'
    );
    return $branch_names{$branch} || $branch;
}

sub get_importance_display {
    my $importance = shift;
    my %importance_colors = (
        'low' => '#28a745',
        'medium' => '#ffc107',
        'high' => '#fd7e14',
        'urgent' => '#dc3545',
        'critical' => '#721c24'
    );
    my $color = $importance_colors{$importance} || '#333';
    return "<span style='color: $color; font-weight: bold;'>" . ucfirst($importance) . "</span>";
}

sub print_success_page {
    my ($title, $date, $branch, $importance) = @_;
    
    my $branch_name = get_branch_name($branch);
    my $importance_display = get_importance_display($importance);
    my $current_time = strftime "%Y-%m-%d %H:%M:%S", localtime;
    
    print qq{
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notice Added Successfully</title>
    <link rel="stylesheet" href="admin_style.css">
    <style>
        .success-container {
            max-width: 600px;
            margin: 50px auto;
            padding: 30px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .success-icon {
            text-align: center;
            font-size: 4rem;
            color: #28a745;
            margin-bottom: 20px;
        }
        .success-title {
            text-align: center;
            color: #28a745;
            font-size: 2rem;
            margin-bottom: 30px;
        }
        .notice-details {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #28a745;
        }
        .detail-row {
            display: flex;
            margin-bottom: 10px;
            padding: 5px 0;
            border-bottom: 1px solid #dee2e6;
        }
        .detail-label {
            font-weight: bold;
            width: 120px;
            color: #495057;
        }
        .detail-value {
            flex: 1;
            color: #212529;
        }
        .actions {
            text-align: center;
            margin-top: 30px;
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            margin: 0 10px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-secondary {
            background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
            color: #333;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-container">
            <div class="success-icon">✅</div>
            <h1 class="success-title">Notice Added Successfully!</h1>
            
            <div class="notice-details">
                <div class="detail-row">
                    <div class="detail-label">Title:</div>
                    <div class="detail-value">$title</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Date:</div>
                    <div class="detail-value">$date</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Branch:</div>
                    <div class="detail-value">$branch_name</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Importance:</div>
                    <div class="detail-value">$importance_display</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Added:</div>
                    <div class="detail-value">$current_time</div>
                </div>
            </div>
            
            <div class="actions">
                <a href="admin_form_protected.cgi" class="btn btn-primary">Add Another Notice</a>
                <a href="view_notices.cgi" class="btn btn-secondary">View All Notices</a>
            </div>
        </div>
    </div>
</body>
</html>
    };
}

sub print_error_page {
    my $errors = shift;
    
    print qq{
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error Adding Notice</title>
    <link rel="stylesheet" href="admin_style.css">
    <style>
        .error-container {
            max-width: 600px;
            margin: 50px auto;
            padding: 30px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .error-icon {
            text-align: center;
            font-size: 4rem;
            color: #dc3545;
            margin-bottom: 20px;
        }
        .error-title {
            text-align: center;
            color: #dc3545;
            font-size: 2rem;
            margin-bottom: 30px;
        }
        .error-list {
            background: #f8d7da;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #dc3545;
            color: #721c24;
        }
        .error-list ul {
            margin: 0;
            padding-left: 20px;
        }
        .error-list li {
            margin-bottom: 10px;
        }
        .actions {
            text-align: center;
            margin-top: 30px;
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            margin: 0 10px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-container">
            <div class="error-icon">❌</div>
            <h1 class="error-title">Error Adding Notice</h1>
            
            <div class="error-list">
                <ul>
    };
    
    foreach my $error (@$errors) {
        print "<li>$error</li>";
    }
    
    print qq{
                </ul>
            </div>
            
            <div class="actions">
                <a href="javascript:history.back()" class="btn btn-primary">Go Back</a>
            </div>
        </div>
    </div>
</body>
</html>
    };
}

# Authentication check subroutine
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
