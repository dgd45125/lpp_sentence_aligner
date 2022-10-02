import os
import re
import sys
import zipfile
import shutil
import pandas as pd
import subprocess
import urllib
from urllib import request
import json
import gzip




def print_help_message():
	'''
	prints the help message.
	'''

	print('''
This software aligns sentences from two translations of "The Little Prince." See`README.md` and the argument descriptions below.

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
''')





def raw_dictionary_to_hunalign_file (dic_urls_len_tuples,lang1,lang2):
	'''
	Takesa list of (dictionary_url, dictionary_len) tuples, sorts them, redownloads the largest (longest) one, and transforms it into a hunalign-style bilingual dictonary file
	'''

	lang1_copy = lang1
	lang2_copy = lang2
	
	#sort by size
	dic_urls_len_tuples.sort(key=lambda x : -x[1])


	
	try:
		for i in range(len(dic_urls_len_tuples)):

			FLIPPED = False
			print(f"\nTrying {i}th largest bilingual dictionary.\n")

			url = dic_urls_len_tuples[i][0]

			print(f"Bilingual dictionary at URL {url} had the {i}th largest number of rows. Redownloading it and converting to Hunalign format.")


			#if it is not the case that language one is source in downloaded dictionary: flip
			if not lang1==re.findall(r'/(..-..\.dic.gz)',url)[0][:2]:
				print("Flipping bilingual dictionary order\n")
				lang1 = lang2_copy
				lang2 = lang1_copy
				FLIPPED = True


			#re.findall(r'/(..-..\.dic.gz)',url)[0]
			
			urllib.request.urlretrieve(url,f"{lang1}-{lang2}.dic.gz")

			test = pd.read_csv(f"{lang1}-{lang2}.dic.gz", sep= "\t",header=None)
			if len(test.iloc[0]) != 6:
				print("The format of this particular bilingual dictionary is not yet supported. Deleting this one and trying the next one.")
				os.remove(f"{lang1}-{lang2}.dic.gz")
				continue

			raw_dict = pd.read_csv(f"{lang1}-{lang2}.dic.gz", sep= "\t",header=None,names=['A',lang1,lang2,'D','E'])
			raw_dict.drop(columns=['A','D','E'],inplace=True)
			raw_dict[lang1] = raw_dict[lang1].str.lower()
			raw_dict[lang2] = raw_dict[lang2].str.lower()
			raw_dict.reset_index(inplace=True,drop=True)
			print("\nPrinting first 5 rows of the dataframe.")
			print(raw_dict.head())

			user_input = input("\nDoes this look about right (structurally; check output for final content): [y/n]")
			if user_input == 'n' or user_input == 'N':
				print("\nOK. Trying the next bilingual dictonary")
				os.remove(f"{lang1}-{lang2}.dic.gz")
				continue

			elif user_input == 'y' or user_input =='Y':
				print("\nOK. Converting the dataframe to a hunalign format bilingual dictionary and saving it to the working directory. NB the hunalign format bilingual dictionary should be TARGET @ SOURCE")
				os.remove(f"{lang1}-{lang2}.dic.gz")


				if FLIPPED == False:
					f = open(f"{lang2}-{lang1}.dic","w")
					for j in range(len(raw_dict)):
						f.write(f"{raw_dict.iloc[j][lang2]} @ {raw_dict.iloc[j][lang1]}\n")
					f.close()

				else:
					f = open(f"{lang1}-{lang2}.dic","w")
					for j in range(len(raw_dict)):
						f.write(f"{raw_dict.iloc[j][lang1]} @ {raw_dict.iloc[j][lang2]}\n")
					f.close()
			


				print("\n Done")
				
				return


			else:
				print("\nOK. Trying the next bilingual dictonary")
				os.remove(f"{lang1}-{lang2}.dic.gz")
				continue

		sys.exit(f"\nI have run out of bilingual dictionaries to try. Exiting gracefully.")
		os.remove(f"{lang1}-{lang2}.dic.gz")
		

	except:
		print("\nSomething has gone wrong. Probably trying to read an empty file. Exiting gracefully.")
		#os.remove(f"{lang1}-{lang2}.dic.gz")




