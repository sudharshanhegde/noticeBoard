#!C:\Strawberry\perl\bin\perl.exe

use strict;
use warnings;
use CGI;
use CGI::Session;
use XML::LibXML;
use File::Copy;
use POSIX qw(strftime);
use Date::Parse;

# Configuration
my $SESSION_TIMEOUT = 3600;  # Session timeout in seconds (1 hour)

# Create CGI object
my $cgi = CGI->new;

# Initialize session and check authentication
my $session = CGI::Session->new("driver:File", undef, {Directory=>'/tmp'});

# Check authentication before processing
unless (is_authenticated($session)) {
    # Not authenticated, redirect to login
    print $cgi->redirect(-uri => 'admin_login.cgi');
    exit;
}

# Print HTTP header
print $cgi->header(-type => 'text/html', -charset => 'UTF-8');

# File paths
my $notices_file = 'notices.xml';
my $archive_file = 'archive.xml';

# Get today's date
my $today = strftime "%Y-%m-%d", localtime;

# Check if user wants to perform archiving
my $action = $cgi->param('action') || '';

if ($action eq 'archive') {
    # Perform archiving
    my $result = archive_old_notices($notices_file, $archive_file, $today);
    print_result_page($result);
} else {
    # Show preview of what will be archived
    my $old_notices = get_old_notices($notices_file, $today);
    print_preview_page($old_notices, $today);
}

# Subroutines

sub get_old_notices {
    my ($notices_file, $today) = @_;
    my @old_notices = ();
    
    return @old_notices unless -f $notices_file;
    
    eval {
        my $parser = XML::LibXML->new();
        my $doc = $parser->parse_file($notices_file);
        my $root = $doc->getDocumentElement();
        
        my @notice_nodes = $root->findnodes('//notice');
        
        foreach my $notice_node (@notice_nodes) {
            my $notice_date = get_node_text($notice_node, 'date');
            
            # Compare dates (notices older than today)
            if ($notice_date && $notice_date lt $today) {
                my %notice = (
                    id => $notice_node->getAttribute('id') || '',
                    title => get_node_text($notice_node, 'title'),
                    date => $notice_date,
                    description => get_node_text($notice_node, 'description'),
                    branch => get_node_text($notice_node, 'branch'),
                    importance => get_node_text($notice_node, 'importance')
                );
                push @old_notices, \%notice;
            }
        }
    };
    
    if ($@) {
        print STDERR "Error reading notices XML: $@\n";
    }
    
    return @old_notices;
}

sub archive_old_notices {
    my ($notices_file, $archive_file, $today) = @_;
    my %result = (
        success => 0,
        archived_count => 0,
        remaining_count => 0,
        error => '',
        archived_notices => []
    );
    
    # Check if notices file exists
    unless (-f $notices_file) {
        $result{error} = "Notices file not found.";
        return \%result;
    }
    
    eval {
        # Create backups
        copy($notices_file, "$notices_file.bak") or die "Cannot create backup of notices: $!";
        copy($archive_file, "$archive_file.bak") if -f $archive_file;
        
        # Parse notices file
        my $parser = XML::LibXML->new();
        my $notices_doc = $parser->parse_file($notices_file);
        my $notices_root = $notices_doc->getDocumentElement();
        
        # Create or parse archive file
        my $archive_doc;
        my $archive_root;
        
        if (-f $archive_file) {
            $archive_doc = $parser->parse_file($archive_file);
            $archive_root = $archive_doc->getDocumentElement();
        } else {
            $archive_doc = XML::LibXML::Document->new('1.0', 'UTF-8');
            $archive_root = $archive_doc->createElement('archived_notices');
            $archive_doc->setDocumentElement($archive_root);
        }
        
        # Get all notice nodes
        my @notice_nodes = $notices_root->findnodes('//notice');
        my @nodes_to_remove = ();
        
        foreach my $notice_node (@notice_nodes) {
            my $notice_date = get_node_text($notice_node, 'date');
            
            # Check if notice is old (date < today)
            if ($notice_date && $notice_date lt $today) {
                # Clone the notice node for archive
                my $archived_notice = $notice_node->cloneNode(1);
                
                # Add archive date attribute
                $archived_notice->setAttribute('archived_date', $today);
                
                # Import and append to archive
                my $imported_notice = $archive_doc->importNode($archived_notice, 1);
                $archive_root->appendChild($imported_notice);
                
                # Mark for removal from notices
                push @nodes_to_remove, $notice_node;
                
                # Add to result
                my %notice_info = (
                    id => $notice_node->getAttribute('id') || '',
                    title => get_node_text($notice_node, 'title'),
                    date => $notice_date,
                    branch => get_node_text($notice_node, 'branch'),
                    importance => get_node_text($notice_node, 'importance')
                );
                push @{$result{archived_notices}}, \%notice_info;
                $result{archived_count}++;
            }
        }
        
        # Remove archived notices from notices file
        foreach my $node (@nodes_to_remove) {
            $node->parentNode->removeChild($node);
        }
        
        # Count remaining notices
        my @remaining_nodes = $notices_root->findnodes('//notice');
        $result{remaining_count} = scalar(@remaining_nodes);
        
        # Save both files
        $notices_doc->toFile($notices_file, 1);
        $archive_doc->toFile($archive_file, 1);
        
        $result{success} = 1;
    };
    
    if ($@) {
        $result{error} = "Error during archiving: $@";
    }
    
    return \%result;
}

