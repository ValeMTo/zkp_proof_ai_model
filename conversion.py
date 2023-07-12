"""

Usage:
  conversion.py <model.onnx> [-o <output>] [-v] [--raw]
  conversion.py (-h | --help)

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
from utils import compile_code
import json
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
  
  compile_code('snarkjs', 'wtns export json', [ 'hash_computation/witness.wtns', 'hash_computation/witness.json'])

  with open('hash_computation/witness.json', 'r') as file:
    file_content = file.read()

  # Parse the file content as a JSON array
  data = json.loads(file_content)

  # Retrieve the second element
  hash = data[1]
  print('Calculated hash: ' + hash)

  utils.add_merkle_tree(os.path.join(args['--output'], 'circuit.circom'),  hash)
  print('Merkle tree added to circuit')

  print('Circuit ready to be compiled')

  utils.compile_code('circom', os.path.join(args['--output'], 'circuit.circom'), ['--r1cs', '--wasm', '--sym', '-o', 'output','-l', '../'])
  print('Circuit compiled')



