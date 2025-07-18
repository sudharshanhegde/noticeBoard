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
my $ARCHIVE_DAYS = 30;       # Default days to consider for archiving

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

# Get action parameter
my $action = $cgi->param('action') || 'view';

# Process actions
if ($action eq 'auto_archive') {
    auto_archive_old_notices();
} elsif ($action eq 'manual_archive') {
    manual_archive_notices();
} elsif ($action eq 'restore') {
    restore_notices();
} elsif ($action eq 'view_archived') {
    view_archived_notices();
} else {
    show_archive_dashboard();
}

# Auto archive old notices
sub auto_archive_old_notices {
    my $days = $cgi->param('days') || $ARCHIVE_DAYS;
    
    my @current_notices = read_notices_from_xml('notices.xml');
    my @notices_to_archive = ();
    my @notices_to_keep = ();
    
    my $current_time = time();
    my $cutoff_time = $current_time - ($days * 24 * 60 * 60);
    
    foreach my $notice (@current_notices) {
        my $notice_time = parse_date($notice->{date});
        
        if ($notice_time && $notice_time < $cutoff_time) {
            push @notices_to_archive, $notice;
        } else {
            push @notices_to_keep, $notice;
        }
    }
    
    if (@notices_to_archive) {
        # Move to archive
        move_notices_to_archive(@notices_to_archive);
        
        # Update current notices
        write_notices_to_xml('notices.xml', @notices_to_keep);
        
        print_success_page("Auto Archive Complete", 
            "Successfully archived " . scalar(@notices_to_archive) . " notices older than $days days.");
    } else {
        print_info_page("No Notices to Archive", 
            "No notices older than $days days were found.");
    }
}

# Manual archive specific notices
sub manual_archive_notices {
    my @notice_ids = $cgi->multi_param('notice_ids');
    
    if (@notice_ids) {
        my @current_notices = read_notices_from_xml('notices.xml');
        my @notices_to_archive = ();
        my @notices_to_keep = ();
        
        foreach my $notice (@current_notices) {
            if (grep { $_ == $notice->{id} } @notice_ids) {
                push @notices_to_archive, $notice;
            } else {
                push @notices_to_keep, $notice;
            }
        }
        
        if (@notices_to_archive) {
            move_notices_to_archive(@notices_to_archive);
            write_notices_to_xml('notices.xml', @notices_to_keep);
            
            print_success_page("Manual Archive Complete", 
                "Successfully archived " . scalar(@notices_to_archive) . " selected notices.");
        } else {
            print_error_page("No notices selected for archiving.");
        }
    } else {
        print_error_page("No notices selected for archiving.");
    }
}

# Restore notices from archive
sub restore_notices {
    my @notice_ids = $cgi->multi_param('archived_notice_ids');
    
    if (@notice_ids) {
        my @archived_notices = read_notices_from_xml('archive.xml');
        my @current_notices = read_notices_from_xml('notices.xml');
        
        my @notices_to_restore = ();
        my @notices_to_keep_archived = ();
        
        foreach my $notice (@archived_notices) {
            if (grep { $_ == $notice->{id} } @notice_ids) {
                # Remove archive metadata
                delete $notice->{archived_date};
                delete $notice->{archived_by};
                push @notices_to_restore, $notice;
            } else {
                push @notices_to_keep_archived, $notice;
            }
        }
        
        if (@notices_to_restore) {
            # Update files
            write_notices_to_xml('archive.xml', @notices_to_keep_archived);
            
            push @current_notices, @notices_to_restore;
            write_notices_to_xml('notices.xml', @current_notices);
            
            print_success_page("Restore Complete", 
                "Successfully restored " . scalar(@notices_to_restore) . " notices from archive.");
        } else {
            print_error_page("No notices selected for restoration.");
        }
    } else {
        print_error_page("No notices selected for restoration.");
    }
}

# Parse date string to timestamp
sub parse_date {
    my $date_str = shift;
    return undef unless $date_str;
    
    # Parse YYYY-MM-DD format
    if ($date_str =~ /^(\d{4})-(\d{2})-(\d{2})$/) {
        my ($year, $month, $day) = ($1, $2, $3);
        return POSIX::mktime(0, 0, 0, $day, $month - 1, $year - 1900);
    }
    
    return undef;
}

