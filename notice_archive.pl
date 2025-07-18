#!/usr/bin/perl

use strict;
use warnings;
use XML::LibXML;
use File::Copy;
use POSIX qw(strftime);
use DateTime;

# Configuration
my $ARCHIVE_DAYS = 30;  # Archive notices older than 30 days
my $NOTICES_FILE = 'notices.xml';
my $ARCHIVE_FILE = 'archive.xml';

# Main archive function
sub archive_old_notices {
    my ($days_old) = @_;
    $days_old ||= $ARCHIVE_DAYS;
    
    print "Archiving notices older than $days_old days...\n";
    
    # Get current date
    my $current_date = DateTime->now();
    my $cutoff_date = $current_date->subtract(days => $days_old);
    
    # Read current notices
    my @current_notices = read_notices_from_xml($NOTICES_FILE);
    my @notices_to_archive = ();
    my @notices_to_keep = ();
    
    foreach my $notice (@current_notices) {
        my $notice_date = DateTime->new(
            year  => substr($notice->{date}, 0, 4),
            month => substr($notice->{date}, 5, 2),
            day   => substr($notice->{date}, 8, 2)
        );
        
        if ($notice_date < $cutoff_date) {
            push @notices_to_archive, $notice;
        } else {
            push @notices_to_keep, $notice;
        }
    }
    
    if (@notices_to_archive) {
        # Move old notices to archive
        move_notices_to_archive(@notices_to_archive);
        
        # Update current notices file with remaining notices
        write_notices_to_xml($NOTICES_FILE, @notices_to_keep);
        
        print "Archived " . scalar(@notices_to_archive) . " notices.\n";
        print "Kept " . scalar(@notices_to_keep) . " current notices.\n";
    } else {
        print "No notices to archive.\n";
    }
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
                archived_by => get_node_text($notice_node, 'archived_by') || 'auto'
            };
            push @notices, $notice;
        }
    };
    
    if ($@) {
        print "Error reading XML file $xml_file: $@\n";
    }
    
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

# Move notices to archive
sub move_notices_to_archive {
    my (@notices_to_archive) = @_;
    
    # Read existing archived notices
    my @existing_archived = read_notices_from_xml($ARCHIVE_FILE);
    
    # Add archive metadata to new notices
    my $current_time = strftime("%Y-%m-%d %H:%M:%S", localtime);
    foreach my $notice (@notices_to_archive) {
        $notice->{archived_date} = $current_time;
        $notice->{archived_by} ||= 'auto';
    }
    
    # Combine with existing archived notices
    my @all_archived = (@existing_archived, @notices_to_archive);
    
    # Write to archive file
    write_notices_to_xml($ARCHIVE_FILE, @all_archived);
}

# Get current notices (not archived)
sub get_current_notices {
    my ($branch_filter, $importance_filter, $search_text) = @_;
    
    my @notices = read_notices_from_xml($NOTICES_FILE);
    
    # Filter by branch
    if ($branch_filter) {
        @notices = grep { $_->{branch} eq $branch_filter } @notices;
    }
    
    # Filter by importance
    if ($importance_filter) {
        @notices = grep { $_->{importance} eq $importance_filter } @notices;
    }
    
    # Filter by search text
    if ($search_text) {
        @notices = grep { 
            $_->{title} =~ /\Q$search_text\E/i || 
            $_->{description} =~ /\Q$search_text\E/i 
        } @notices;
    }
    
    return @notices;
}

# Get archived notices
sub get_archived_notices {
    my ($branch_filter, $importance_filter, $search_text, $date_from, $date_to) = @_;
    
    my @notices = read_notices_from_xml($ARCHIVE_FILE);
    
    # Filter by branch
    if ($branch_filter) {
        @notices = grep { $_->{branch} eq $branch_filter } @notices;
    }
    
    # Filter by importance
    if ($importance_filter) {
        @notices = grep { $_->{importance} eq $importance_filter } @notices;
    }
    
    # Filter by search text
    if ($search_text) {
        @notices = grep { 
            $_->{title} =~ /\Q$search_text\E/i || 
            $_->{description} =~ /\Q$search_text\E/i 
        } @notices;
    }
    
    # Filter by date range
    if ($date_from || $date_to) {
        @notices = grep {
            my $notice_date = $_->{date};
            my $include = 1;
            
            if ($date_from && $notice_date lt $date_from) {
                $include = 0;
            }
            if ($date_to && $notice_date gt $date_to) {
                $include = 0;
            }
            
            $include;
        } @notices;
    }
    
    return @notices;
}

# Manually archive specific notices by ID
sub archive_notices_by_id {
    my (@notice_ids) = @_;
    
    my @current_notices = read_notices_from_xml($NOTICES_FILE);
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
        write_notices_to_xml($NOTICES_FILE, @notices_to_keep);
        
        print "Manually archived " . scalar(@notices_to_archive) . " notices.\n";
        return 1;
    }
    
    return 0;
}

# Restore notices from archive
sub restore_notices_from_archive {
    my (@notice_ids) = @_;
    
    my @archived_notices = read_notices_from_xml($ARCHIVE_FILE);
    my @current_notices = read_notices_from_xml($NOTICES_FILE);
    
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
        # Update archive file
        write_notices_to_xml($ARCHIVE_FILE, @notices_to_keep_archived);
        
        # Add to current notices
        push @current_notices, @notices_to_restore;
        write_notices_to_xml($NOTICES_FILE, @current_notices);
        
        print "Restored " . scalar(@notices_to_restore) . " notices from archive.\n";
        return 1;
    }
    
    return 0;
}

# Get statistics
sub get_notice_statistics {
    my @current = read_notices_from_xml($NOTICES_FILE);
    my @archived = read_notices_from_xml($ARCHIVE_FILE);
    
    my %stats = (
        total_current => scalar(@current),
        total_archived => scalar(@archived),
        by_branch => {},
        by_importance => {},
        recent_activity => 0
    );
    
    # Count by branch and importance
    foreach my $notice (@current, @archived) {
        $stats{by_branch}{$notice->{branch}}++;
        $stats{by_importance}{$notice->{importance}}++;
    }
    
    # Count recent activity (last 7 days)
    my $week_ago = DateTime->now()->subtract(days => 7)->ymd;
    $stats{recent_activity} = grep { $_->{date} ge $week_ago } @current;
    
    return %stats;
}

# Example usage and test functions
sub run_archive_example {
    print "=== Notice Archive System Demo ===\n\n";
    
    # Show current statistics
    my %stats = get_notice_statistics();
    print "Current Statistics:\n";
    print "- Current notices: $stats{total_current}\n";
    print "- Archived notices: $stats{total_archived}\n";
    print "- Recent activity (7 days): $stats{recent_activity}\n\n";
    
    # Archive old notices
    archive_old_notices(30);
    
    # Show updated statistics
    %stats = get_notice_statistics();
    print "\nUpdated Statistics:\n";
    print "- Current notices: $stats{total_current}\n";
    print "- Archived notices: $stats{total_archived}\n";
    
    print "\n=== Demo Complete ===\n";
}

# Run the example if script is executed directly
if ($0 eq __FILE__) {
    run_archive_example();
}

1;  # Return true for module usage
