from keras.layers import Input, Dense, GRU, Dropout, BatchNormalization, \
                         MaxPooling1D, Conv1D, Flatten, Concatenate, PReLU
from keras.models import Model
from keras import metrics
from keras import optimizers
from magpie.config import SAMPLE_LENGTH


def get_nn_model(nn_model, embedding, output_length):
    if nn_model == 'cnn':
        return cnn(embedding_size=embedding, output_length=output_length)
    elif nn_model == 'rnn':
        return rnn(embedding_size=embedding, output_length=output_length)
    else:
        raise ValueError("Unknown NN type: {}".format(nn_model))


def cnn(embedding_size, output_length):
    """ Create and return a keras model of a CNN """

    NB_FILTER = 256
    NGRAM_LENGTHS = [1, 2, 3, 4, 5]

    conv_layers, inputs = [], []

    for ngram_length in NGRAM_LENGTHS:
        current_input = Input(shape=(SAMPLE_LENGTH, embedding_size))
        inputs.append(current_input)

        convolution = Conv1D(
            NB_FILTER,
            ngram_length,
            kernel_initializer='he_uniform',
            activation=None,
        )(current_input)
        activation = PReLU()(convolution)
        pool_size = SAMPLE_LENGTH - ngram_length + 1
        pooling = MaxPooling1D(pool_size=pool_size)(activation)
        conv_layers.append(pooling)

    merged = Concatenate()(conv_layers)
    dropout = Dropout(0.25)(merged)
    flattened = Flatten()(dropout)
    outputs = Dense(output_length, activation='softmax')(flattened)

    model = Model(inputs=inputs, outputs=outputs)
    sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(
        loss='categorical_crossentropy',
        optimizer=sgd,
        metrics=[metrics.categorical_accuracy],
    )

    return model


def rnn(embedding_size, output_length):
    """ Create and return a keras model of a RNN """
    HIDDEN_LAYER_SIZE = 256

    inputs = Input(shape=(SAMPLE_LENGTH, embedding_size))

    gru = GRU(
        HIDDEN_LAYER_SIZE,
        input_shape=(SAMPLE_LENGTH, embedding_size),
        activation='tanh', recurrent_activation='hard_sigmoid', 
        kernel_initializer='glorot_uniform', recurrent_initializer='orthogonal'
    )(inputs)

    batch_normalization = BatchNormalization()(gru)
    dropout = Dropout(0.1)(batch_normalization)
    outputs = Dense(output_length, activation='softmax')(dropout)

    model = Model(inputs=inputs, outputs=outputs)

    model.compile(
        loss='categorical_crossentropy',
        optimizer='adam',
        metrics=[metrics.categorical_accuracy],
    )

    return model
