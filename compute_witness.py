"""
Usage:
  compute_witness.py <input_file> [-o <output>]

Options:
  -h, --help         Show this help message.
  -o <output> --output=<output>   Directory in which the circuit is [default: output].


Arguments:
  <input_file>       Path to the input file.
"""
from utils import merge_jsons, compile_code
from docopt import docopt
import os

def main():
    args = docopt(__doc__)
    input_file = args['<input_file>']
    print("Input file:", input_file)
  
    # Merge JSON files
    merge_jsons(input_file, os.path.join(args['--output'], 'circuit.json'), os.path.join(args['--output'], 'input_weights.json'))

    print('Merged input with weights')

    os.chdir(os.path.join(args['--output'], 'circuit_js'))

    compile_code('node', 'generate_witness.js', ['circuit.wasm',  '../input_weights.json',  '../witness.wtns'])
    os.chdir("../")
    os.chdir("../")

    print('Witness generated')
    compile_code('snarkjs', 'wtns export json', [ 'output/witness.wtns', 'output/witness.json'])

    
if __name__ == "__main__":
    main()

