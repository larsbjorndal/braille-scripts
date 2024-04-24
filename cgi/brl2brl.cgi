#!/bin/perl
use warnings;
use strict;
use utf8;

use App::Brl2Brl;
use CGI '-utf8';
use CGI::Carp qw ( fatalsToBrowser );
use IO::File;
use File::Basename;
$CGI::POST_MAX = 5 * 1024 * 1024;
my $query = CGI->new;

my $filename = $query->param("file");
my $input_brl = $query->param("input_brl");
my $output_brl = $query->param("output_brl");
eval {
  handle_upload( $input_brl, $output_brl, $filename );
}; # eval
sub download_file {
  my( $filename, $dl_content ) = @_;
  print $query->header(
    -charset => "utf-8",
    -type => 'application/octet-stream',
    -attachment => "$filename"
   );
  print $dl_content;
} # download_file

sub handle_upload {
  my( $input_brl, $output_brl, $filename ) = @_;
  if ( (!$filename) or (!$input_brl) or (!$output_brl)  ) {
    die "Error! You must specify a text file, and please choose an input and output table.\n";
  } # if
  if( $input_brl eq $output_brl ){
    die "Error! Input and output must be different. Now both is $output_brl.";
  } # if
  my ( $fname, $fpath, $fextension ) = fileparse ( $filename, '\.[^.]*' );
  $filename = $fname . $fextension;
  $filename =~ s/[^a-zA-Z0-9_.\-æÆøØåÅ]/_/g;
  if ( length($filename) == 0 or length($filename) >= 255 ){
    die "Invalid filename\n";
  } # if

  my $brl_obj = App::Brl2Brl->new( {
    from_table_file => "$input_brl.dis",
    to_table_file => "$output_brl.dis",
  } );
  if( $output_brl =~ /en-us-brf/ ) {
    $fname = $fname . '-brf';
  } elsif( $output_brl =~ /no-no/ ) {
    $fname = $fname . '-no';
  } elsif( $output_brl =~ /unic/ ) {
    $fname = $fname . '-unicode_brl';
  } # if

  $filename = $fname . '.txt';

  my $upload_filehandle = $query->upload("file");
  my $content = do {
    local $/;
    <$upload_filehandle>;
  }; # do

  if( !$content ){
    die "There was a problem with the upload: $!\n";
  } # if
  utf8::decode($content);
  my $result = $brl_obj->switch_brl_char_map( $content );
  if( !$result ){
    die "There was a problem with the conversion process: $!\n";
  } # if
  download_file( $filename, $result );
} # handle_upload

if( $@ ){
  print $query->header( -charset => "utf-8");
  print <<EOT;
<html lang="en">
  <head>
    <title>Braille to braille conversion</title>
  </head>
  <body>
    <h1>Result</h1>

    <h2>Error</h2>
    <p>$@</p>\n";

  </body></html>
EOT
} # if
