<?php

function read_file($filename) {
  $fp = fopen($filename,"r");
  $out = '';

  $line=fgets($fp);
  while($line != false) {
    $out = $out . $line;
    $line=fgets($fp);
  }
  if($out == '') return null;


  fclose($fp);
  return $out;
}
