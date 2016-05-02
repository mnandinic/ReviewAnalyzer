import sys
import re
import math
import os
from decimal import Decimal
import string
THRESHOLD_FOR_CONSIDERATION = 5
POSITIVE_CLASS = "pos"
NEGATIVE_CLASS = "neg"
SPACE = ' '
EMPTYCHAR = ''
STOPWORDS = {"the", "a","there","then"}

def create_word_dict_for_training_files_for_class(word_dict, train_class_dir, class_name):
    total_word_count = 0
    word_list_for_current_class=[]
    for filename in os.listdir(train_class_dir):
        fopen = open(os.path.join(train_class_dir, filename), "r")
        sentence_list = fopen.read().split('\n')
        for sentence in sentence_list:
            new_word_list = sentence.split()
            if SPACE in new_word_list:
                new_word_list.remove(SPACE)
            if EMPTYCHAR in new_word_list:
                new_word_list.remove(EMPTYCHAR)
            new_word_list = [x for x in new_word_list if x != '']
            word_list_for_current_class.extend(new_word_list)
        
    total_word_count = len(word_list_for_current_class)
    inpfile = open("stopWords.txt", "r")
    line = inpfile.readline()
    stopWords = []
    while line:
         stopWord = line.strip()
         stopWords.append(stopWord)
         line = inpfile.readline()
    inpfile.close()
    for word in word_list_for_current_class:
        word=word.lower()
        #val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*[a-zA-Z]+[a-zA-Z0-9]*$", word)
        #if (word in stopWords):
        #    continue
        if word in word_dict:
            if class_name in word_dict[word]:
                count = word_dict[word][class_name]
                word_dict[word][class_name] = count + 1
            else:
                word_dict[word][class_name] = 1
        else:
            word_dict[word] = {}
            word_dict[word][class_name] = 1
    
    return len(os.listdir(train_class_dir))


def calculate_probability(word_dict, train_class_dir, word_count_dict, probability_dict,
                          class_name):
    for word in word_dict:
        if word in probability_dict:
            if class_name in word_dict[word]:
                probability_dict[word][class_name] = \
                    Decimal(word_dict[word][class_name] + 1) / Decimal(
                        word_count_dict[class_name] + len(word_dict.keys()))
    
            else:
                probability_dict[word][class_name] = \
                    1 / Decimal(
                        word_count_dict[class_name] + len(word_dict.keys()))
    
        else:
            probability_dict[word] = {}
            probability_dict[word][POSITIVE_CLASS] = 1 / Decimal(
            word_count_dict[POSITIVE_CLASS] + len(word_dict.keys()))
            probability_dict[word][NEGATIVE_CLASS] = 1 / Decimal(
            word_count_dict[NEGATIVE_CLASS] + len(word_dict.keys()))
            if class_name in word_dict[word]:
                 probability_dict[word][class_name] = Decimal(
                     word_dict[word][class_name] + 1) \
                                                  / Decimal(
                     word_count_dict[class_name] +
                     len(word_dict.keys()))
            else:
                 probability_dict[word][class_name] = 1 / Decimal(
                 word_count_dict[class_name] + len(word_dict.keys()))



def remove_words_with_frequencies_less_than_threshold(word_list_for_current_class , THRESHOLD_FOR_CONSIDERATION):
    new_word_dict = {}
    for word in word_list_for_current_class.keys():
        if (word_list_for_current_class[word].get(POSITIVE_CLASS,0) + word_list_for_current_class[word].get(NEGATIVE_CLASS,0)) >= THRESHOLD_FOR_CONSIDERATION:
            new_word_dict[word] = word_list_for_current_class[word]

    return new_word_dict


def class_sum(word_list_for_current_class, class_name):
    total = 0
    for word in word_list_for_current_class:
        total += word_list_for_current_class[word].get(class_name,0)
    return total


def main(argv):
    word_dict = {}
    word_count_dict = {}
    probability_dict = {}
    doc_count_dict = {}
    if argv:
        training_dir = argv[0]
        model_file = argv[1]
	
	#creates the class word frequency table
	#returns the count of number of documents of the corresponding class dir sent
    for class_name in os.listdir(training_dir):
        class_dir = os.path.join(training_dir, class_name)
        doc_count_dict[class_name] = create_word_dict_for_training_files_for_class(word_dict, class_dir, class_name)

	#Remove words with frequency less than 5
    new_word_dict = remove_words_with_frequencies_less_than_threshold(word_dict, THRESHOLD_FOR_CONSIDERATION)

	#Calulates the correct number of words being considered
    for class_name in os.listdir(training_dir):
        word_count_dict[class_name] = class_sum(new_word_dict, class_name)

	#Calculate the probabalistic values
    for class_name in os.listdir(training_dir):
        class_dir = os.path.join(training_dir, class_name)
        calculate_probability(new_word_dict, class_dir, word_count_dict, probability_dict,
                              class_name)

	#writes the results of every word into model file						  
    file_handle = open(model_file, "w")
    for m in word_count_dict:
        file_handle.writelines(m + ":" + str(doc_count_dict[m]) + "," + str(word_count_dict[m]) + "\n")
    file_handle.write("$@%" + "\n")
    for k in probability_dict:
        file_handle.writelines("@#!" + k + "\n")
        for j in probability_dict[k]:
            file_handle.writelines(j + ":" + str(probability_dict[k][j]) + "\n")

main(sys.argv[1:])
