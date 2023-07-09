"""
Usage:
  compute_witness.py <input_file>

Options:
  -h, --help         Show this help message.

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
    merge_jsons(input_file, 'output/circuit.json', 'output/input_weights.json')

    print('Merged input with weights')

    os.chdir('./output/circuit_js')

    compile_code('node', 'generate_witness.js', ['circuit.wasm',  '../input_weights.json',  '../witness.wtns'])
    print('Witness generated')
    
if __name__ == "__main__":
    main()

