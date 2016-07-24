#!/usr/bin/env perl
#=============================================================================#
# https://github.com/MartyCombs/bin/blob/master/pic-pulldata.pl
#=============================================================================#

my @exif_data=`/usr/local/bin/exiftool $ARGV[0]`;
my @optionlist=('GPSLatitudeRef', 'GPSLongitudeRef', 'GPSAltitudeRef',
                'GPSAltitude', 'GPSLatitude', 'GPSLongitude');
my $options;
foreach my $o (@optionlist) { $options->{"$o"} = 1 };
printf "exiftool ";
foreach my $line (@exif_data) {
    chomp $line;
    next unless ( $line =~ /^GPS.*/ );
    my ($option,$value) = $line =~ /^([^\:].*?)\:(.*?)$/;
    $option =~ s/\s//g;
    next unless $options->{"$option"};
    $value =~ s/^\s+//;
    $value =~ s/"/\\"/g;
    printf "-%s=\"%s\" ", $option, $value;
}
printf "\n";
