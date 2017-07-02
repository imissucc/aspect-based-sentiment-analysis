
#!/usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------------------#
#       author: BinhDT                                                                      #
#       description: preprocess data like exporting aspect, word2vec, load embedding        #
#       prepare data for training                                                           #
#       last update on 02/7/2017                                                    		#
#-------------------------------------------------------------------------------------------#

import numpy as np
import os
import re
import csv
from collections import Counter
import codecs
from collections import defaultdict
import xml.etree.ElementTree as ET



def load_embedding(data_dir, flag_addition_corpus, flag_word2vec):
    word_dict = dict()
    embedding = list()
    
    f_corpus = codecs.open('../data/corpus_for_word2vec.txt', 'w', 'utf-8')

    for file in os.listdir(data_dir + '/ABSA_SemEval2015/'):
        if file.endswith('.txt'):
            f_processed = codecs.open(data_dir + '/ABSA_SemEval2015/' + file, 'r', 'utf-8')
            for line in f_processed:
                f_corpus.write(line.replace('{a-positive}', '').replace('{a-negative}', '').replace('{a-neutral}', ''))

    if (flag_addition_corpus):
        for file in os.listdir(data_dir + '/Addition_Restaurants_Reviews_For_Word2vec'):
            try:
                with codecs.open(data_dir + '/Addition_Restaurants_Reviews_For_Word2vec/' + file, 'rb', 'utf-8') as csvfile:
                    if file == '1-restaurant-test.csv':
                        reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
                        for row in reader:
                            f_corpus.write(re.sub(r'[.,:;?!\n()\\]','', row[0]).lower() + '\n')
                    elif file == '1-restaurant-train.csv':
                        reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
                        for row in reader:
                            f_corpus.write(re.sub(r'[.,:;?!\n()\\]','', row[1]).lower() + '\n')
                    else:
                        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                        for row in reader:        
                            f_corpus.write(re.sub(r'[.,:;?!\n()\\]','', row[9]).lower() + '\n')
            except (IndexError, UnicodeEncodeError) as error:
                continue

    f_corpus.close()

    if (flag_word2vec):
        os.system('cd ../fastText && ./fasttext cbow -input ../data/corpus_for_word2vec.txt -output ../data/cbow -dim 100 -minCount 2 -epoch 300')
    
    f_vec = codecs.open('../data/cbow.vec', 'r', 'utf-8')
    idx = 0
    for line in f_vec:
        
        if len(line) < 100:
            continue
        else:
            component = line.strip().split(' ')
            word_dict[component[0].lower()] = idx
            word_vec = list()
            for i in range(1, len(component)):
                word_vec.append(float(component[i]))
            embedding.append(word_vec)
            idx = idx + 1
    f_vec.close()
    word_dict['<padding>'] = idx
    embedding.append([0.] * len(embedding[0]))
    word_dict_rev = {v: k for k, v in word_dict.iteritems()}
    return word_dict, word_dict_rev, embedding


def load_stop_words():
    stop_words = list()
    fsw = codecs.open('../dictionary/stop_words.txt', 'r', 'utf-8')
    for line in fsw:
        stop_words.append(line.strip())
    fsw.close()
    return stop_words

def export_aspect(data_dir):
    aspect_list = list()
    
    fa = codecs.open('../dictionary/aspect.txt', 'w', 'utf-8')
    for file in os.listdir(data_dir + '/ABSA_SemEval2015'):
        if not file.endswith('.txt'):
            continue
            
        f = codecs.open(data_dir + '/ABSA_SemEval2015/' + file, 'r', 'utf-8')
        for line in f:
            for word in line.split(' '):
                if '{a-' in word:
                    aspect_list.append(word.split('{')[0].strip())
        f.close()
            
    for w in sorted(set(aspect_list)):
        fa.write(w + '\n')
    
    fa.close()
    
    return set(aspect_list)