# Move notices to archive with metadata
sub move_notices_to_archive {
    my (@notices) = @_;
    
    # Read existing archived notices
    my @existing_archived = read_notices_from_xml('archive.xml');
    
    # Add archive metadata
    my $current_time = strftime("%Y-%m-%d %H:%M:%S", localtime);
    foreach my $notice (@notices) {
        $notice->{archived_date} = $current_time;
        $notice->{archived_by} = 'admin';
    }
    
    # Combine and save
    my @all_archived = (@existing_archived, @notices);
    write_notices_to_xml('archive.xml', @all_archived);
}

# Read notices from XML file
sub read_notices_from_xml {
    my ($xml_file) = @_;
    my @notices = ();
    
    return @notices unless -f $xml_file;
    
    eval {
        my $parser = XML::LibXML->new();
        my $doc = $parser->parse_file($xml_file);
        my $root = $doc->getDocumentElement();
        
        my @notice_nodes = $root->findnodes('//notice');
        
        foreach my $notice_node (@notice_nodes) {
            my $notice = {
                id => $notice_node->getAttribute('id'),
                title => get_node_text($notice_node, 'title'),
                date => get_node_text($notice_node, 'date'),
                description => get_node_text($notice_node, 'description'),
                branch => get_node_text($notice_node, 'branch'),
                importance => get_node_text($notice_node, 'importance'),
                archived_date => get_node_text($notice_node, 'archived_date') || '',
                archived_by => get_node_text($notice_node, 'archived_by') || ''
            };
            push @notices, $notice;
        }
    };
    
    return @notices;
}

# Get text content from XML node
sub get_node_text {
    my ($parent, $tag) = @_;
    my $node = $parent->findnodes($tag)->get_node(1);
    return $node ? $node->textContent : '';
}

# Write notices to XML file
sub write_notices_to_xml {
    my ($xml_file, @notices) = @_;
    
    # Create backup
    copy($xml_file, "$xml_file.bak") if -f $xml_file;
    
    # Create new XML document
    my $doc = XML::LibXML::Document->new('1.0', 'UTF-8');
    my $root = $doc->createElement('notices');
    $doc->setDocumentElement($root);
    
    foreach my $notice (@notices) {
        my $notice_elem = $doc->createElement('notice');
        $notice_elem->setAttribute('id', $notice->{id});
        
        # Add all fields
        add_xml_element($doc, $notice_elem, 'title', $notice->{title});
        add_xml_element($doc, $notice_elem, 'date', $notice->{date});
        add_xml_element($doc, $notice_elem, 'description', $notice->{description});
        add_xml_element($doc, $notice_elem, 'branch', $notice->{branch});
        add_xml_element($doc, $notice_elem, 'importance', $notice->{importance});
        
        # Add archive-specific fields if they exist
        if ($notice->{archived_date}) {
            add_xml_element($doc, $notice_elem, 'archived_date', $notice->{archived_date});
            add_xml_element($doc, $notice_elem, 'archived_by', $notice->{archived_by});
        }
        
        $root->appendChild($notice_elem);
    }
    
    # Save to file
    $doc->toFile($xml_file, 1);
}

# Add XML element with text content
sub add_xml_element {
    my ($doc, $parent, $tag, $text) = @_;
    my $elem = $doc->createElement($tag);
    $elem->appendTextNode($text) if defined $text;
    $parent->appendChild($elem);
}

