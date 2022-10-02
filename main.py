#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys

from utils import *




def main():

	#no command line arguments
	if len(sys.argv) == 1:
		print_help_message()

	#1 command line argument
	elif len(sys.argv) == 2:

		if sys.argv[1] == '--help':
			print_help_message()

		elif sys.argv[1] == '--download-RosettaStone':
			download_RosettaStone()

		elif sys.argv[1] == '--download-hunalign':
			download_Hunalign()			

		elif sys.argv[1] == '--print-languages':
			print(get_available_languages())


		elif sys.argv[1] == '--test':

			lang1 = 'ko'
			lang2 = 'es'

			dic_urls_len_tuples = get_raw_parallel_dictionaries(lang1,lang2)
			raw_dictionary_to_hunalign_file (dic_urls_len_tuples,lang1,lang2)

			#dic_urls_len_tuples.sort(key=lambda x : -x[1])
			#print(dic_urls_len_tuples)


			#for lang in get_available_languages():
			#	print(f"{lang} : {language_abbrev_lookup(lang)}")

			#basic_alignment(language1 = 'french', language2 = 'english', lowercase=False)

			#for sentence in get_language_section_sentences(language = 'english', chapter = '1', lowercase=True):
			#	print(sentence)

			'''
			for lang in get_available_languages():
				print("\n", lang, "\n")

				for section in range(1,7):

					print("\n", section, "\n")

					for sentence in get_language_section_sentences(language = lang, chapter = section, lowercase=False):
						print(sentence)
			'''

		else:
			print("That command line argument is unrecognized. Printing help message.")
			print_help_message()

	
	#3 command line arguments
	elif len(sys.argv) == 4:

		if sys.argv[1] == '--basic-alignment':
			basic_alignment(sys.argv[2], sys.argv[3])

		elif sys.argv[1] == '--advanced-alignment':
			advanced_alignment(sys.argv[2], sys.argv[3])

		else:

			print("That command line argument is unrecognized. Printing help message.")
			print_help_message()



	#something else
	else:
		print("That command line argument is unrecognized. Printing help message.")
		print_help_message()




if __name__ == "__main__":
	main()