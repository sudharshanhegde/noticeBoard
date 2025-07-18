#!C:\Strawberry\perl\bin\perl.exe

use strict;
use warnings;
use CGI;
use XML::LibXML;
use POSIX qw(strftime);

# Create CGI object
my $cgi = CGI->new;

# Print HTTP header
print $cgi->header(-type => 'text/html', -charset => 'UTF-8');

# Get filter parameters
my $filter_branch = $cgi->param('branch') || '';
my $filter_importance = $cgi->param('importance') || '';
my $search_text = $cgi->param('search') || '';

# Path to XML file
my $xml_file = 'notices.xml';

# Read and parse notices
my @notices = ();
if (-f $xml_file) {
    @notices = read_notices_from_xml($xml_file);
}

# Filter notices based on search criteria
@notices = filter_notices(\@notices, $filter_branch, $filter_importance, $search_text);

# Sort notices by date (newest first) and importance
@notices = sort_notices(@notices);

# Print HTML page
print_notices_page(\@notices, $filter_branch, $filter_importance, $search_text);

# Subroutines

sub read_notices_from_xml {
    my $xml_file = shift;
    my @notices = ();
    
    eval {
        my $parser = XML::LibXML->new();
        my $doc = $parser->parse_file($xml_file);
        my $root = $doc->getDocumentElement();
        
        my @notice_nodes = $root->findnodes('//notice');
        
        foreach my $notice_node (@notice_nodes) {
            my %notice = (
                id => $notice_node->getAttribute('id') || '',
                title => get_node_text($notice_node, 'title'),
                date => get_node_text($notice_node, 'date'),
                description => get_node_text($notice_node, 'description'),
                branch => get_node_text($notice_node, 'branch'),
                importance => get_node_text($notice_node, 'importance')
            );
            push @notices, \%notice;
        }
    };
    
    if ($@) {
        print STDERR "Error reading XML: $@\n";
    }
    
    return @notices;
}

sub get_node_text {
    my ($parent_node, $tag_name) = @_;
    my $node = $parent_node->findnodes($tag_name)->get_node(1);
    return $node ? $node->textContent : '';
}

sub filter_notices {
    my ($notices, $branch_filter, $importance_filter, $search_text) = @_;
    my @filtered = ();
    
    foreach my $notice (@$notices) {
        # Filter by branch
        if ($branch_filter && $notice->{branch} ne $branch_filter && $notice->{branch} ne 'all_branches') {
            next unless ($branch_filter eq 'all_branches');
        }
        
        # Filter by importance
        if ($importance_filter && $notice->{importance} ne $importance_filter) {
            next;
        }
        
        # Filter by search text
        if ($search_text) {
            my $search_lower = lc($search_text);
            my $title_lower = lc($notice->{title});
            my $desc_lower = lc($notice->{description});
            
            unless ($title_lower =~ /\Q$search_lower\E/ || $desc_lower =~ /\Q$search_lower\E/) {
                next;
            }
        }
        
        push @filtered, $notice;
    }
    
    return @filtered;
}

