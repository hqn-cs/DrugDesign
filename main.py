from tensorflow.keras import datasets
from core.model import MHSADrugVQA, create_model
import numpy as np
import tensorflow as tf
import random
from dataTF import *
from utils import *
import matplotlib.pyplot as plt

from tqdm import tqdm
from sklearn import metrics
import pickle
from test import *
#Newest version updated on 10/1/21

EPOCHS = 30
train_loss = []
model = create_model()


def train(model):
    
    optimizer = tf.optimizers.Adam(learning_rate = 0.001)
    loss_obj = tf.keras.losses.CategoricalCrossentropy()
    dataset = get_data_train(trainDataSet, seqContactDict)
    
    metric = {}
    for epoch in range(1,EPOCHS+1):
        predict_list, actual_list = [], []
        epoch_loss_avg = tf.keras.metrics.Mean()
        print("Epochs {}".format(epoch))
        
        for lines, contactMap, proper in tqdm(dataset):
            """
            Input to model: 
            String: Smiles --> shape = [1,x]
            Feature 2D: Contactmap --> Shape = [1, size, size, 1]
            """
            smiles, length, y = make_variables([lines], proper, smiles_letters)
            smiles = tf.reshape(smiles, [1, smiles.shape[-1]])
            
            with tf.GradientTape() as tape:
                logits = model(smiles, contactMap, training=True) 
                loss =loss_obj(y, logits)

            grads = tape.gradient(loss, model.trainable_variables)
        
            optimizer.apply_gradients((grads, var) for (grads, var) in zip(grads, model.trainable_variables))
            
            epoch_loss_avg.update_state(loss)
        print("Loss after {} epochs : {}".format(epoch, epoch_loss_avg.result()))
        testModel(model, epoch)
        """
            predict_list.append(np.argmax(logits))
            actual_list.append(np.argmax(y))
            #model.save("model_batch"+str(epoch))
            #saveModel = open("mymodel.pkl", mode = 'wb')
            #pickle.dump(model, saveModel)
            #saveModel.close()
            #break
            print("Testing....")
            
            print("Predict: {} -- Actual: {} =========== Loss: {}".format(np.argmax(logits),np.argmax(y),epoch_loss_avg.result()))
            
            metric['f1'] = metrics.f1_score(actual_list, predict_list)
            metric['prec'] = metrics.precision_score(actual_list, predict_list)
            metric['recall'] = metrics.recall_score(actual_list, predict_list)
            metric['accuracy'] = metrics.accuracy_score(actual_list, predict_list)
            print("Save metric")
            inFile = open("metric_batch"+str(batch)+".pkl", mode= 'wb')
            pickle.dump(metric, inFile)
            inFile.close()
            print("Save done")
        #    train_loss.append(epoch_loss_avg.result())
        """
        
            
train(model)   

                