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
import subprocess
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

  #compile_code('snarkjs.cmd', 'wtns export json', [ 'hash_computation/witness.wtns', 'hash_computation/witness.json'])

  with open('hash_computation/witness.json', 'r') as file:
    file_content = file.read()

  # Parse the file content as a JSON array
  data = json.loads(file_content)

  # Retrieve the second element
  hash = data[1]
  print('Calculated hash: ' + hash)

  #utils.add_merkle_tree(os.path.join(args['--output'], 'circuit.circom'),  hash)
  print('Merkle tree added to circuit')

  print('Circuit ready to be compiled')

  if not os.path.exists(os.path.join(args['--output'], 'powersoftau')):
    os.makedirs(os.path.join(args['--output'], 'powersoftau'))

  os.chdir(os.path.join(args['--output'], 'powersoftau'))


  utils.compile_code('snarkjs.cmd', 'powersoftau new bn128 16', ['pot14_0000.ptau', '-v'])
  utils.compile_code('snarkjs.cmd', 'powersoftau contribute', ['pot14_0000.ptau', 'pot14_0001.ptau', '--name=\"First contribution\"', '-v', '-e=\"some random text\"'])
  utils.compile_code('snarkjs.cmd', 'powersoftau contribute', ['pot14_0001.ptau', 'pot14_0002.ptau', '-name=\"Second contribution\"',  '-v', '-e=\"some random text\"'])
  utils.compile_code('snarkjs.cmd', 'powersoftau export challenge', ['pot14_0002.ptau', 'challenge_0003'])
  utils.compile_code('snarkjs.cmd', 'powersoftau challenge contribute', ['bn128', 'challenge_0003', 'response_0003', '-e=\"some random text\"' ])
  utils.compile_code('snarkjs.cmd', 'powersoftau import response', ['pot14_0002.ptau', 'response_0003', 'pot14_0003.ptau', '-n=\"Third contribution name\"'] )
  utils.compile_code('snarkjs.cmd', 'powersoftau verify', ['pot14_0003.ptau'])
  
  #change the number of constraints
  utils.compile_code('snarkjs.cmd', 'powersoftau beacon', ['pot14_0003.ptau', 'pot14_beacon.ptau', '0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f', '10', '-n=\"Final Beacon\"' ])
  utils.compile_code('snarkjs.cmd', 'powersoftau prepare phase2', ['pot14_beacon.ptau', 'pot14_final.ptau', '-v'])
  utils.compile_code('snarkjs.cmd', 'powersoftau verify', ['pot14_final.ptau'])

  os.chdir('../')
  os.chdir('../')

  utils.compile_code('circom', os.path.join(args['--output'], 'circuit.circom'), ['--r1cs', '--wasm', '--sym', '-o', 'output','-l', '../'])
  print('Circuit compiled')

  os.chdir(args['--output'])

  utils.compile_code('snarkjs.cmd', 'plonk setup', ['circuit.r1cs', 'powersoftau/pot14_final.ptau', 'circuit_final.zkey'])
  print('Circuit & ZKP setup completed')