def change_xml_to_txt_v1(data_dir):
    train_filename = data_dir + '/ABSA_SemEval2015/ABSA-15_Restaurants_Train_Final.xml'
    test_filename = data_dir + '/ABSA_SemEval2015/ABSA15_Restaurants_Test.xml'

    train_text = codecs.open(data_dir + '/ABSA_SemEval2015/ABSA-15_Restaurants_Train_Final.txt', 'w', 'utf-8')
    test_text = codecs.open(data_dir + '/ABSA_SemEval2015/ABSA15_Restaurants_Test.txt', 'w', 'utf-8')

    reviews = ET.parse(train_filename).getroot().findall('Review')
    sentences = []
    for r in reviews:
        sentences += r.find('sentences').getchildren()

    for i in range(len(sentences)):
        try:
            sentence = sentences[i].find('text').text
            new_sentence = sentences[i].find('text').text
            opinions = sentences[i].find('Opinions').findall('Opinion')
            for opinion in opinions:
                start = int(opinion.get('from'))
                end = int(opinion.get('to'))
                polarity = opinion.get('polarity')
                if (end != 0):
                    new_sentence = new_sentence.replace(sentence[start:end],
                                                        sentence[start:end].replace(' ', '_') + '{a-' + polarity + '}')
                else:
                    new_sentence = new_sentence + ' unknowntoken{a-' + polarity + '}'
                    
            train_text.write(re.sub(r'[.,:;?!\n()\\]','', new_sentence).lower() + '\n')

        except AttributeError:
            continue

    reviews = ET.parse(test_filename).getroot().findall('Review')
    sentences = []
    for r in reviews:
        sentences += r.find('sentences').getchildren()

    for i in range(len(sentences)):
        try:
            sentence = sentences[i].find('text').text
            new_sentence = sentences[i].find('text').text
            opinions = sentences[i].find('Opinions').findall('Opinion')
            for opinion in opinions:
                start = int(opinion.get('from'))
                end = int(opinion.get('to'))
                polarity = opinion.get('polarity')
                if (end != 0):
                    new_sentence = new_sentence.replace(sentence[start:end],
                                                        sentence[start:end].replace(' ', '_') + '{a-' + polarity + '}')
                else:
                    new_sentence = new_sentence + ' unknowntoken{a-' + polarity + '}'
                    
            test_text.write(re.sub(r'[.,:;?!\n()\\]','', new_sentence).lower() + '\n')

        except AttributeError:
            continue

def sortchildrenby(parent, attr):
    parent[:] = sorted(parent, key=lambda child: int(child.get(attr)))

def change_xml_to_txt_v2(data_dir):
    train_filename = data_dir + '/ABSA_SemEval2015/ABSA-15_Restaurants_Train_Final.xml'
    test_filename = data_dir + '/ABSA_SemEval2015/ABSA15_Restaurants_Test.xml'

    train_text = codecs.open(data_dir + '/ABSA_SemEval2015/ABSA-15_Restaurants_Train_Final.txt', 'w', 'utf-8')
    test_text = codecs.open(data_dir + '/ABSA_SemEval2015/ABSA15_Restaurants_Test.txt', 'w', 'utf-8')

    reviews = ET.parse(train_filename).getroot().findall('Review')
    sentences = []
    for r in reviews:
        sentences += r.find('sentences').getchildren()

    for i in range(len(sentences)):
        try:
            new_sentence = sentences[i].find('text').text
            opinions = sentences[i].find('Opinions').findall('Opinion')
            sortchildrenby(opinions, 'from')
            bias = 0
            for opinion in opinions:
                start = int(opinion.get('from'))
                end = int(opinion.get('to'))
                polarity = opinion.get('polarity')
                category = opinion.get('category')
                target = opinion.get('target').lower()
                if (end != 0):
                    new_sentence = new_sentence[:bias+end] + ' ' + category + '{a-' + polarity + '}' + new_sentence[bias+end:]
                    bias = bias + len(category + '{a-' + polarity + '}') + 1
                else:
                    new_sentence = new_sentence + ' ' + category + '{a-' + polarity + '}'
            train_text.write(re.sub(r'[.,:;?!\n()\\]','', new_sentence).lower() + '\n')

        except AttributeError:
            continue

    reviews = ET.parse(test_filename).getroot().findall('Review')
    sentences = []
    for r in reviews:
        sentences += r.find('sentences').getchildren()

    for i in range(len(sentences)):
        try:
            new_sentence = sentences[i].find('text').text
            opinions = sentences[i].find('Opinions').findall('Opinion')
            sortchildrenby(opinions, 'from')
            bias = 0
            for opinion in opinions:
                start = int(opinion.get('from'))
                end = int(opinion.get('to'))
                polarity = opinion.get('polarity')
                category = opinion.get('category')
                if (end != 0):
                    new_sentence = new_sentence[:bias+end] + ' ' + category + '{a-' + polarity + '}' + new_sentence[bias+end:]
                    bias = bias + len(category + '{a-' + polarity + '}') + 1
                else:
                    new_sentence = new_sentence + ' ' + category + '{a-' + polarity + '}'
                    
            test_text.write(re.sub(r'[.,:;?!\n()\\]','', new_sentence).lower() + '\n')

        except AttributeError:
            continue

