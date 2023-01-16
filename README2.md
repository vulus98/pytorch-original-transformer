## The Original Transformer (PyTorch) :computer: = :rainbow:
This repo contains the code developed for the Deep Learning project 2022. In this project we tried to replace the self-attention with feed-forward networks (FFN) to evaluate the importance of attention inside the transformer.

The developed code builds on top of an open-source implementation  of the original transformer (:link: [Vaswani et al.](https://arxiv.org/abs/1706.03762)) taken from an open-source implementation by Aleksa Godric who works for Deep Mind(:link: [ pytorch-original-transformer](https://github.com/gordicaleksa/pytorch-original-transformer)). <br/>

## Table of Contents
  * [Environment setup](#Environment-setup)
  * [Code overview](#code-overview)
  * [Train baseline transformer](#Train-baseline-transformer)
  * [Intermediate data extraction](#Intermediate-data-extraction)
  * [Full sentence approach](#Full-sentence-approach)
  * [Average approach](#usage)
  * [Random feature appraoch](#hardware-requirements)

## Environment setup

1. Navigate into the project directory `cd path_to_repo`
2. Run `conda env create` from project directory (this will create a brand new conda environment).
3. Run `activate pytorch-transformer` (for running scripts from your console or set the interpreter in your IDE)
4. Run `export SCRATCH=path_to_outputs`, where `path_to_outputs` is the directory where you want the output files to be stored. If you are running this code on the euler cluster, the variable is already defined.
5. Execute `./scripts/download_iwslt.sh` to download the IWSLT dataset which will be used in this project.

In the following, all the commands are assumed to be run from the root of the repository.

## Code overview
As previously mentioned, the code was developed on top of an existing implementation of the transformer. Our main contribution to this code resides in
- the folder `scripts` which contains scripts for extracting intermediate data, training different architectures and evaluating them in the transformer.
- The file `simulator.py` which contains the classes and functions for substituting FFN in the transformer (for the average approach) with three different layers of abstraction: the entire encoder, the MHA and the residual connection and the MHA only.
- The file `full_sentence_utils` which contains the classes and functions for substituting FFN in the transformer (for the full_sentence approach).

The provided code was run on a single GPU with 20G of memory. In case your GPU does not have this much memory you should try to reduce the batch size and in general bigger architecture may not work properly. The description on how to run the code is general for any platform, however in the submission_scripts folder we left the scripts we used for running our jobs on the Euler cluster.

## Train baseline transformer
The weights of a pretrained transformer are saved in the directory `./models/binaries/transformer_128.pth`. The following parts of the project will use this transformer to extract intermediate values which will be used to train the FFNs to replace attention blocks. If you want to train this transformer yourself

1. Execute ./scripts/baseline/training_script.py
2. Copy the checkpoint after 20 epochs executing `cp models/checkpoint/transformer_ckpt_epoch_20.pth models/binaries/transformer_128.pth`

## Intermediate data extraction

To train our FFNs we first extract the intermediate values that are given as input and output to the attention module. To extract the intermediate data run
1. `python3 scripts/extraction/extract.py --path_to_weights models/binaries/transformer_128.pth --batch_size 1400 --dataset_name IWSLT --language_direction E2G --model_name 128emb_20ep`
2. `python scripts/extraction/extract_mha.py --batch_size 1400 --dataset_name IWSLT --language_direction E2G --model_name 128emb_20ep --path_to_weights models/binaries/transformer_128.pth  --output_path $SCRATCH/mha_outputs`

The first script extracts inputs and outputs of
- each encoder layer (identified by *whole_layer* in the file name),
- each multi-headed attention (MHA) module (identified by *just_attention* in the file name),
- each "sublayer zero" which consists of the MHA, the layer normalization and the residual connection (identified by *with_residual* in the file name).

The second script extracts inputs and outputs of 
- each MHA excluded the linear layer which mixes the values extracted by each head. This is to enable learning the output of each head separately as in the 'separate head' approach.

At the end of this section, your SCRATCH folder should contain one folder *output_layers* containing the output of the first script and one folder *mha_outputs* with the outputs of the second script. These values are used to train FFNs which replace attention with different layers of abstraction.

## Full sentence approach

In this approach, the FFN takes in the concatenated word representations of a sentence as input and produces updated word representations as output in a single pass. In order to handle input sentences of varying lengths, we have decided to pad all sentences to a maximum fixed length and mask the padded values with zeros to prevent them from influencing the model's inference. 

We tried substituting attention with three layer of abstraction: 
- *mha_full*: replaces the MHA and the residual connection
- *mha_only*: replaces only the MHA
- *separate_heads*: replaces the same part as *mha_only*, but one FFN is trained for each head.

The architecture used for each approach are listed in 
- `models/definitions/full_FF.py`
- `models/definitions/mha_only_FF.py`
- `models/definitions/mha_FF.py`.

Each approach uses a different training script. Each training script contains a data loader responsible for loading the data extracted at the previous step and creating batches of a fixed length *MAX_LEN* (using padding). Each training script receives as input the name of the substitute class (e.g. FFNetwork_shrink) and the index of the layer to emulate. The training loop iterates over the training data for a specified maximum number of epochs.
The instruction for running the training scripts are listed below. 

### Training mha_full
To train one of the architectures defined in `models/definitions/full_FF.py` for a specific layer run:
`python3 scripts/full_sentence/training_full_FF.py --num_of_curr_trained_layer [0-5] --substitute_class <function name>`.
For example to train the network *FFNetwork_shrink* to substitute layer zero run
`python3 ./scripts/training_full_FF.py --num_of_curr_trained_layer 0 --substitute_class FFNetwork_shrink`.

### Training separate_heads
To train one of the architectures defined in `models/definitions/mha_FF.py` for a specific layer run:
`python3 scripts/full_sentence/training_mha_only_FF.py --num_of_curr_trained_layer [0-5] --substitute_class <function name>`.
For example to train the network *FFNetwork_shrink* to substitute layer zero with 8 heads, one for each head in the MHA of layer zero, run:
`python3 scripts/full_sentence/training_mh_separate_heads.py --num_of_curr_trained_layer 0 --substitute_class FFNetwork_shrink`.

### Training mha_only
To train one of the architectures defined in `models/definitions/mha_only_FF.py` for a specific layer run:
`python3 .scripts/full_sentence/training_mha_only_FF.py --num_of_curr_trained_layer [0-5] --substitute_class <function name>`.
For example to train the network *FFNetwork_shrink* to substitute layer zero with 8 heads, one for each head in the MHA of layer zero, run:
`.scripts/full_sentence/training_mha_only_FF.py --num_of_curr_trained_layer 0 --substitute_class FFNetwork_shrink`.
This approach was also used to train self-attention in the decoder. The architecture used in the decoder are denoted by the word *decoder* in the class name. To train one of this architecture to substitute self-attention in the encoder layer run
`python3 .scripts/full_sentence/training_mha_only_FF.py --num_of_curr_trained_layer [0-5] --substitute_class FFNetwork_decoder_shrink --decoder`

In case you are running this code on a cluster which uses slurm, the script `submission_scripts/training_mha_only_FF_submit_all.sh` can be used to automatically submit the training of a network for each layer (0-5). If you use that script, please make sure that the path specified for the output of the program exists. The script currently assumes a directory `../sbatch_log` which will collect all the outputs.

### Evaluation

All the networks trained in the previous step can be evaluated using `scripts/full_sentence/validation_script.py`. The validation is performed substituting the trained FFN in the pretrained transformer and computing the BLUE score on the validation data. The script receives as inputs the following parameters: 
- substitute_type: type of approach to use for substitution. Must be in ["mha_full", "mha_only", "mha_separate_heads", "none"]. If 'none', no substitution takes place;
- substitute_class: class that substitutes attention e.g. *FFNetwork_shrink*;
- layers: list of layers to substitute. If layer is not specified, all layers are substituted;
- epoch: epoch checkpoint to use;
- untrained: bool. If set, the substitute FF is not loaded with the trained weights and it is left untrained. This can be set to test the performance of a randomly substituted FFN.

The last four attributes appended with '_d' can be used to substitute self-attention in the decoder. Currently, only the mha_only supports substitution in the decoder layer.
To run the evaluation script the following command can be used
`python3 scripts/full_sentence/validation_script.py --substitute_type <subs_type> --substitute_class <class_name> --layers [0-5]* --epoch <epoch number>`
As an example if you want to evaluate the performance of *FFNetwork_shrink* in the mha_only approach, substituting all layers in the encoder with the checkpoint at epoch 21 the following command can be used:
`python3 scripts/full_sentence/validation_script.py --substitute_type mha_only --substitute_class FFNetwork_shrink --epoch 21`

## Average approach

In this approach, the FFN takes in the concatenation of a word representation and the average of the representation of all the other words in the sentence and produces the updated word representations as output. The same is repeated for all words in each sentence. The idea behind this approach is to understand if the average of the work representation is enough information to learn the next representation. Moreover, the advantage of this approach is that it is not dependent on the sentence length.

Similarly to the full_sentence approach, the average approach tries to replace the attention with three level of abstraction:
- The entire encoder layer (referenced as "whole").
- The MHA only referenced as (referenced as "just_attention").
- The MHA with the residual connection (referenced as "with_residual").

## Architectures exploration

The optuna package was used to perform a randomized grid search to find a good architecture that could substitute the attention blocks for all three approaches (just_attention, with_residual, whole). The best performing architectures are used in the following steps to train FFN that simulate the substitute blocks. To run the randomized grid search run 
`python3 scripts/averaging/find_single_layer_arch.py  --[whole|just_attention|with_residual] --input <index-input> --output <index-output>`. In the command index-input and index-output are the indexes identifying the input and output layer considered for the search. In practice, we set index-input = index-output = 0 and use for all layers the architecture that performed best in layer 0. We found in our experiments that the first layer is the hardest to learn and this approach works well in practice.

## Training

The script `sim_all_pretrain.py` handles training of all the layers for the three different approaches. The training can be run with the following command
`python3 ./scripts/averaging/sim_all_pretrain.py --[whole|just_attention|with_residual]`. 

TODO: add single_sim
## Evaluation

The script `evaluate.py` can be used to compute the BLEU score for the pretrained networks with the different approaches. To run the script use the command
`python3 ./scripts/averaging/evaluate.py --[whole|just_attention|with_residual|single_sim|vanilla]`

On top of the normal approaches, this script can be used to evaluate the transformer without any substitutions (vanilla) and with a single FFN replacing the entire encoder part (single_sim).

