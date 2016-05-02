import sys
import re
import math
import os
import string
from decimal import Decimal


class naivebayes:
    def __init__(self, master):
        test_prediction = {}
        dev_prediction = {}
        test_pred_values = {}
        dev_pred_values = {}
        prob_other = {}
        word_dict = {}
        class_doc_stats = {}
        class_prob = {}
        vocab_stats = {}
        predicted_class = ''
        pred_prob = []


def read_model_probs(prob_other, class_doc_stats, class_prob, word_dict, model_file):
    f = open(model_file, "r")
    model_content = f.read().split('$@%')
    class_stats = [x for x in model_content[0].replace('\n', ' ').split(' ') if x != '']
    tot_docs = 0.0
    word_count = 0.0
    for stats in class_stats:
        classname_stat = stats.split(':')
        doccount_word_count = classname_stat[1].split(',')
        class_doc_stats[classname_stat[0]] = (int(doccount_word_count[0]), int(doccount_word_count[1]))
        tot_docs += int(doccount_word_count[0])
    prob_content = str(model_content[1]).replace('\n#', '#').replace('\n', ' ').split('@#!')
    prob_content = [x for x in prob_content if x != ' ']
    for model_details in prob_content:
        model_probs = [x for x in model_details.split(' ') if x != '']
        word = model_probs[0]
        for class_prob_details in model_probs[1:]:
            class_probval = class_prob_details.split(':')
            class_name = class_probval[0]
            if word in word_dict:
                word_dict[word][class_name] = class_probval[1]
            else:
                word_dict[word] = {}
                word_dict[word][class_name] = class_probval[1]
    for class_name in class_doc_stats:
        class_prob[class_name] = class_doc_stats[class_name][0] / tot_docs
        word_count += class_doc_stats[class_name][1]
        prob_other[class_name] = 1.0 / (class_doc_stats[class_name][1] + len(word_dict))


def predict_class(prediction, prob_other, class_doc_stats, class_prob, word_list, word_dict):
    prob_values = []
    new_prob_values = []
    for class_name in class_prob:
        prob_values.append((class_name, class_prob[class_name]))
    inpfile = open("stopWords.txt", "r")
    line = inpfile.readline()
    stopWords = []
    while line:
        stopWord = line.strip()
        stopWords.append(stopWord)
        line = inpfile.readline()
    inpfile.close()
    for val in prob_values:
        prob = math.log(val[1], 2)
        class_name = val[0]
        for word in word_list:
            word = word.lower()
            # val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*[a-zA-Z]+[a-zA-Z0-9]*$", word)
            # if (word in stopWords):
            #	continue
            if word in word_dict:
                prob = prob + math.log(Decimal(word_dict[word][class_name]), 2)
            else:
                prob = prob + math.log(Decimal(prob_other[class_name]), 2)
        new_prob_values.append((class_name, prob))
    prob_values = new_prob_values
    prob_values.sort(key=lambda tup: tup[1], reverse=True)
    return prob_values, prob_values[0][0]


def dir_prediction(prediction, dir_name, prob_other, class_doc_stats, class_prob, word_dict):
    test_pred = {}
    for filename in os.listdir(dir_name):
        f = open(os.path.join(dir_name, filename), "r")
        sentence_list = f.read().split('\n')
        word_list = []
        for sentence in sentence_list:
            new_word_list = [x for x in sentence.split() if x != '']
            new_word_list = [x for x in new_word_list if x != '']
            if new_word_list:
                word_list.extend(new_word_list)
        pred_prob, predicted_class = predict_class(prediction, prob_other, class_doc_stats, class_prob, word_list,
                                                   word_dict)
        if predicted_class in prediction:
            prediction[predicted_class].append(filename)
        else:
            prediction[predicted_class] = []
            prediction[predicted_class].append(filename)
        test_pred[filename] = []
        test_pred[filename] = pred_prob
    return prediction, test_pred


def analyze_dev_prediction(pred, dev_path, class_name):
    if class_name in pred:
        print('Prediction for :' + str(class_name))
        class_filelist = os.listdir(dev_path)
        print('tot in pred list:' + str(len(pred[class_name])))
        compare_set = set(pred[class_name])
        matches = len([x for x in class_filelist if x in compare_set])
        print('no of files:' + str(len(class_filelist)))
        per_match = (matches / len(class_filelist)) * 100
        print(' per match' + str(per_match))
    else:
        print("0% match")


def main(argv):
    test_prediction = {}
    dev_prediction = {}
    test_pred_values = {}
    dev_pred_values = {}
    prob_other = {}
    word_dict = {}
    class_doc_stats = {}
    class_prob = {}
    vocab_stats = {}
    predicted_class = ''
    pred_prob = []
    print("######################################################")
    if argv:
        model_file = argv[0]
        test_dir = argv[1]
        pred_file = argv[2]
    read_model_probs(prob_other, class_doc_stats, class_prob, word_dict, model_file)
    # dev_dir=test_dir.replace('test','dev')
    # for filename in os.listdir(dev_dir):
    #	if(os.path.isdir(os.path.join(dev_dir,filename))):
    #		dev_prediction,dev_pred_values=dir_prediction(dev_prediction,os.path.join(dev_dir,filename),prob_other,class_doc_stats,class_prob,word_dict)
    #		print(dev_prediction)
    #		analyze_dev_prediction(dev_prediction,os.path.join(dev_dir,filename),filename)
    test_prediction, test_pred_values = dir_prediction(test_prediction, test_dir, prob_other, class_doc_stats,
                                                       class_prob, word_dict)
    pos_cnt = 0
    neg_cnt = 0
    for docno in test_pred_values:
        if test_pred_values[docno][0][0] == "pos":
            pos_cnt += 1.0
        else:
            neg_cnt += 1.0
        print('DocNo:' + str(docno))
        print('Pred Values:' + str(test_pred_values[docno]))
    print(' Pos cnt :' + str(pos_cnt) + ' Neg cnt :' + str(neg_cnt))


# main(sys.argv[1:])

def classifyReviews(reviewList):
    prob_other = {}
    word_dict = {}
    class_doc_stats = {}
    class_prob = {}
    model_file = "model.txt"
    test_prediction = {}
    read_model_probs(prob_other, class_doc_stats, class_prob, word_dict, model_file)
    test_pred = []
    for review in reviewList:
        sentence_list = review.split('\n')
        word_list = []
        for sentence in sentence_list:
            new_word_list = [x for x in sentence.split() if x != '']
            new_word_list = [x for x in new_word_list if x != '']
            if new_word_list:
                word_list.extend(new_word_list)
        pred_prob, predicted_label = predict_class(test_prediction, prob_other, class_doc_stats, class_prob, word_list,
                                                   word_dict)
        test_pred.append(predicted_label)

    return test_pred
