"""

Usage:
  compile_circuit.py [-o <output>]
  compile_circuit.py (-h | --help)

Options:
    -h --help                       Show this screen.
    -o <output> --output=<output>   Directory in which the circuit is [default: output].
"""

import utils
from docopt import docopt
import os 
import json

if __name__ == "__main__":

    args = docopt(__doc__)
    print('Output directory: ' + args['--output'])


    # Open the witness JSON file
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

