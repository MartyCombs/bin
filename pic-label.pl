#!/usr/bin/perl
#=============================================================================#
# https://github.com/MartyCombs/bin/blob/master/pic-label.pl
#=============================================================================#

use strict;

my $label = shift @ARGV;
foreach (@ARGV) {
    my $oldname = $_;
    $_ =~ /(.*)\.(.{3,4})$/;
    my $extension = $2;
    my $mainname = $1;
    my @parts = split('-',$mainname);
    print "$oldname $parts[0]-$parts[1]-$label.$extension\n";
    system("/bin/mv $oldname $parts[0]-$parts[1]-$label.$extension");
}
