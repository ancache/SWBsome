#!/bin/bash

#####
# Date: 11.13.2014
# Author: Anca Chereches
# Script reads a list of file names without extension
# finds the corresponding sphere files in the Switchboard folder
# pipes each one of them to sph2pipe, which converts them to PCM wav
# this output is then piped to lame, which encodes them in mp3 format
####

while read line terminalID
do
    find /Users/acasa/tools/Switchboard_LDC97S62/ -name "$line.sph" | xargs -I {} sph2pipe -p {} | lame -r -s 8000 -m m -a - "$line$terminalID.mp3"
## alternatively, without using xargs:
# sph2pipe -p ` find /Users/acasa/tools/Switchboard_LDC97S62/ -name "$line.sph"` | lame -r -s 8000 -m m -a - "$line.mp3"
done < sph_files.txt