#!/usr/bin/perl
use strict;
use warnings;

my $n = 10;
my $aa = 2;
my $bb = 3;
my $c = 1;


my @segments;

my $len = 0;

for (my $i = 0; $i <= $n / $aa; $i++) {
    if (not grep /$len/, @segments) {
        push(@segments, $len);
    }
    $len += $aa;
}

$len = $n - $bb;
for (my $i = 0; $i < int($n / $bb); $i++) {
    if (not grep /$len$/, @segments) {
        push(@segments, $len);
    }
    $len -= $bb;
}

@segments = sort { $a <=> $b } @segments;

my $colored = 0;
for (my $i = 0; $i <= $n; $i++) {
    my $ii = $i + $c;
    if (grep /$i$/, @segments and grep /$ii$/, @segments) {
        $colored++;
    }
}

print($n - $colored);