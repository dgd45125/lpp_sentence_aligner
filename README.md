<b>Introduction</b>

This is software which aligns sentences from two translations of "The Little Prince." 

Under the hood, the hunalign utility is used for the alignment. Hunalign needs to be downloaded and installed in the working directory. Please see the --download-hunalign argument below. 

The source material for the alignment is the first 6 sections of the story book texts. These occur in a "RosettaStone" and need to be present in the working directory. Please see the --download-RosettaStone argument below. To get a list of the languages available in the RosettaStone, see the --print-languages argument below.  

A simple alignment will run hunalign just using the available text sentences. See the --basic-alignment argument below.

An advanced alignment will scan OPUS for available parallel dictionaries and then use the longest one during the alignment process. It may be the case that the algorithm works better in one direction than the other (i.e., you may want to try both language1 -> language2 and language2 -> language1).



<b>Dependencies:</b>

os, re, sys, zipfile, shutil, pandas, subprocess, urllib, json, gzip



<b>Arguments</b>:

--help 

	Will print this help message

--download-RosettaStone

	Will download the RosettaStone directory into the working directory

--download-hunalign

	Will download and install hunalign into the working directory

--print-languages 

	Will print the languages available in the RosettaStone

--basic-alignment language1 language2

	Performs a basic alignment (no bilingual dictionary) between language1 and language2


--advanced-alignment language1 language2

	Performs a basic alignment between language1 and language2 by searching OPUS for all available parallel dictonaries, converting the largest properly formatted one to hunalign format, and then providing it to hualign for the alignment


<b>Details</b>

Performing an alignment will store the reconstructed sentences from the RosettaStone in the directories language1_prepped and language2_prepped, with one sentence per line and separate files for each section.

The resulting alignments will be stored in the directory language1-language2_(basic|advanced)\_alignments depending on whether a basic or advanced alignment was performed.

If an advanced alignment is performed, OPUS will be probed for available parallel bilingual dictionaries for the two languages. Each available dictionary is downloaded, the number of rows is recorded, and then the dictionary is deleted. The largest (heuristic for best) dictionary is then redownloaded and converted into the format desired by hunalign. This dictionary is saved into the working directory as lang2-lang1.dic. The downloaded dictionary is then deleted again. The hunalign-formatted dictionary is past to hunalign for the alignment process.



<b>References:</b>

Sabrina Stehwien, Lena Henke, Jon T. Hale, Jonathan Brennan, Lars Meyer (2020),
The Little Prince in 26 Languages: Towards a Multilingual Neuro-Cognitive Corpus.
Workshop on Linguistic and Neurocognitive Resources (LiNCR 2020), pages 43-69.
Language Resources and Evaluation Conference (LREC 2020), Marseille, France.


