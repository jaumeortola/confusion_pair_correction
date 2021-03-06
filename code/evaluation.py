# -*- coding: utf-8 -*-
import numpy as np    
import pickle
import keras
import time
import tensorflow as tf
import gensim
from keras.preprocessing import sequence
from keras.models import Model, load_model
from keras.layers import Input, LSTM, Dense, Embedding, Bidirectional, Concatenate
from keras.models import model_from_json
from nltk.tokenize import word_tokenize
from ast import literal_eval

def load_evaluation_data(language):
    input_sentences = []
    input_indices = []
    input_targets = []
    with open(language+"/text_files/eval_data.txt") as f :
        for line in f.readlines() :
            sent = line.split("</>")[0]
            tokenized_line = sent.split()
            input_sentences.append(tokenized_line)
            ind = literal_eval(line.split("</>")[1].strip())
            input_indices.append(ind)

    with open(language+"/text_files/eval_targets.txt") as f :
        for line in f.readlines() :
            temp = []
            for num in line.split() :
                temp.append(int(num))
            input_targets.append(temp)

    return input_sentences,input_indices,input_targets

def make_evaluation_data(filename,language):
    with open(language+"/pickle_files/confusion_dict.pkl",'rb') as f:
        confusion_dict = pickle.load(f)

    confusion_words = confusion_dict.keys()

    data = []
    targets = []
    indices = []
    count = 0

    with open(language+"/text_files/eval_data.txt",'w') as f1 :
        with open(language+"/text_files/eval_targets.txt",'w') as f2 :
            with open(filename) as f:
                for line in f.readlines():
                    if count%10000 == 0 :
                        print("Sentences done : ",count+1)
                    count += 1
                    tokenized_line = word_tokenize(line,language = language.lower())
                    if len(tokenized_line) <= 20 :
                        aug_sentences = [" ".join(tokenized_line)]
                        aug_targets = [" ".join(['0' for i in range(len(tokenized_line))])]
                        aug_indices = []
                        for i,word in enumerate(tokenized_line) :
                            if word in confusion_words :
                                aug_indices.append(i)
                                temp_sentences = aug_sentences[:]
                                for alt_word in confusion_dict[word] :
                                    if alt_word != word :
                                        for j,sent in enumerate(temp_sentences) :
                                            new_sent = sent.split()
                                            new_sent[i] = alt_word
                                            new_sent = " ".join(new_sent)
                                            aug_sentences.append(new_sent)
                                            new_target = aug_targets[j].split()
                                            new_target[i] = '1'
                                            new_target = " ".join(new_target)
                                            aug_targets.append(new_target)
                        

                        data = data + aug_sentences
                        targets = targets + aug_targets
                        for j in range(len(aug_sentences)):
                            indices.append(aug_indices)

                    if len(data) > 10000 :
                        for i,datapoint in enumerate(data) :
                            f1.write(datapoint+ " </> "+str(indices[i]) + "\n")
                        data = []
                        indices = []

                    if len(targets) > 10000 :
                        for data_point in targets :
                            f2.write(data_point + "\n")
                        targets = []

            if len(data) > 0 :
                for i,datapoint in enumerate(data) :
                    f1.write(datapoint+ " </> "+str(indices[i]) + "\n")
                data = []
                indices = []

            if len(targets) > 0 :
                for data_point in targets :
                    f2.write(data_point + "\n")
                targets = []

   
def process(sentence,decoded_sentence) :
    ans = ""
    for i,word in enumerate(sentence) :
        if decoded_sentence[i] == '0' :
            ans = ans + word + " "
        elif decoded_sentence[i] == '1' :
            if sentence[i].lower() in confusion_dict.keys() :
                ans = ans + confusion_dict[word.lower()][0] + " "
            else :
                print("failed :( ")
                ans = ans + sentence[i] + " "
    return ans


def inference(input_seq,encoder_model,decoder_model,len_output_vocab,MAX_DECODER_SEQUENCE_LENGTH):
    states_value = encoder_model.predict(input_seq)
    target_seq = np.zeros((1, 1, len_output_vocab))
    target_seq[0, 0, 2] = 1.
    flag = False
    decoded_sentence = ''
    while not flag:
        output_tokens, h, c = decoder_model.predict(
            [target_seq] + states_value)

        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_char = sampled_token_index
        decoded_sentence += str(sampled_char)

        if (sampled_char == '3' or len(decoded_sentence) > MAX_DECODER_SEQUENCE_LENGTH):
            flag = True

        target_seq = np.zeros((1, 1, len_output_vocab))
        target_seq[0, 0, sampled_token_index] = 1.

        states_value = [h, c]

    return decoded_sentence



#-------------------- Evaluation-----------------------------------------------------

