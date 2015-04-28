#!/bin/bash

sphpath="/Users/acasa/tools/Switchboard_LDC97S62/"
offset=0.005
leeway=0.005

#######
# Date: 11.19.2014
# Author: Anca Chereches
# To run: ./make-mp3s2.sh filename
# Input: script expects as input a tab-separated file
# Input file format: name-of-sphere-format-audiofile starttime endtime starttime endtime ...
# Output: mp3 format audiofile with segments at given timestamps replaced with noise
#######
# Script reads sphere files, converts to wav files, 
# replaces segments at certain timestamps with noise,
# converts the modified wav to mp3 and duplicates the mp3 file
# so there is one mp3 per noise segment
#######

# read 1 line at a time
# tab-delimited fields stored in array "line"
while IFS=$'\t' read -r -a line 
do
    fname=${line[0]}
    # convert sph to wav
    find "$sphpath" -name "$fname.sph" | xargs -I {} sph2pipe -p {} "$fname.wav"
    # increase volume
    sox "$fname.wav" "$fname+vol.wav" vol $(sox "$fname.wav" -n stat -v 2>&1)

    fname="$fname+vol.wav"
    bitrate=`soxi -b $fname`
    
    # make sox commands for trimming & arguments for splicing
    # first context (head of the file)
    spliceArg[1]=`python -c "print ${line[1]} + $offset"`
    trim[1]="<(sox $fname -p trim 0 ${spliceArg[1]})"
    
    # contexts & hits in middle of file
    len=${#line[@]}
    for (( i=2; i<$len; i++ ));
    do
	spliceArg[i]=`python -c "print ${line[i]} + ($i-1)*(2*$offset +$leeway)"`
	
	soff=`python -c "print ${line[i-1]} - $offset - $leeway"`
	eoff=`python -c "print ${line[i]} + $offset"`
	
	if [ $((i%2)) -eq 0 ];
	then
	    # extract hit & create a noise file of same duration
	    trim[i]="<(sox $fname -p trim $soff =$eoff | sox - -b $bitrate -p synth pinknoise vol 0.5)"
	else
	    # extract context around hit
	    trim[i]="<(sox $fname -p trim $soff =$eoff)"
	fi
    done
    
    # tail end context
    soff=`python -c "print ${line[$len-1]} - $offset - $leeway"`
    trim[$len]="<(sox $fname -p trim $soff)"

    fout="${line[0]}+vol+noise.wav"
    command="sox ${trim[*]} -b $bitrate $fout splice ${spliceArg[*]}"
    #command="sox -V ${trim[*]} -b $bitrate $fout splice ${spliceArg[*]}"
    echo "$command"
    if eval "$command"; then
	echo "---> Successful for $fname"
    else
	echo "---> Unsuccessful for $fname"
    fi
    
    # unsetting array variables - very important!!!!
    unset trim
    unset spliceArg   

done < hits_start_end.txt

######
# Make mp3s and duplicate so we have 1 audio/hit
# even when there are multiple hits per original Switchboard recording
######
while read line terminalID
do
    lame -r -s 8 -m m -a -b 32 <(find . -name "${line}+vol+noise.wav") "$line$terminalID.mp3"
done < sph_files.txt

#### maybe add a line to remove wav files?

#### Useful references
# splice example from sox manual: http://sox.sourceforge.net/sox.html
# http://linguistics.berkeley.edu/plab/guestwiki/index.php?title=Sox_in_phonetic_research
# http://sox.10957.n7.nabble.com/Replace-sound-with-silence-td4082.html


### Note1 on SOX command: it's important to specify the bitrate both for output of synth, and for the final output file, because (as explained in the Berkley wiki page), sox default output is 32-bit, which is not readable by some audio programs, including Praat.