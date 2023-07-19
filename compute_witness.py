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
import shutil

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
    os.chdir(args['--output'])

    if not os.path.exists('keys'):
      os.makedirs('keys')

    
    compile_code('snarkjs.cmd', 'wtns export json', [ 'witness.wtns', 'keys/witness.json'])
    print('Witness generated')


    shutil.copy2('verification_key.json', 'keys')
    shutil.copy2('circuit.sym', 'keys')

    compile_code('snarkjs.cmd', 'plonk prove', ['circuit_final.zkey', 'witness.wtns', 'keys/proof.json', 'keys/public.json'])

    
if __name__ == "__main__":
    main()

