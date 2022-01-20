from random import randint
import tensorflow as tf

class FC(tf.keras.layers.Layer):
    def __init__(self, dense_layers, dropout, activation = 'gelu'):
        super(FC,self).__init__()
        
        layers = []
        for num_of_units in dense_layers:
            layers.extend(
                [tf.keras.layers.Dense(units = num_of_units, activation = activation),
                tf.keras.layers.Dropout(dropout)]
            )
        
        self.FC = tf.keras.Sequential(layers)
    
    def call(self, inputs, *args, **kwargs):
        output = self.FC(inputs, *args, **kwargs)
        return output

class MHSABlock(tf.keras.layers.Layer):
    def __init__(self, num_heads, Dim, hidden_layers, dropout, norm_coff = 1e-12):
        super(MHSABlock, self).__init__()
        
        self.attention = tf.keras.layers.MultiHeadAttention(
            num_heads = num_heads, key_dim = Dim, dropout = dropout, name = "multihead_attention"
        )
        self.FC = FC(hidden_layers, dropout)
        self.layerNormAtt = tf.keras.layers.LayerNormalization(epsilon = norm_coff, name = "layer_norm_att")
        self.layerNormFC = tf.keras.layers.LayerNormalization(epsilon = norm_coff, name = "layer_norm_fc")
        
        self.wkey = tf.keras.layers.Dense(units = Dim, activation = 'tanh', name = "wkey")
        self.wquery = tf.keras.layers.Dense(units = Dim, activation = 'tanh', name = "wquery")
        self.wvalue = tf.keras.layers.Dense(units = Dim, activation = 'tanh', name = "wvalue")
        
    def call(self, inputs):
        
        norm_attention = self.layerNormAtt(inputs) #Pass by layer norm 

        key, query, value = self.wkey(norm_attention), self.wquery(norm_attention), self.wvalue(norm_attention)
        
        attention = self.attention(query = query, value = value, key = key) # Pass by Multihead attention
        
        attention += inputs #Skip connection
        
        output = self.layerNormFC(attention) # Pass by layer norm 
        
        output = self.FC(output) # Pass by fully connected 
    
        output += attention
        return output
        #return attention

class Encoder(tf.keras.layers.Layer):
    def __init__(self, num_layers_encoder, num_heads, Dim, hidden_dim, dropout, norm_coff = 1e-12):
        super(Encoder, self).__init__()
        self.encoder = tf.keras.Sequential(
            [
                MHSABlock(
                    num_heads = num_heads,
                    Dim = Dim, 
                    hidden_layers=[hidden_dim, Dim],
                    dropout = dropout,
                    norm_coff=norm_coff
                )
                for _ in range(num_layers_encoder)       
            ]
        )
    def call(self, inputs, *args, **kwargs):
        output = self.encoder(inputs)
        return output
