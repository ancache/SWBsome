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

/// sph-files.py & make-mp3s(2).sh
- sph-files.py outputs 2 txt files, to be used to run the shell scripts. File 1 is "hits_start_end.txt", used by make-mp3s2.sh. File 2 is "sph_files.xt", used by make-mp3s.sh. sph-files.py needs to be updated with the correct path to Switchboard on your computer.
- make-mp3s.sh - used to convert to mp3s those NIST Sphere files in the Switchboard where EZRA targets were found.
- make-mp3s2.sh - both converts Sphere files to mp3 files, and replaces certain segments (locations of "some") with noise.
- make-mp3s(2).sh require: sph2pipe (from LDC website) and Lame. Additionally, make-mp3s2.sh requires SoX.