def change_xml_to_txt_v3(data_dir):
    train_filename = data_dir + '/ABSA_SemEval2015/ABSA-15_Restaurants_Train_Final.xml'
    test_filename = data_dir + '/ABSA_SemEval2015/ABSA15_Restaurants_Test.xml'

    train_text = codecs.open(data_dir + '/ABSA_SemEval2015/ABSA-15_Restaurants_Train_Final.txt', 'w', 'utf-8')
    test_text = codecs.open(data_dir + '/ABSA_SemEval2015/ABSA15_Restaurants_Test.txt', 'w', 'utf-8')

    reviews = ET.parse(train_filename).getroot().findall('Review')
    sentences = []
    for r in reviews:
        sentences += r.find('sentences').getchildren()

    for i in range(len(sentences)):
        try:
            new_sentence = sentences[i].find('text').text
            opinions = sentences[i].find('Opinions').findall('Opinion')
            sortchildrenby(opinions, 'from')
            bias = 0
            last_start = -1
            last_end = -1
            for opinion in opinions:
                start = int(opinion.get('from'))
                end = int(opinion.get('to'))
                polarity = opinion.get('polarity')
                category = opinion.get('category')
                target = opinion.get('target').lower()
                if (end != 0):
                    if (last_start == start and last_end == end):
                        new_sentence = new_sentence[:bias+len(target)+start+1] + category + '{a-' + polarity + '}' + new_sentence[bias+len(target)+start:]
                        bias = bias + len(category + '{a-' + polarity + '}') + 1
                    else:
                        new_sentence = new_sentence[:bias+start] + category + '{a-' + polarity + '}' + new_sentence[bias+end:]
                        bias = bias + len(category + '{a-' + polarity + '}') - len(target)
                else:
                    new_sentence = new_sentence + ' ' + category + '{a-' + polarity + '}'

                last_start = start
                last_end = end
            train_text.write(re.sub(r'[.,:;?!\n()\\]','', new_sentence).lower() + '\n')

        except AttributeError:
            continue

    reviews = ET.parse(test_filename).getroot().findall('Review')
    sentences = []
    for r in reviews:
        sentences += r.find('sentences').getchildren()

    for i in range(len(sentences)):
        try:
            new_sentence = sentences[i].find('text').text
            opinions = sentences[i].find('Opinions').findall('Opinion')
            sortchildrenby(opinions, 'from')
            bias = 0
            last_start = -1
            last_end = -1
            for opinion in opinions:
                start = int(opinion.get('from'))
                end = int(opinion.get('to'))
                polarity = opinion.get('polarity')
                category = opinion.get('category')
                target = opinion.get('target').lower()
                if (end != 0):
                    if (last_start == start and last_end == end):
                        new_sentence = new_sentence[:bias+len(target)+start+1] + category + '{a-' + polarity + '}' + new_sentence[bias+len(target)+start:]
                        bias = bias + len(category + '{a-' + polarity + '}') + 1
                    else:
                        new_sentence = new_sentence[:bias+start] + category + '{a-' + polarity + '}' + new_sentence[bias+end:]
                        bias = bias + len(category + '{a-' + polarity + '}') - len(target)
                else:
                    new_sentence = new_sentence + ' ' + category + '{a-' + polarity + '}'

                last_start = start
                last_end = end
            test_text.write(re.sub(r'[.,:;?!\n()\\]','', new_sentence).lower() + '\n')

        except AttributeError:
            continue

