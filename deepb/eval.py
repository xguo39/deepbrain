import tensorflow as tf
import numpy as np
import os
import time
import datetime
import dataloader
from tensorflow.contrib import learn
import csv
import os.path
BASE = os.path.dirname(os.path.abspath(__file__))
## usage: python eval.py  

# Parameters
# ==================================================

# Data Parameters
tf.flags.DEFINE_string("eval_data_file", os.path.join(BASE, "data/pubmed_query_results.csv"), "Data source for evaluation")
tf.flags.DEFINE_string("delimiter", "\t", "Delimiter in the data file")

# Eval Parameters
tf.flags.DEFINE_integer("batch_size", 64, "Batch Size (default: 64)")
tf.flags.DEFINE_string("checkpoint_file", os.path.join(BASE, "data/1491075157_nsent_5_maxsentlen_180_filters345_rmparentheses/checkpoints/model-3000"), "Model file from training run")
tf.flags.DEFINE_string("vocab_file", os.path.join(BASE, "data/1491075157_nsent_5_maxsentlen_180_filters345_rmparentheses/vocab"), "Vocab file from training run")
tf.flags.DEFINE_boolean("eval_train", False, "Evaluate on all training data")
tf.flags.DEFINE_string("outfile", os.path.join(BASE, "/tmp/prediction_filters345.csv"), "outfile path")

# Misc Parameters
tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")

FLAGS = tf.flags.FLAGS
FLAGS._parse_flags()
# print("\nParameters:")
# for attr, value in sorted(FLAGS.__flags.items()):
    # print("{}={}".format(attr.upper(), value))
# print("")

# CHANGE THIS: Load data. Load your own data here
if FLAGS.eval_train:
    x_raw, y_test = dataloader.load_data_and_labels(FLAGS.eval_data_file, FLAGS.delimiter)
    y_test = np.argmax(y_test, axis=1)
else:
    with open(FLAGS.eval_data_file, 'rb') as f:
        x_raw, y_test, genes, variants, titles, texts, impactfactors, years, journals = [], [], [], [], [], [], [], [], []
        f.readline()
        for line in f.readlines():
            text = line.rstrip()
            parts = text.split('|')
            title, text, gene, variant, protein, impactfactor, year, journal = parts[3], parts[7], parts[0], parts[1], parts[2], parts[6], parts[5], parts[4]
            x_raw.append(dataloader.extractSentencesFromText(title, text, gene, variant, protein))
            y_test.append(1)
            genes.append(gene)
            variants.append(variant)
            titles.append(title)
            texts.append(text)
            impactfactors.append(impactfactor)
            years.append(year)
            journals.append(journal)

# Map data into vocabulary
#vocab_path = os.path.join(FLAGS.checkpoint_dir, "..", "vocab")
vocab_path = FLAGS.vocab_file
vocab_processor = learn.preprocessing.VocabularyProcessor.restore(vocab_path)
x_test = []
for i in xrange(len(x_raw)):
    x_test.append( np.array(list(vocab_processor.transform(x_raw[i]))).flatten().tolist() )
maxlen = max(map(len, x_test))
map(lambda x: x.extend([0] * (maxlen - len(x))), x_test)
x_test = np.array(x_test)
# print("\nEvaluating...\n")

# Evaluation
# ==================================================
#checkpoint_file = tf.train.latest_checkpoint(FLAGS.checkpoint_dir)
checkpoint_file = FLAGS.checkpoint_file
graph = tf.Graph()
with graph.as_default():
    session_conf = tf.ConfigProto(
      allow_soft_placement=FLAGS.allow_soft_placement,
      log_device_placement=FLAGS.log_device_placement)
    sess = tf.Session(config=session_conf)
    with sess.as_default():
        # Load the saved meta graph and restore variables
        saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
        saver.restore(sess, checkpoint_file)

        # Get the placeholders from the graph by name
        input_x = graph.get_operation_by_name("input_x").outputs[0]
        # input_y = graph.get_operation_by_name("input_y").outputs[0]
        dropout_keep_prob = graph.get_operation_by_name("dropout_keep_prob").outputs[0]

        # Tensors we want to evaluate
        predictions = graph.get_operation_by_name(os.path.join(BASE, "output/predictions")).outputs[0]
        prediction_probs = graph.get_operation_by_name(os.path.join(BASE, "output/predict_probs")).outputs[0]
        predict_pathogenicity_probs = graph.get_operation_by_name(os.path.join(BASE, "output/predict_pathogenicity_probs")).outputs[0]
        predict_uncertain_probs = graph.get_operation_by_name(os.path.join(BASE, "output/predict_uncertain_probs")).outputs[0]
        predict_benign_probs = graph.get_operation_by_name(os.path.join(BASE, "output/predict_benign_probs")).outputs[0]

        # Collect the predictions here
        all_predictions, all_prediction_probs, all_predict_pathogenicity_probs, all_predict_uncertain_probs, all_predict_benign_probs = sess.run([predictions, prediction_probs, 
                                                                                   predict_pathogenicity_probs, predict_uncertain_probs, predict_benign_probs], 
                                                                                  {input_x: x_test, 
                                                                                   dropout_keep_prob: 1.0})
        #print all_predictions, all_prediction_probs, all_predict_pathogenicity_probs, all_predict_uncertain_probs, all_predict_benign_probs
 
# Save the evaluation to a csv
predictions_human_readable = np.column_stack((np.array(genes), np.array(variants), all_predictions, all_prediction_probs, all_predict_pathogenicity_probs, all_predict_uncertain_probs, all_predict_benign_probs, np.array(journals), np.array(impactfactors), np.array(years), np.array(titles), np.array(texts)))
out_path = FLAGS.outfile
# print("Saving evaluation to {0}".format(out_path))
with open(out_path, 'w') as f:
    f.write('gene|variant|prediction|prob|pathogenicity_prob|uncertain_prob|benign_prob|journal|impactfactor|year|title|text\n')
    csv.writer(f, delimiter='|').writerows(predictions_human_readable)