def get_raw_parallel_dictionaries(lang1, lang2):
	'''
	It is assumed that langauge availability checking is done at a higher level.
	Takes lang1 and lang2 as input. Pings the OPUS API for all available corpora, checking to see if they contain a parallel dictionary. 
	If a parallel dictionary is found, the URL is extracted and the paralell dictionary is downloaded and its size is recorded. It is then deleted.
	Returns a list containing (dictionary_url, dictionary_len) tuples 
	'''

	print("Searching for parallel dictionaries from OPUS")

	corpus_lang1_lang2_query = f'http://opus.nlpl.eu/opusapi/?&source={lang1}&target={lang2}&corpora=True'

	#this returns the available corpora for the queried source and target languages
	response = request.urlopen(corpus_lang1_lang2_query)
	response = response.read().decode('utf-8')
	response = json.loads(response)
	response = response['corpora']

	dic_urls_len_tuples = []

	#probe all of the returned corpora, check if they have an associated bilingual dictionary
	#if they do, download it and record how many items it has
	for corpus in response:
		specific_corpus_query = f'http://opus.nlpl.eu/opusapi/?corpus={corpus}&source={lang1}&target={lang2}'

		response = request.urlopen(specific_corpus_query)
		response = response.read().decode('utf-8')
		response = json.loads(response)

		for thing in response['corpora']:
			if 'dic' in thing['url']:

				dic_url = thing['url']
				print(f"Found a dictionary at {dic_url}")

				#print(f"Downloading {dic_url} into the working directory.")

				#download the compressed bilingual dictionary
				urllib.request.urlretrieve(str(dic_url),'candidate-bilingual-dictionary.gz')

				#unzip the dictionary and write to text file
				with gzip.open('candidate-bilingual-dictionary.gz', 'rb') as f_in:
					with open('candidate-bilingual-dictionary.txt', 'wb') as f_out:
						shutil.copyfileobj(f_in, f_out)

				dictionary_len = sum(1 for line in open('candidate-bilingual-dictionary.txt'))

				#delete the compressed bilingual dictionary
				os.remove('candidate-bilingual-dictionary.gz')
				#delete the uncompressed bilingual dictionary
				os.remove('candidate-bilingual-dictionary.txt')

				dic_urls_len_tuples.append((dic_url,dictionary_len))

	return dic_urls_len_tuples



def advanced_alignment(language1, language2, lowercase=True):
	'''
	Takes language1 and language2 and performs an advanced alignment between them with hunalign i.e. (a bilingual dictionary is used).
	The constructed bilingual dictionary is saved to the working directory.
	Stores the 6 aligned sections in a new directory called language1-language2_advanced_alignments.
	'''

	#check that language1 is valid
	if language1 not in get_available_languages():
		sys.exit(f"Language {language1} is not included in the RosettaStone. Exiting gracefully.")
	#check that language2 is valid
	if language2 not in get_available_languages():
		sys.exit(f"Language {language2} is not included in the RosettaStone. Exiting gracefully.")

	print(f"Starting advanced alignment with {language1} and {language2}")


	print(f"Saving the {language1} and {language2} chapter sentences (one per line; from the RosettaStone) into dirs `{language1}_prepped` and `{language2}_prepped`.")
	for i in range(1,7):

		lang1_sentences = get_language_section_sentences(language = language1, chapter = i, lowercase=lowercase)
		save_language_section_sentences(language = language1, chapter = i, sentences=lang1_sentences)

		lang2_sentences = get_language_section_sentences(language = language2, chapter = i, lowercase=lowercase)
		save_language_section_sentences(language = language2, chapter = i, sentences=lang2_sentences)


	lang1_abrev = language_abbrev_lookup(language1)
	lang2_abrev = language_abbrev_lookup(language2)

	dic_urls_len_tuples = get_raw_parallel_dictionaries(lang1_abrev,lang2_abrev)
	raw_dictionary_to_hunalign_file (dic_urls_len_tuples,lang1_abrev,lang2_abrev)


	print(f"Making a directory `{language1}-{language2}_advanced_alignments` to store the section alignments in.")
	if not os.path.exists(f"{language1}-{language2}_advanced_alignments"):
		os.mkdir(f"{language1}-{language2}_advanced_alignments")

	for i in range(1,7):
		print(f"\nCalling hunalign for section {i}\n")
		command = f" hunalign-1.1/src/hunalign/hunalign {lang2_abrev}-{lang1_abrev}.dic {language1}_prepped/{language1}_section{i}.txt {language2}_prepped/{language2}_section{i}.txt -utf -realign -text "
		f = open(f"{language1}-{language2}_advanced_alignments/{language1}-{language2}_section{i}","w")
		process = subprocess.call(command.split(),stdout=f)
		f.close()








