SWBsome
=======
/// swb-search.py 
- before running, edit the path variable to the location of Switchboard on your computer
- run without arguments: python swb-search.py 
- searches the Switchboard NXT files for occurrences of the target ("some") using XPath queries (needs lxml module)
- saves hits in a list of dictionaries, which it pickles to swbsomes.pkl
- creates transcripts for (the entire conversation in) files where target was found
- transcripts stored in a dictionary (keys are filenames) of dictionaries (keys are NXT sentence IDs) of lists of words
- transcripts written to disk as swbtranscripts.pkl


/// swb-to-ezra.py
- reads in 'swbsomes.pkl'
- cleans up dataset for loading to Ezra
- stores new dataset to 'swbsomesEZRA.pkl'
- also writes .param files for Ezra import

/// sph-files.py & make-mp3.sh
- used to convert to mp3s those NIST Sphere files in the Switchboard where EZRA targets were found 
- edit sph-files.py with the correct path to Switchboard on your computer, then run to produce a list of filenames (without .sph extension) and NXT terminal ID extensions (appended to filenames to allow multiple hits per mp3 file to be uploaded to EZRA): sph_files.txt
- make-mp3.sh requires: sph2pipe (from LDC website) and Lame. It searches for the files in sph_files.txt, converts to wav, pipes output to lame for mp3 encoding, and saves as filename+NXTterminalID+.mp3