# Show archive dashboard
sub show_archive_dashboard {
    my @current_notices = read_notices_from_xml('notices.xml');
    my @archived_notices = read_notices_from_xml('archive.xml');
    
    # Calculate statistics
    my $total_current = scalar(@current_notices);
    my $total_archived = scalar(@archived_notices);
    
    # Count old notices (older than 30 days)
    my $current_time = time();
    my $cutoff_time = $current_time - ($ARCHIVE_DAYS * 24 * 60 * 60);
    my $old_notices = 0;
    
    foreach my $notice (@current_notices) {
        my $notice_time = parse_date($notice->{date});
        if ($notice_time && $notice_time < $cutoff_time) {
            $old_notices++;
        }
    }
    
    print qq{
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archive Management - Notice Board</title>
    <link rel="stylesheet" href="admin_style.css">
    <style>
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #007bff;
        }
        .action-buttons {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .notice-list {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 10px;
        }
        .notice-item {
            padding: 10px;
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
            font-weight: bold;
            color: #333;
        }
        .notice-meta {
            font-size: 0.9rem;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Archive Management</h1>
            <p>Manage current and archived notices</p>
            <div style="text-align: right; margin-top: 10px;">
                <a href="admin_form_protected.cgi" style="color: #007bff; text-decoration: none; margin-right: 15px;">
                    📋 Add Notice
                </a>
                <a href="view_notices.cgi" style="color: #007bff; text-decoration: none; margin-right: 15px;">
                    👀 View Notices
                </a>
                <a href="admin_login.cgi?action=logout" style="color: #dc3545; text-decoration: none;">
                    🔓 Logout
                </a>
            </div>
        </header>

        <main>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">$total_current</div>
                    <div>Current Notices</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">$total_archived</div>
                    <div>Archived Notices</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">$old_notices</div>
                    <div>Old Notices (30+ days)</div>
                </div>
            </div>

            <div class="action-buttons">
                <form action="archive_notices.cgi" method="post" style="display: inline;">
                    <input type="hidden" name="action" value="auto_archive">
                    <input type="number" name="days" value="30" min="1" max="365" style="width: 80px; padding: 5px;">
                    <button type="submit" class="btn btn-primary">
                        🗂️ Auto Archive (days)
                    </button>
                </form>
                
                <a href="archive_notices.cgi?action=view_archived" class="btn btn-secondary">
                    📂 View Archived
                </a>
            </div>

            <h3>Current Notices - Select to Archive</h3>
            <form action="archive_notices.cgi" method="post">
                <input type="hidden" name="action" value="manual_archive">
                <div class="notice-list">
    };
    
    if (@current_notices) {
        foreach my $notice (@current_notices) {
            my $branch_name = get_branch_name($notice->{branch});
            my $importance_color = get_importance_color($notice->{importance});
            
            print qq{
                <div class="notice-item">
                    <div class="notice-info">
                        <div class="notice-title">$notice->{title}</div>
                        <div class="notice-meta">
                            $notice->{date} | $branch_name | 
                            <span style="color: $importance_color;">$notice->{importance}</span>
                        </div>
                    </div>
                    <input type="checkbox" name="notice_ids" value="$notice->{id}">
                </div>
            };
        }
    } else {
        print qq{
            <div class="notice-item">
                <div class="notice-info">No current notices found.</div>
            </div>
        };
    }
    
    print qq{
                </div>
                <div style="margin-top: 15px;">
                    <button type="submit" class="btn btn-warning">
                        🗃️ Archive Selected
                    </button>
                </div>
            </form>
        </main>

        <footer>
            <p>&copy; 2025 UVCE - Archive Management System</p>
        </footer>
    </div>

    <script>
        // Select all functionality
        function toggleAll(source) {
            const checkboxes = document.querySelectorAll('input[name="notice_ids"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = source.checked;
            });
        }
        
        // Add select all checkbox
        document.addEventListener('DOMContentLoaded', function() {
            const firstCheckbox = document.querySelector('input[name="notice_ids"]');
            if (firstCheckbox) {
                const selectAllHtml = '<div class="notice-item" style="background: #e9ecef;"><div class="notice-info"><strong>Select All</strong></div><input type="checkbox" onchange="toggleAll(this)"></div>';
                firstCheckbox.closest('.notice-list').insertAdjacentHTML('afterbegin', selectAllHtml);
            }
        });
    </script>
</body>
</html>
    };
}