def basic_alignment(language1, language2, lowercase=True):
	'''
	Takes language1 and language2 and performs a basic alignment between them with hunalign i.e. (a bilingual dictionary is not used).
	Stores the 6 aligned sections in a new directory called language1-language2_basic_alignments.
	'''

	#check that language1 is valid
	if language1 not in get_available_languages():
		sys.exit(f"Language {language1} is not included in the RosettaStone. Exiting gracefully.")
	#check that language2 is valid
	if language2 not in get_available_languages():
		sys.exit(f"Language {language2} is not included in the RosettaStone. Exiting gracefully.")

	print(f"Starting basic alignment with {language1} and {language2}")


	print(f"Saving the {language1} and {language2} chapter sentences (one per line; from the RosettaStone) into dirs `{language1}_prepped` and `{language2}_prepped`.")
	for i in range(1,7):

		lang1_sentences = get_language_section_sentences(language = language1, chapter = i, lowercase=lowercase)
		save_language_section_sentences(language = language1, chapter = i, sentences=lang1_sentences)

		lang2_sentences = get_language_section_sentences(language = language2, chapter = i, lowercase=lowercase)
		save_language_section_sentences(language = language2, chapter = i, sentences=lang2_sentences)

	print(f"Making a directory `{language1}-{language2}_basic_alignments` to store the section alignments in.")
	if not os.path.exists(f"{language1}-{language2}_basic_alignments"):
		os.mkdir(f"{language1}-{language2}_basic_alignments")

	for i in range(1,7):
		print(f"\nCalling hunalign for section {i}\n")
		command = f"hunalign-1.1/src/hunalign/hunalign hunalign-1.1/data/null.dic {language1}_prepped/{language1}_section{i}.txt {language2}_prepped/{language2}_section{i}.txt -utf -realign -text "
		f = open(f"{language1}-{language2}_basic_alignments/{language1}-{language2}_section{i}","w")
		process = subprocess.call(command.split(),stdout=f)
		f.close()




def save_language_section_sentences(language, chapter, sentences):
	'''
	saves the chapter sentences for a language. If a directory does not already exist with the
	prepared section files, one is created. The chapter sentences are then saved as text files
	with one sentence per line.
	'''
	if not os.path.exists(f"{language}_prepped"):
		os.mkdir(f"{language}_prepped")

	f = open(f"{language}_prepped/{language}_section{chapter}.txt", "w")
	for line in sentences:
		f.write(line + "\n")
	f.close()


def get_language_section_sentences(language, chapter, lowercase):
	'''
	takes a language and a section as parameters and returns a list of sentences (either lowercased or not)
	from the RosettaStone with one sentence per line and tokens separated by spaces.
	'''

	#check that language is valid
	if language not in get_available_languages():
		sys.exit(f"Language {language} is not included in the RosettaStone. Exiting gracefully.")
	#check that chapter is valid
	if chapter not in [1,2,3,4,5,6]:
		sys.exit(f"Chapter {chapter} is not included in the RosettaStone. Exiting gracefully.")

	section = pd.read_csv(f'RosettaStone/lpp_{language}_chapter{chapter}_RosettaStone.txt',header=None)

	sentences = []

	#buffer to build sentences in
	sentence = ''

	for i in range(len(section)):

		#at new sentence, save out  previously built sentence and flush buffer,
		#but only if not the very first word
		if len(str(section.iloc[i][1])) == 3:
			if i != 0:
				if lowercase == True:
					sentences.append(sentence[:-1].lower()) #chops off trailing space behind final word
				else: 
					sentences.append(sentence[:-1])
			sentence = ''

		sentence += str(section.iloc[i][0]+' ')
		
	#save out final sentence
	if lowercase == True:
		sentences.append(sentence[:-1].lower()) #chops off trailing space behind final word
	else: 
		sentences.append(sentence[:-1])

	return sentences


