from tensorflow.keras import datasets
from core.model import MHSADrugVQA, create_model
import numpy as np
import tensorflow as tf
import random
from dataTF import *
from utils import *
import matplotlib.pyplot as plt
#import tensorflow_addons as tfa
from tqdm import tqdm
from sklearn import metrics
import pickle

EPOCHS = 30
train_loss = []
model = create_model()

def train(model):
    
    optimizer = tf.optimizers.Adam(learning_rate = 0.001)
    loss_obj = tf.keras.losses.CategoricalCrossentropy()
    dataset = get_data_loader(trainDataSet, seqContactDict, True)
    print("Load Data Sucessful!")
    for epoch in range(EPOCHS):
        epoch_loss_avg = tf.keras.metrics.Mean()
        print(epoch)
        batch = 0
        for lines, contactMap, proper in tqdm(dataset):
            
            """
            Input to model: 
            String: Smiles --> shape = [1,x]
            Feature 2D: Contactmap --> Shape = [1, size, size, 1]
            """
            #print("Image:")
            

            smiles, length, y = make_variables([lines], proper, smiles_letters)
            smiles = tf.reshape(smiles, [1, smiles.shape[-1]])
            
            with tf.GradientTape() as tape:
                logits = model(smiles, contactMap, training=True) 
                
                loss =loss_obj(y, logits)

            grads = tape.gradient(loss, model.trainable_variables)
        
            optimizer.apply_gradients((grads, var) for (grads, var) in zip(grads, model.trainable_variables))
            
            epoch_loss_avg.update_state(loss)
            if batch % 100 == 0 and batch is not 0:
                print("Loss: {}".format(epoch_loss_avg.result()))
            batch += 1
        metric = {}
        for x in testProteinList:
            pred = []
            actual = []
            #Preparing data for Testing
            print("Current Testing -->", x.split('_')[0])
            data = dataDict[x]
            test_loader = get_data_loader(data, seqContactDict, True)

            #Testing phase
            print("Starting Testing...")
            for lines, contactMap, proper in tqdm(test_loader):
                smiles, length, y = make_variables([lines], proper, smiles_letters)
                smiles = tf.reshape(smiles, [1, smiles.shape[-1]])
                print("Label in test: {}".format(y))
                logits = model(smiles, contactMap, training=False)
                #print("Predict: {} -- Actual: {}".format(np.argmax(logits), np.argmax(y)))
                #print("Predict: {} -- Actual: {}".format((logits), (y)))
                pred.append(np.argmax(logits))
                actual.append(np.argmax(y))
            print("Actual: {}".format(actual))
            print("Predict :{}".format(pred))
            f1_score = metrics.f1_score(actual, pred)
            recall = metrics.recall_score(actual, pred)
            precision = metrics.precision_score(actual, pred)
            acc = metrics.accuracy_score(actual, pred)
            print("F1: {} -- Recall :{} -- Precision: {} -- Accuracy: {}".format(f1_score, recall, precision, acc))
            metric['f1'] = f1_score
            metric['precision'] = precision
            metric['accuracy'] = acc
            metric['recall'] = recall

            print("Saving result...")
            inFile = open("metric_epoch"+str(epoch)+str(x)+".pkl", mode = 'wb')
            pickle.dump(metric, inFile)
            inFile.close()
            print("Saving Success!")

            print("End...")
            print("\n")      
            
train(model)   

                