# def evaluate(language):
 
#     with open(language+'/pre_trained_models/model.json', 'r') as f:
#         model = model_from_json(f.read())
#     model.load_weights(language+"/pre_trained_models/model_weight.hdf5")
#     encoder_model = load_model(language+"/pre_trained_models/encoder_model.h5")
#     decoder_model = load_model(language+"/pre_trained_models/decoder_model.h5")
#     # language_model = gensim.models.Word2Vec.load(language+"/pre_trained_models/language_model")
#     print("[INFO] -> Trained models loaded")

#     with open(language+"/pickle_files/word_to_index.pkl",'rb') as f:
#         word_to_index = pickle.load(f)

#     with open(language+"/pickle_files/confusion_dict.pkl",'rb') as f:
#         confusion_dict = pickle.load(f)

    
#     confusion_words = confusion_dict.keys()
#     len_input_vocab = len(word_to_index.keys())
#     len_output_vocab = 4
#     MAX_ENCODER_SEQUENCE_LENGTH = 20
#     MAX_DECODER_SEQUENCE_LENGTH = 20

#     print("[INFO] -> Starting Evaluations")  
#     input_test_sentences = []
#     input_test_sentences,input_indices,input_targets = load_evaluation_data(language)

#     input_test = input_test_sentences[:]
#     for i, sent in enumerate(input_test_sentences):
#         input_test[i] = [w if w in word_to_index.keys() else "UNK" for w in sent]
#     X = np.asarray([[word_to_index[w] for w in sent] for sent in input_test])
#     padded_input_test = sequence.pad_sequences(X, maxlen=MAX_ENCODER_SEQUENCE_LENGTH)



#-------------------- Evaluation-----------------------------------------------------

def evaluate(language):
 
    with open(language+'/pre_trained_models/model.json', 'r') as f:
        model = model_from_json(f.read())
    model.load_weights(language+"/pre_trained_models/model_weight.hdf5")
    encoder_model = load_model(language+"/pre_trained_models/encoder_model.h5")
    decoder_model = load_model(language+"/pre_trained_models/decoder_model.h5")
    # language_model = gensim.models.Word2Vec.load(language+"/pre_trained_models/language_model")
    print("[INFO] -> Trained models loaded")

    with open(language+"/pickle_files/word_to_index.pkl",'rb') as f:
        word_to_index = pickle.load(f)

    with open(language+"/pickle_files/confusion_dict.pkl",'rb') as f:
        confusion_dict = pickle.load(f)

    
    confusion_words = confusion_dict.keys()
    len_input_vocab = len(word_to_index.keys())
    len_output_vocab = 4
    MAX_ENCODER_SEQUENCE_LENGTH = 20
    MAX_DECODER_SEQUENCE_LENGTH = 20

      
    input_test_sentences = []
    input_test_sentences,input_indices,input_targets = load_evaluation_data(language)

    input_test = input_test_sentences[:]
    for i, sent in enumerate(input_test_sentences):
        input_test[i] = [w if w in word_to_index.keys() else "UNK" for w in sent]
    X = np.asarray([[word_to_index[w] for w in sent] for sent in input_test])
    padded_input_test = sequence.pad_sequences(X, maxlen=MAX_ENCODER_SEQUENCE_LENGTH)

    print("[INFO] -> Starting Evaluations")
    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    time_taken = 0
    for seq_index in range(len(input_test)):
        input_seq = padded_input_test[seq_index: seq_index + 1]

        start_time = time.time()
        decoded_sentence = inference(input_seq,encoder_model,decoder_model,len_output_vocab,MAX_DECODER_SEQUENCE_LENGTH)
        time_taken = time_taken + time.time() - start_time

        print("input : "," ".join(input_test_sentences[seq_index]))
        decoded_sentence = [int(i) for i in list(decoded_sentence)]
        print("prediction   : ",decoded_sentence)
        print("ground truth : ",input_targets[seq_index])
        print("")
        for i,value in enumerate(input_targets[seq_index]) :
            if value == 0 :
                if decoded_sentence[i] == 0 :
                    true_negatives += 1
                elif decoded_sentence[i] == 1 :
                    false_positives += 1
            elif value == 1 :
                if decoded_sentence[i] == 1 :
                    true_positives += 1
                elif decoded_sentence[i] == 0 :
                    false_negatives += 1

    print("true_positives  : ",true_positives)
    print("true_negatives  : ",true_negatives)
    print("false_positives : ",false_positives)
    print("false_negatives : ",false_negatives)
    precision = true_positives/(true_positives + false_positives)
    recall = true_positives/(true_positives + false_negatives)
    print("Precision : ",precision)
    print("Recall : ",recall)
    print("Avg Time taken per sentences : ", time_taken/len(input_test))





