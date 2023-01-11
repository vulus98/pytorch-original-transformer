import os


BASELINE_MODEL_NUMBER_OF_LAYERS = 6
#BASELINE_MODEL_DIMENSION = 512
BASELINE_MODEL_DIMENSION = 128
BASELINE_MODEL_NUMBER_OF_HEADS = 8
BASELINE_MODEL_DROPOUT_PROB = 0.1
BASELINE_MODEL_LABEL_SMOOTHING_VALUE = 0.1


BIG_MODEL_NUMBER_OF_LAYERS = 6
BIG_MODEL_DIMENSION = 1024
BIG_MODEL_NUMBER_OF_HEADS = 16
BIG_MODEL_DROPOUT_PROB = 0.3
BIG_MODEL_LABEL_SMOOTHING_VALUE = 0.1


SCRATCH = os.environ.get('SCRATCH')
CHECKPOINTS_SCRATCH = os.path.join(SCRATCH, 'models', 'checkpoints')
CHECKPOINTS_PATH = os.path.join(os.path.dirname(__file__), os.pardir, 'models', 'checkpoints')
CHECKPOINTS_SCRATCH = os.path.join(SCRATCH, 'models', 'checkpoints')

BINARIES_PATH = os.path.join(os.path.dirname(__file__), os.pardir, 'models', 'binaries')
FF_MODELS_PATH = os.path.join(os.path.dirname(__file__), os.pardir, 'models', 'binaries','ff')
DATA_DIR_PATH = os.path.join(os.path.dirname(__file__), os.pardir, 'data')
LAYER_OUTPUT_PATH = os.path.join(SCRATCH, "layer_outputs")
MHA_OUTPUT_PATH = os.path.join(SCRATCH, "mha_outputs")
MHA_ONLY_CHECKPOINT_FORMAT = "ff_network_{0}_layer_{1}.pth" #.format(epoch, layer)
MHA__CHECKPOINT_FORMAT = "" #TODO: modify this according to your needs (Vule)
os.makedirs(CHECKPOINTS_SCRATCH, exist_ok=True)
ATTENTION_WEIGHTS_OUTPUT_PATH = os.path.join(SCRATCH, "attention_weights_outputs")

os.makedirs(CHECKPOINTS_PATH, exist_ok=True)
os.makedirs(BINARIES_PATH, exist_ok=True)
os.makedirs(DATA_DIR_PATH, exist_ok=True)
os.makedirs(LAYER_OUTPUT_PATH, exist_ok=True)
os.makedirs(MHA_OUTPUT_PATH, exist_ok=True)
os.makedirs(ATTENTION_WEIGHTS_OUTPUT_PATH, exist_ok=True)
os.makedirs(CHECKPOINTS_SCRATCH, exist_ok=True)


BOS_TOKEN = '<s>'
EOS_TOKEN = '</s>'
PAD_TOKEN = "<pad>"
MAX_LEN = 50