sub get_node_text {
    my ($parent_node, $tag_name) = @_;
    my $node = $parent_node->findnodes($tag_name)->get_node(1);
    return $node ? $node->textContent : '';
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

sub get_importance_class {
    my $importance = shift;
    my %importance_classes = (
        'low' => 'importance-low',
        'medium' => 'importance-medium',
        'high' => 'importance-high',
        'urgent' => 'importance-urgent',
        'critical' => 'importance-critical'
    );
    return $importance_classes{$importance} || 'importance-default';
}

sub format_date {
    my $date = shift;
    if ($date =~ /^(\d{4})-(\d{2})-(\d{2})$/) {
        my ($year, $month, $day) = ($1, $2, $3);
        my @months = qw(Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec);
        return "$day " . $months[$month - 1] . " $year";
    }
    return $date;
}

sub print_preview_page {
    my ($old_notices, $today) = @_;
    
    my $old_count = scalar(@$old_notices);
    my $formatted_today = format_date($today);
    
    print qq{
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archive Old Notices - Preview</title>
    <link rel="stylesheet" href="admin_style.css">
    <style>
        .archive-container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        .preview-header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            text-align: center;
        }
        .preview-title {
            color: #333;
            font-size: 2rem;
            margin-bottom: 15px;
        }
        .preview-info {
            color: #666;
            font-size: 1.1rem;
            margin-bottom: 25px;
        }
        .archive-stats {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-bottom: 30px;
        }
        .stat-item {
            text-align: center;
        }
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            font-size: 1rem;
        }
        .notice-list {
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            overflow: hidden;
            margin-bottom: 30px;
        }
        .notice-item {
            padding: 20px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .notice-item:last-child {
            border-bottom: none;
        }
        .notice-info {
            flex: 1;
        }
        .notice-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        .notice-meta {
            display: flex;
            gap: 15px;
            font-size: 0.9rem;
            color: #666;
        }
        .notice-branch {
            background: #f8f9fa;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
        }
        .notice-importance {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        .importance-low { background: #d4edda; color: #155724; }
        .importance-medium { background: #fff3cd; color: #856404; }
        .importance-high { background: #f8d7da; color: #721c24; }
        .importance-urgent { background: #f5c6cb; color: #721c24; }
        .importance-critical { background: #721c24; color: white; }
        .notice-date {
            color: #dc3545;
            font-weight: 500;
            font-size: 0.9rem;
        }
        .action-buttons {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-top: 30px;
        }
        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }
        .btn-danger {
            background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
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
        .warning-box {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .warning-title {
            color: #856404;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .warning-text {
            color: #856404;
            line-height: 1.5;
        }
        .no-old-notices {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        .no-old-notices-icon {
            font-size: 4rem;
            margin-bottom: 20px;
        }
        
        \@media (max-width: 768px) {
            .archive-stats {
                flex-direction: column;
                gap: 20px;
            }
            .notice-item {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }
            .action-buttons {
                flex-direction: column;
                align-items: center;
            }
            .btn {
                width: 100%;
                max-width: 300px;
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="archive-container">
            <div class="preview-header">
                <h1 class="preview-title">🗂️ Archive Old Notices</h1>
                <p class="preview-info">
                    Review notices that will be archived (older than $formatted_today)
                </p>
                
                <div class="archive-stats">
                    <div class="stat-item">
                        <div class="stat-number">$old_count</div>
                        <div class="stat-label">Notices to Archive</div>
                    </div>
                </div>
            </div>
    };
    
    if ($old_count > 0) {
        print qq{
            <div class="warning-box">
                <div class="warning-title">⚠️ Important Notice</div>
                <div class="warning-text">
                    The following notices will be moved from notices.xml to archive.xml. 
                    This action will create backup files (.bak) before making changes. 
                    Archived notices will be preserved with all their original data.
                </div>
            </div>
            
            <div class="notice-list">
        };
        
        foreach my $notice (@$old_notices) {
            my $branch_name = get_branch_name($notice->{branch});
            my $importance_class = get_importance_class($notice->{importance});
            my $formatted_date = format_date($notice->{date});
            my $importance_display = ucfirst($notice->{importance});
            
            # Truncate description if too long
            my $description = $notice->{description};
            if (length($description) > 100) {
                $description = substr($description, 0, 100) . "...";
            }
            
            print qq{
                <div class="notice-item">
                    <div class="notice-info">
                        <div class="notice-title">$notice->{title}</div>
                        <div class="notice-meta">
                            <span class="notice-branch">$branch_name</span>
                            <span class="notice-importance $importance_class">$importance_display</span>
                        </div>
                        <div style="margin-top: 8px; color: #666; font-size: 0.9rem;">$description</div>
                    </div>
                    <div class="notice-date">$formatted_date</div>
                </div>
            };
        }
        
        print qq{
            </div>
            
            <div class="action-buttons">
                <form method="POST" style="display: inline;">
                    <input type="hidden" name="action" value="archive">
                    <button type="submit" class="btn btn-danger" onclick="return confirm('Are you sure you want to archive these notices? This action cannot be undone.')">
                        <span>📦</span> Archive $old_count Notice(s)
                    </button>
                </form>
                <a href="view_notices.cgi" class="btn btn-secondary">
                    <span>👀</span> View Current Notices
                </a>
            </div>
        };
    } else {
        print qq{
            <div class="no-old-notices">
                <div class="no-old-notices-icon">✨</div>
                <h3>No Old Notices Found</h3>
                <p>All notices are current (dated today or later). No archiving needed.</p>
                <div style="margin-top: 30px;">
                    <a href="view_notices.cgi" class="btn btn-secondary">
                        <span>👀</span> View Current Notices
                    </a>
                </div>
            </div>
        };
    }
    
    print qq{
        </div>
    </div>
</body>
</html>
    };
}

sub print_result_page {
    my $result = shift;
    
    if ($result->{success}) {
        my $archived_count = $result->{archived_count};
        my $remaining_count = $result->{remaining_count};
        
        print qq{
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archive Complete</title>
    <link rel="stylesheet" href="admin_style.css">
    <style>
        .success-container {
            max-width: 700px;
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
        .result-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 30px 0;
        }
        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #28a745;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #666;
            font-size: 1rem;
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
        
        \@media (max-width: 768px) {
            .result-stats {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-container">
            <div class="success-icon">✅</div>
            <h1 class="success-title">Archive Complete!</h1>
            
            <div class="result-stats">
                <div class="stat-card">
                    <div class="stat-number">$archived_count</div>
                    <div class="stat-label">Notices Archived</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">$remaining_count</div>
                    <div class="stat-label">Active Notices</div>
                </div>
            </div>
            
            <p style="text-align: center; color: #666; margin: 20px 0;">
                Old notices have been successfully moved to archive.xml. 
                Backup files have been created for safety.
            </p>
            
            <div class="actions">
                <a href="view_notices.cgi" class="btn btn-primary">View Current Notices</a>
                <a href="admin_form_protected.cgi" class="btn btn-secondary">Add New Notice</a>
            </div>
        </div>
    </div>
</body>
</html>
        };
    } else {
        print qq{
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archive Error</title>
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
        .error-message {
            background: #f8d7da;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #dc3545;
            color: #721c24;
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
            <h1 class="error-title">Archive Error</h1>
            
            <div class="error-message">
                <strong>Error:</strong> $result->{error}
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