def download_Hunalign():
	'''
	downloads the hunalign software, decompresses it, and builds it in the working directory.
	ftp://ftp.mokk.bme.hu/Hunglish/src/hunalign/latest/hunalign-1.1.tgz
	'''
	
	print("Downloading hunalign-1.1.tgz into the working directory.")
	urllib.request.urlretrieve("ftp://ftp.mokk.bme.hu/Hunglish/src/hunalign/latest/hunalign-1.1.tgz","hunalign-1.1.tgz")
	
	print("\nDecompressing hunalign-1.1.tgz\n")
	process = subprocess.Popen("tar zxvf hunalign-1.1.tgz".split())
	process.wait()

	print("\nBuilding hunalign\n")
	os.chdir("hunalign-1.1/src/hunalign")
	process = subprocess.Popen("make".split())
	process.wait()	

	print("\nDeleting hunalign-1.1.tgz")
	os.chdir("../../..")
	os.remove("hunalign-1.1.tgz")

	print("\nDone")


def download_RosettaStone():
	'''
	downloads the RosettaStone directory from the web host into the working directory. 
	https://owncloud.gwdg.de/index.php/s/Fve0bs0xWGJZ6TA
	'''
	
	print("Downloading RosettaStone.zip into the working directory.")
	urllib.request.urlretrieve("https://owncloud.gwdg.de/index.php/s/Fve0bs0xWGJZ6TA/download?path=%2F&files=RosettaStone&downloadStartSecret=98jcpz4u45","RosettaStone.zip")
	
	print("Making a directory `RosettaStone` (or overwriting the existing version) to store the files in.")
	if os.path.exists("RosettaStone"):
		shutil.rmtree("RosettaStone")
	os.mkdir("RosettaStone")

	print("Extracting the files.")
	with zipfile.ZipFile("RosettaStone.zip", "r") as zip_ref:
		zip_ref.extractall()
	
	print("Deleting RosettaStone.zip.")
	os.remove("RosettaStone.zip")
	print("Done")


def get_num_files(language):
	'''
	takes as input a lowercase language string and checks whether there are 6 chapters present in 
	the RosettaStone directory. Returns the number of chapters present.
	'''

	count = 0
	for file in os.listdir('./RosettaStone/'):
		if language in file:
			count+=1
	return(count)


def get_available_languages():
	'''
	Scans the RosettaStone directory and pulls out the available languages.
	If a found language does not have all 6 files, then an exception is thrown and the program exits gracefully.
	returns a set of lower case strings of the found languages.  
	'''

	if not os.path.exists("RosettaStone"):
		sys.exit(f"It looks like the RosettaStone has not yet been downloaded. Try the argument --download-RosettaStone. Exiting gracefully.")

	languages = []
	for file in  os.listdir('./RosettaStone/'):
		languages.append(re.findall('lpp_(.*)_chapter',file)[0])

	for language in languages:
		num_files = get_num_files(language)
		if num_files != 6:
			sys.exit(f"Language {language} only has {num_files} files. Exiting gracefully.")
	languages =  set(languages)
	return languages


def language_abbrev_lookup(language):
	'''
	takes a RosettaStone lower-case language as input and returns the Opus 2 letter abbreviation
	'''
	language_lookup = {'arabic':'ar',
				   'chinese':'zh',
				   'czech':'cs',
				   'danish':'da',
				   'dutch':'nl',
				   'english':'en',
				   'finnish':'fi',
				   'french':'fr',
				   'german':'de',
				   'greek':'el',
				   'hindi':'hi',
				   'hungarian':'hu',
				   'indonesian':'id',
				   'italian':'it',
				   'japanese':'ja',
				   'korean':'ko',
				   'norwegian':'no',
				   'polish':'pl',
				   'portuguese':'pt',
				   'russian':'ru',
				   'slovak':'sk',
				   'spanish':'es',
				   'swedish':'sv',
				   'turkish':'tr',
				   'ukrainian':'uk',
				   'vietnamese':'vi'}
	return language_lookup[str(language)]