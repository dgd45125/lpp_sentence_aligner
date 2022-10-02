This is software which aligns sentences from two translations of "The Little Prince." 

Under the hood, the hunalign utility is used for the alignment. Hunalign needs to be downloaded and installed in the working directory. Please see the --download-hunalign argument below. 

The source material for the alignment is the first 6 sections of the story book texts. These occur in a "RosettaStone" and need to be present in the working directory. Please see the --download-RosettaStone argument below. To get a list of the languages available in the RosettaStone, see the --print-languages argument below.  

A simple alignment will run hunalign just using the available text sentences. See the --basic-alignment argument below.

An advanced alignment will scan OPUS for available parallel dictionaries and then use the longest one during the alignment process. It may be the case that the algorithm works better in one direction than the other (i.e., you may want to try both language1 -> language2 and language2 -> language1).


Arguments:

--help 

	will print this help message.

--download-RosettaStone

	will download the RosettaStone directory into the working directory

--download-hunalign

	will download and install hunalign into the working directory

--print-languages 

	will print the languages available in the RosettaStone.

--basic-alignment language1 language2

	performs a basic alignment (no bilingual dictionary) between language1 and language2

--advanced-alignment language1 language2

	performs a basic alignment between language1 and language2 by searching OPUS for all available parallel dictonaries, converting the largest properly formatted one to hunalign format, and then providing it to hualign for the alignment.


Details:




References:

Sabrina Stehwien, Lena Henke, Jon T. Hale, Jonathan Brennan, Lars Meyer (2020),
The Little Prince in 26 Languages: Towards a Multilingual Neuro-Cognitive Corpus.
Workshop on Linguistic and Neurocognitive Resources (LiNCR 2020), pages 43-69.
Language Resources and Evaluation Conference (LREC 2020), Marseille, France.