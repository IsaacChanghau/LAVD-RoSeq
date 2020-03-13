import os
from utils.prepro_data_roseq import process_data
from utils.data_utils import RoSeqDataset, boolean_string
from utils.configs_roseq import Configurations
from roseq.robust_seq_labeling import RobustSeqLabelingModel
from argparse import ArgumentParser

# parser
parser = ArgumentParser()
parser.add_argument("--use_gpu", type=boolean_string, default=True, help="if use GPU for training")
parser.add_argument("--gpu_idx", type=str, default="0", help="indicate which GPU is used for training and inference")
parser.add_argument("--log_level", type=str, default="3", help="log level")
parser.add_argument("--random_seed", type=int, default=86, help="random seed")
parser.add_argument("--train", type=boolean_string, default=True, help="if train a model")
parser.add_argument("--at", type=boolean_string, default=False, help="if True, use adversarial training")
parser.add_argument("--language", default="spanish", help="specify the task language")
parser.add_argument("--label_weight", type=boolean_string, default=False, help="use label balanced CRF")
parser.add_argument("--iobes", type=boolean_string, default=True, help="if True, use IOBES scheme, otherwise, IOB2")
parser.add_argument("--dev_for_train", type=boolean_string, default=False, help="use development dataset for training")
parser.add_argument("--use_orthographic", type=boolean_string, default=False, help="use orthographic features")
parser.add_argument("--word_lowercase", type=boolean_string, default=True, help="lowercase words")
parser.add_argument("--char_lowercase", type=boolean_string, default=False, help="lowercase characters")
parser.add_argument("--word_threshold", type=int, default=10, help="word threshold")
parser.add_argument("--ortho_word_threshold", type=int, default=10, help="orthographic word feature threshold")
parser.add_argument("--char_threshold", type=int, default=20, help="character threshold")
parser.add_argument("--word_dim", type=int, default=50, help="word embedding dimension")
parser.add_argument("--word_project", type=boolean_string, default=False, help="word projection")
parser.add_argument("--ortho_word_dim", type=int, default=50, help="orthographic word embedding dimension")
parser.add_argument("--char_dim", type=int, default=30, help="character embedding dimension")
parser.add_argument("--ortho_char_dim", type=int, default=30, help="orthographic character embedding dimension")
parser.add_argument("--tune_emb", type=boolean_string, default=False, help="optimizing word embeddings while training")
parser.add_argument("--highway_layers", type=int, default=2, help="number of highway layers used")
parser.add_argument("--char_kernels", type=int, nargs="+", default=[2, 3, 4], help="CNN kernels for char")
parser.add_argument("--char_kernel_features", type=int, nargs="+", default=[20, 20, 20], help="CNN features for char")
parser.add_argument("--num_units", type=int, default=100, help="number of units for RNN")
parser.add_argument("--concat_rnn", type=boolean_string, default=True, help="if concatenating RNN units")
parser.add_argument("--epsilon", type=float, default=5.0, help="epsilon")
parser.add_argument("--focal_loss", type=boolean_string, default=False, help="use focal loss to handle label imbalance")
parser.add_argument("--lr", type=float, default=0.001, help="learning rate")
parser.add_argument("--use_lr_decay", type=boolean_string, default=True, help="apply learning rate decay at each epoch")
parser.add_argument("--lr_decay", type=float, default=0.05, help="learning rate decay factor")
parser.add_argument("--decay_step", type=int, default=1, help="learning rate decay steps")
parser.add_argument("--minimal_lr", type=float, default=1e-4, help="minimal learning rate")
parser.add_argument("--optimizer", type=str, default="adam", help="optimizer: [rmsprop | adadelta | adam | ...]")
parser.add_argument("--grad_clip", type=float, default=5.0, help="maximal gradient norm")
parser.add_argument("--epochs", type=int, default=50, help="train epochs")
parser.add_argument("--batch_size", type=int, default=16, help="batch size")
parser.add_argument("--emb_drop_rate", type=float, default=0.2, help="dropout rate for embeddings")
parser.add_argument("--rnn_drop_rate", type=float, default=0.5, help="dropout rate for embeddings")
parser.add_argument("--max_to_keep", type=int, default=1, help="maximum trained model to be saved")
parser.add_argument("--no_imprv_tolerance", type=int, default=None, help="no improvement tolerance")
config = Configurations(parser.parse_args())

# os environment
os.environ['TF_CPP_MIN_LOG_LEVEL'] = config.log_level
os.environ["CUDA_VISIBLE_DEVICES"] = config.gpu_idx

# if dataset is not prepared, then build it
if not os.path.exists(config.save_path) or not os.listdir(config.save_path):
    process_data(config)

print("load dataset...")
dataset = RoSeqDataset(config.train_set, config.dev_set, config.test_set, batch_size=config.batch_size, shuffle=True)

print("build model and train...")
model = RobustSeqLabelingModel(config)
if config.train:
    model.train(dataset)
model.restore_last_session()
model.evaluate(dataset.get_data_batches("test"), name="test")
model.close_session()