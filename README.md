# Confusion Pair Correction
A confusion pair is defined as a set of words where there is common confusion about which word to use correctly in a sentence. <br>
&nbsp;&nbsp;&nbsp;For example : <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Incorrect input sentence    : Take the spoon **end** the fork.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Correct output sentence     : Take the spoon **and** the fork.<br>
Here **end** and **and** is a confusion pair. <br><br>
The aim of this GSoC project is to leverage the use of sequence-to-sequence models to detect the word(s) that are used incorrectly by taking the entire sentence as context to detect the confusion pairs present. <br>

The sequence-to-sequence model that takes as input an incorrect sentence and marks all the places where an error is detected. The ith place is marked with 0 if there is no error present or 1 if the ith word has an error. <br>
Example <br>
Input &nbsp; &nbsp;: “Take **you’re** spoon and keep it on the **widow** pane” <br>
Output &nbsp;:    0         1          0        0       0    0   0    0     1        0 <br>

The sequence-to-sequence model uses a bi-directional LSTM for the encoder to create the repeat vector which is used by a LSTM which is the decoder. <br>

Dataset Creation
------
> 1) The file _language_/text_files/correct_sentences.txt contains all the correct sentences that the model uses for training. This file is used for creating the dataset for the model to train on. Incorrect sentences are generated by taking all permutaions of error words occuring in the sentence and its corresponding targets are generated. 
> 2) For example : If the correct sentences is **This is your way of doing things**. The following data and targets are generated.
> > This is your way of doing things : 0 0 0 0 0 0 0 <br>
> > This is you’re way of doing things : 0 0 1 0 0 0 0 <br>
> > This is your way of doing thinks : 0 0 0 0 0 0 1<br>
> > This is you’re way of doing thinks : 0 0 1 0 0 0 1<br>
> 3) All data genterated are stroed in _language_/text_files/data.txt
> 4) All targets generated are stored in _language_/text_files/targets.txt
> 5) run `python3 code/make_dataset.py` to generate the data and targets.

Pre-processing
------
> 1) VOCAB SIZE = 30000
> 2) MAX SEQUENCE LENGTH = 20
> 3) The targets are padded with 2 (as the start of sequence tag) and 3 (as the end of sequence tag).
> 4) The padded incorrect sentences are vectorized and is stored as  _language_/pickle_files/padded_input.pkl. This is the input to the encoder.
> 5) The padded output targets are vectorized and is stored as  _language_/pickle_files/decoder_input_data.pkl. This is the input to the decoder.
> 6) The decoder output data is the same as the padded output targets but offset by one time step. It is stored as _language_/pickle_files/decoder_output_data.pkl
> 7) run `python3 code/preprocessing.py` to generate padded_input.pkl, decoder_input_data.pkl and decoder_ouput_data.pkl.

Instructions For Training
------

> 1) Choose the language to train on. There should be a directory with the same name as the language to train in the main directory. 
> 2) If the dataset is skewed (more correct samples than incorrect samples) Change the `is_skew` variable to `True` in code/make_dataset.py
> 3) If you are using pretrained word embedding, specify the correct path in code/train.py
> 4) Specify the number of GPUs and CPUs to be used in code/train.py
> 5) Put the LT confusion pairs for a language in _language_/text_files/LT_cps.txt. This file should be of the format described [here](https://github.com/languagetool-org/languagetool/blob/master/languagetool-language-modules/en/src/main/resources/org/languagetool/resource/en/confusion_sets.txt)
> 6) The file _language_/text_files/correct_sentences.txt contains all the correct sentences that the model uses for training.
> 7) run `python3 main_train.py`

Instructions For Evaluation
------
> 1) Choose the language to evaluate.
> 2) Put the dataset to evaluate in _language_/text_files/evaluation_correct_sentences.txt
> 3) run `python3 main_eval.py`. This will create correct + incorrect sentences which is saved in _language_/text_files/eval_data.txt and  _language_/text_files/eval_targets.txt contains the corresponding ground truth.
> 4) open `main_eval.py` and comment out the following lines :
`make_evaluation_data(language+"/text_files/evaluation_correct_sentences.txt",language)` <br>
`exit(0)`
> 5) run `python3 main_eval.py` again.


File Structure
------
> 1) _language_/text_files/selected_cps.txt contains all the confusion pairs supported.
> 2) _language_/text_files/data.txt contains all the correct+incorrect sentences and _language_/text_files/targets.txt contains the corresponding targets used for training.
> 3) _language_/pickle_files contains all the pickle files created.
> 4) _language_/pre_trained_models/ contains the trained model JSON files. The weights files are not added as they exceed the github file size.

Results and Future Work
------
**English** <br>
Datasets used for correct sentences : Tatoeba, British National Corpus, Europarl Corpus. Total 1028860 sentences. <br>
Total incorrect sentences generated for training : 6346161 sentences. <br>
Evalutaion on 300 unseen sentences : <br>
Precision : 0.8451816745655608 <br>
Recall : 0.8143074581430746 <br>

**French** <br>
Datasets used for correct sentences : Tatoeba, French News Crawl Articles 2011,2010,2015, Europarl Corpus. Total 16336780 correct sentences. <br>
Total incorrect sentences generated for training : 18786915 sentences <br>
Evaluation on  2,276,775 unseen sentences from French News crawl 2007 dataset <br>
Precision : 0.692038157768896 <br>
Recall : 0.6897229582976625 <br>

In theory, The current model developed is not optimal for this task because the output space of the decoder is too large. Also, in encoder-decoder models, the ith prediction of the decoder is dependent on the repeat vector (from the encoder) and the i-1th prediction (of the decoder). This works well in Machine translation because the ith word generated is dependent on the word that comes before it. But its not suitable for this task (because the ith 1 is not dependent on the previous 0 or 1).
<br>
The future work involves replacing the decoder with a classifier for each confusion pair. The problem will be then formulated as a classification task rather than a generative one which would require much less data to train. 