# View archived notices
sub view_archived_notices {
    my @archived_notices = read_notices_from_xml('archive.xml');
    
    print qq{
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archived Notices - Notice Board</title>
    <link rel="stylesheet" href="admin_style.css">
    <style>
        .archive-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .notice-list {
            max-height: 500px;
            overflow-y: auto;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 10px;
        }
        .notice-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        .notice-item:last-child {
            border-bottom: none;
        }
        .notice-content {
            flex: 1;
        }
        .notice-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .notice-description {
            color: #666;
            margin-bottom: 10px;
        }
        .notice-meta {
            font-size: 0.9rem;
            color: #888;
        }
        .archive-meta {
            font-size: 0.8rem;
            color: #999;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Archived Notices</h1>
            <p>View and manage archived notices</p>
            <div style="text-align: right; margin-top: 10px;">
                <a href="archive_notices.cgi" style="color: #007bff; text-decoration: none; margin-right: 15px;">
                    🗂️ Archive Dashboard
                </a>
                <a href="admin_login.cgi?action=logout" style="color: #dc3545; text-decoration: none;">
                    🔓 Logout
                </a>
            </div>
        </header>

        <main>
            <div class="archive-header">
                <h3>Archived Notices (} . scalar(@archived_notices) . qq{)</h3>
            </div>

            <form action="archive_notices.cgi" method="post">
                <input type="hidden" name="action" value="restore">
                <div class="notice-list">
    };
    
    if (@archived_notices) {
        foreach my $notice (@archived_notices) {
            my $branch_name = get_branch_name($notice->{branch});
            my $importance_color = get_importance_color($notice->{importance});
            
            print qq{
                <div class="notice-item">
                    <div class="notice-content">
                        <div class="notice-title">$notice->{title}</div>
                        <div class="notice-description">$notice->{description}</div>
                        <div class="notice-meta">
                            Original Date: $notice->{date} | $branch_name | 
                            <span style="color: $importance_color;">$notice->{importance}</span>
                        </div>
                        <div class="archive-meta">
                            Archived: $notice->{archived_date} by $notice->{archived_by}
                        </div>
                    </div>
                    <input type="checkbox" name="archived_notice_ids" value="$notice->{id}">
                </div>
            };
        }
    } else {
        print qq{
            <div class="notice-item">
                <div class="notice-content">No archived notices found.</div>
            </div>
        };
    }
    
    print qq{
                </div>
                <div style="margin-top: 15px;">
                    <button type="submit" class="btn btn-success">
                        ↩️ Restore Selected
                    </button>
                </div>
            </form>
        </main>

        <footer>
            <p>&copy; 2025 UVCE - Archived Notices</p>
        </footer>
    </div>
</body>
</html>
    };
}

# Utility functions
sub get_branch_name {
    my $branch = shift;
    my %branch_names = (
        'cse' => 'Computer Science & Engineering',
        'ai' => 'Artificial Intelligence',
        'ise' => 'Information Science & Engineering',
        'mechanical' => 'Mechanical Engineering',
        'civil' => 'Civil Engineering',
        'ece' => 'Electronics & Communication Engineering',
        'eee' => 'Electrical & Electronics Engineering',
        'all_branches' => 'All Branches'
    );
    return $branch_names{$branch} || $branch;
}

sub get_importance_color {
    my $importance = shift;
    my %colors = (
        'low' => '#28a745',
        'medium' => '#ffc107',
        'high' => '#fd7e14',
        'urgent' => '#dc3545',
        'critical' => '#721c24'
    );
    return $colors{$importance} || '#333';
}

# Success/Error page functions
sub print_success_page {
    my ($title, $message) = @_;
    print qq{
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$title</title>
    <link rel="stylesheet" href="admin_style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>$title</h1>
        </header>
        <main>
            <div style="text-align: center; padding: 50px;">
                <div style="font-size: 4rem; color: #28a745; margin-bottom: 20px;">✓</div>
                <p style="font-size: 1.2rem; color: #333;">$message</p>
                <div style="margin-top: 30px;">
                    <a href="archive_notices.cgi" class="btn btn-primary">Return to Archive</a>
                    <a href="view_notices.cgi" class="btn btn-secondary">View All Notices</a>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
    };
}

sub print_error_page {
    my ($message) = @_;
    print qq{
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <link rel="stylesheet" href="admin_style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Error</h1>
        </header>
        <main>
            <div style="text-align: center; padding: 50px;">
                <div style="font-size: 4rem; color: #dc3545; margin-bottom: 20px;">✗</div>
                <p style="font-size: 1.2rem; color: #333;">$message</p>
                <div style="margin-top: 30px;">
                    <a href="archive_notices.cgi" class="btn btn-primary">Return to Archive</a>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
    };
}

sub print_info_page {
    my ($title, $message) = @_;
    print qq{
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$title</title>
    <link rel="stylesheet" href="admin_style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>$title</h1>
        </header>
        <main>
            <div style="text-align: center; padding: 50px;">
                <div style="font-size: 4rem; color: #007bff; margin-bottom: 20px;">ℹ</div>
                <p style="font-size: 1.2rem; color: #333;">$message</p>
                <div style="margin-top: 30px;">
                    <a href="archive_notices.cgi" class="btn btn-primary">Return to Archive</a>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
    };
}

# Authentication function
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
