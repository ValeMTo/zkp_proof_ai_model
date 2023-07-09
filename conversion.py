"""

Usage:
  main.py <model.onnx> [-o <output>] [-v] [--raw]
  main.py (-h | --help)

Options:
    -h --help                       Show this screen.
    -o <output> --output=<output>   Output directory [default: output].
    -v --verbose                    Verbose output [default: False].
    --raw                           Output raw model outputs instead of the argmax of outputs [default: False].

"""

import utils
from docopt import docopt
from onnx2circom.onnx2circom.model import Model
import os 

if __name__ == "__main__":

    args = docopt(__doc__)
    print('Transpiling model: ' + args['<model.onnx>'])
    print('Output directory: ' + args['--output'])
    print('Verbose: ' + str(args['--verbose']))
    print('Raw: ' + str(args['--raw']))
    print('\n')

    model = Model(args['<model.onnx>'])
    model.create_circuit(args['--output'], args['--verbose'], args['--raw']) 
    print('Model created')

    num_weights = utils.count_json_values(os.path.join(args['--output'], 'circuit.json'))
    print('Number of weights: ' + str(num_weights))

    markle_tree_path = utils.write_markle_tree(num_weights, args['--output'])
    print('Merkle tree created in: ' + markle_tree_path)

    utils.calculate_hash(markle_tree_path,os.path.join(args['--output'], 'circuit.json'))

    #No permission to snarkjs in the docker container
    """
    hash = utils.calculate_hash(markle_tree_path,os.path.join(args['--output'], 'circuit.json'))
    print('Calculated hash: ' + hash)

    utils.add_merkle_tree(os.path.join(args['--output'], 'circuit.circom'),  hash)
    print('Merkle tree added to circuit')

    print('Circuit ready to be compiled')

    utils.compile_circuit(os.path.join(args['--output'], 'circuit.circom'), os.path.join(args['--output'], 'circuit.r1cs'), os.path.join(args['--output'], 'circuit.wasm'))
    print('Circuit compiled')
    """