def load_data(data_dir, flag_word2vec, label_dict, seq_max_len, flag_addition_corpus,
            flag_change_xml_to_txt, negative_weight, positive_weight, neutral_weight):
    train_data = list()
    train_mask = list()
    train_binary_mask = list()
    train_label = list()
    train_seq_len = list()
    test_data = list()
    test_mask = list()
    test_binary_mask = list()
    test_label = list()
    test_seq_len = list()
    count_pos = 0
    count_neg = 0
    count_neu = 0

    if (flag_change_xml_to_txt):
        change_xml_to_txt_v2(data_dir)

    stop_words = load_stop_words()
    aspect_list = export_aspect(data_dir)
    word_dict, word_dict_rev, embedding = load_embedding(data_dir, flag_addition_corpus, flag_word2vec)
    # load data, mask, label


    for file in os.listdir(data_dir + '/ABSA_SemEval2015/'):
        if not file.endswith('.txt'):
            continue

        f_processed = codecs.open(data_dir + '/ABSA_SemEval2015/' + file, 'r', 'utf-8')
        for line in f_processed:
            data_tmp = list()
            mask_tmp = list()
            binary_mask_tmp = list()
            label_tmp = list()
            count_len = 0

            words = line.strip().split(' ')
            for word in words:
                if (word in stop_words):
                    continue
                word_clean = word.replace('{a-positive}', '').replace('{a-negative}', '').replace('{a-neutral}', '')

                if (word_clean in word_dict.keys() and count_len < seq_max_len):
                    if ('a-positive' in word):
                        mask_tmp.append(positive_weight)
                        binary_mask_tmp.append(1.0)
                        label_tmp.append(label_dict['a-positive'])
                        count_pos = count_pos + 1
                    elif ('a-neutral' in word):
                        mask_tmp.append(neutral_weight)
                        binary_mask_tmp.append(1.0)
                        label_tmp.append(label_dict['a-neutral'])
                        count_neu = count_neu + 1
                    elif ('a-negative' in word):
                        mask_tmp.append(negative_weight)
                        binary_mask_tmp.append(1.0)
                        label_tmp.append(label_dict['a-negative'])
                        count_neg = count_neg + 1
                    else:
                        mask_tmp.append(0.)
                        binary_mask_tmp.append(0.)
                        label_tmp.append(0)
                    count_len = count_len + 1

                    data_tmp.append(word_dict[word_clean])


            if file == 'ABSA-15_Restaurants_Train_Final.txt':
                train_seq_len.append(count_len)
            else:
                test_seq_len.append(count_len)

            for _ in range(seq_max_len - count_len):
                data_tmp.append(word_dict['<padding>'])
                mask_tmp.append(0.)
                binary_mask_tmp.append(0.)
                label_tmp.append(0)

            if file == 'ABSA-15_Restaurants_Train_Final.txt':
                train_data.append(data_tmp)
                train_mask.append(mask_tmp)
                train_binary_mask.append(binary_mask_tmp)
                train_label.append(label_tmp)
            else:
                test_data.append(data_tmp)
                test_mask.append(mask_tmp)
                test_binary_mask.append(binary_mask_tmp)
                test_label.append(label_tmp)
        f_processed.close()
    #TODO: get sequence length for each sentence
    print('pos: %d' %count_pos)
    print('neu: %d' %count_neu)
    print('neg: %d' %count_neg)
    print('len of train data is %d' %(len(train_data)))
    print('len of test data is %d' %(len(test_data)))
    data_sample = ''
    for id in train_data[10]:
        data_sample = data_sample + ' ' + word_dict_rev[id]
    print('%s' %data_sample)
    print(train_data[10])
    print(train_mask[10])
    print(train_label[10])
    print('len of word dictionary is %d' %(len(word_dict)))
    print('len of embedding is %d' %(len(embedding)))
    print('len of aspect_list is %d' %(len(aspect_list)))
    print('max sequence length is %d' %(np.max(test_seq_len)))
    return train_data, train_mask, train_binary_mask, train_label, train_seq_len, \
    test_data, test_mask, test_binary_mask, test_label, test_seq_len, \
    word_dict, word_dict_rev, embedding, aspect_list


def main():
    seq_max_len = 64
    negative_weight = 2.5
    positive_weight = 1.0
    neutral_weight = 5.0

    label_dict = {
        'a-positive' : 1,
        'a-neutral' : 0,
        'a-negative': 2
    }

    data_dir = '../data'
    flag_word2vec = False
    flag_addition_corpus = False
    flag_change_xml_to_txt = True

    train_data, train_mask, train_binary_mask, train_label, train_seq_len, \
    test_data, test_mask, test_binary_mask, test_label, test_seq_len, \
    word_dict, word_dict_rev, embedding, aspect_list = load_data(
        data_dir,
        flag_word2vec,
        label_dict,
        seq_max_len,
        flag_addition_corpus,
        flag_change_xml_to_txt,
        negative_weight,
        positive_weight,
        neutral_weight
    )

if __name__ == '__main__':
    main()
