#!/usr/bin/perl
use strict;
use warnings;
use List::Util qw(max);

my $size = 670;
my %diag;

sub remainder {
    my ($a, $b) = @_;
    return 0 unless $b && $a;
    return $a / $b - int($a / $b);
}

for (my $i = 1; $i <= $size; $i++) {
    for (my $j = $i + 1; $j <= $size; $j++) {
        my $h = sqrt($i * $i + $j * $j);
        if (remainder($h, 1) == 0 and not exists($diag{$h})) {
            $diag{$h} = $h;
        }
    }
}

print(max(values(%diag)));
my @keys = keys %diag;
$size = @keys;
print(" ");
print($size);