sub sort_notices {
    my @notices = @_;
    
    # Sort by importance (critical first) then by date (newest first)
    my %importance_order = (
        'critical' => 1,
        'urgent' => 2,
        'high' => 3,
        'medium' => 4,
        'low' => 5
    );
    
    return sort {
        ($importance_order{$a->{importance}} || 6) <=> ($importance_order{$b->{importance}} || 6)
        || $b->{date} cmp $a->{date}
    } @notices;
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

sub print_notices_page {
    my ($notices, $filter_branch, $filter_importance, $search_text) = @_;
    
    my $notice_count = scalar(@$notices);
    my $search_value = $search_text ? "value=\"$search_text\"" : "";
    
    print qq{
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notice Board - View Notices</title>
    <link rel="stylesheet" href="admin_style.css">
    <style>
        .search-container {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .search-form {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr auto;
            gap: 15px;
            align-items: end;
        }
        .search-group {
            display: flex;
            flex-direction: column;
        }
        .search-group label {
            margin-bottom: 5px;
            font-weight: 600;
            color: #555;
        }
        .search-input, .search-select {
            padding: 10px;
            border: 2px solid #e1e1e1;
            border-radius: 6px;
            font-size: 1rem;
        }
        .search-btn {
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            height: 42px;
        }
        .search-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 0 10px;
        }
        .results-count {
            font-size: 1.1rem;
            color: #666;
        }
        .clear-filters {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        .clear-filters:hover {
            text-decoration: underline;
        }
        .notices-grid {
            display: grid;
            gap: 20px;
        }
        .notice-card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-left: 5px solid #667eea;
        }
        .notice-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        .notice-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }
        .notice-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #333;
            margin: 0;
            flex: 1;
        }
        .notice-date {
            font-size: 0.9rem;
            color: #666;
            white-space: nowrap;
            margin-left: 15px;
        }
        .notice-meta {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }
        .notice-branch {
            background: #f8f9fa;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            color: #495057;
            font-weight: 500;
        }
        .notice-importance {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        .importance-low { background: #d4edda; color: #155724; }
        .importance-medium { background: #fff3cd; color: #856404; }
        .importance-high { background: #f8d7da; color: #721c24; }
        .importance-urgent { background: #f5c6cb; color: #721c24; }
        .importance-critical { background: #721c24; color: white; }
        .notice-description {
            color: #555;
            line-height: 1.6;
            margin: 0;
        }
        .no-notices {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        .no-notices-icon {
            font-size: 4rem;
            margin-bottom: 20px;
        }
        .add-notice-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 50px;
            padding: 15px 25px;
            font-size: 1rem;
            font-weight: 600;
            text-decoration: none;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .add-notice-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        \@media (max-width: 768px) {
            .search-form {
                grid-template-columns: 1fr;
                gap: 15px;
            }
            .results-header {
                flex-direction: column;
                gap: 10px;
                align-items: stretch;
            }
            .notice-header {
                flex-direction: column;
                gap: 10px;
            }
            .notice-date {
                margin-left: 0;
            }
            .notice-meta {
                flex-wrap: wrap;
            }
            .add-notice-btn {
                bottom: 20px;
                right: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Notice Board</h1>
            <p>Engineering College Notices</p>
        </header>

        <main>
            <div class="search-container">
                <form method="GET" class="search-form">
                    <div class="search-group">
                        <label for="search">Search Notices</label>
                        <input type="text" id="search" name="search" class="search-input" 
                               placeholder="Search in title or description..." $search_value>
                    </div>
                    
                    <div class="search-group">
                        <label for="branch">Filter by Branch</label>
                        <select id="branch" name="branch" class="search-select">
                            <option value="">All Branches</option>
    };
    
    # Branch options
    my @branches = (
        ['cse', 'Computer Science & Engineering (CSE)'],
        ['ai', 'Artificial Intelligence (AI)'],
        ['ise', 'Information Science & Engineering (ISE)'],
        ['mechanical', 'Mechanical Engineering'],
        ['civil', 'Civil Engineering'],
        ['ece', 'Electronics & Communication Engineering (ECE)'],
        ['eee', 'Electrical & Electronics Engineering (EEE)'],
        ['all_branches', 'All Branches']
    );
    
    foreach my $branch (@branches) {
        my ($value, $label) = @$branch;
        my $selected = ($filter_branch eq $value) ? 'selected' : '';
        print qq{                            <option value="$value" $selected>$label</option>\n};
    }
    
    print qq{
                        </select>
                    </div>
                    
                    <div class="search-group">
                        <label for="importance">Filter by Importance</label>
                        <select id="importance" name="importance" class="search-select">
                            <option value="">All Levels</option>
    };
    
    # Importance options
    my @importance_levels = (
        ['critical', 'Critical'],
        ['urgent', 'Urgent'],
        ['high', 'High'],
        ['medium', 'Medium'],
        ['low', 'Low']
    );
    
    foreach my $level (@importance_levels) {
        my ($value, $label) = @$level;
        my $selected = ($filter_importance eq $value) ? 'selected' : '';
        print qq{                            <option value="$value" $selected>$label</option>\n};
    }
    
    print qq{
                        </select>
                    </div>
                    
                    <button type="submit" class="search-btn">🔍 Search</button>
                </form>
            </div>

            <div class="results-header">
                <div class="results-count">
                    Found $notice_count notice(s)
                </div>
    };
    
    if ($filter_branch || $filter_importance || $search_text) {
        print qq{                <a href="view_notices.cgi" class="clear-filters">Clear Filters</a>\n};
    }
    
    print qq{
            </div>

            <div class="notices-grid">
    };
    
    if (@$notices) {
        foreach my $notice (@$notices) {
            my $branch_name = get_branch_name($notice->{branch});
            my $importance_class = get_importance_class($notice->{importance});
            my $formatted_date = format_date($notice->{date});
            my $importance_display = ucfirst($notice->{importance});
            
            print qq{
                <div class="notice-card">
                    <div class="notice-header">
                        <h3 class="notice-title">$notice->{title}</h3>
                        <div class="notice-date">$formatted_date</div>
                    </div>
                    
                    <div class="notice-meta">
                        <span class="notice-branch">$branch_name</span>
                        <span class="notice-importance $importance_class">$importance_display</span>
                    </div>
                    
                    <p class="notice-description">$notice->{description}</p>
                </div>
            };
        }
    } else {
        print qq{
                <div class="no-notices">
                    <div class="no-notices-icon">📋</div>
                    <h3>No notices found</h3>
                    <p>No notices match your search criteria. Try adjusting your filters.</p>
                </div>
        };
    }
    
    print qq{
            </div>
        </main>

        <footer>
            <p>&copy; 2025 Engineering College Notice Board</p>
        </footer>
    </div>

    <a href="admin_form_protected.cgi" class="add-notice-btn">
        <span>➕</span> Add Notice
    </a>
</body>
</html>
    };
}
