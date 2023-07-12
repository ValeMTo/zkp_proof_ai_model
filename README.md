# zkp_proof_ai_model

`zkp_proof_ai_model` is a tool designed to convert ONNX models into Circom circuits using the library `onnx2circom`, that calculates the hash with Poseidon formula and compute witness of the given circuit.
The tool relies on an external repository: 
- `onnx2circom`: to transpile from onnx to circom
- `keras2circom`: requested by `onnx2circom`
- `circomlib`: for the single or double hash `Poseidon`
- `snarkjs`: to compute the proof

## Installation
First, clone the `zkp_proof_ai_model` repository:

```
git clone https://github.com/ValeMTo/zkp_proof_ai_model.git
```

Then, install the dependencies. You can use pip:

```
pip install -r requirements.txt
```

If you use conda, you can also create a new environment with the following command:

```
conda env create -f environment.yml
```

`zkp_proof_ai_model` also requires `onnx2circom`, `keras2circom`,`circomlib`,`snarkjs`: to compute the proof  to function properly.

Here's how you can install:
- `onnx2circom`
    ```
    git clone https://github.com/ValeMTo/onnx2circom.git
    ```

- `keras2circom`
    ```
    git clone https://github.com/socathie/keras2circom.git
    ```

- `circomlib`
    ```
    git clone https://github.com/iden3/circomlib.git
    ```

- `snarkjs`
    ```
    git clone https://github.com/iden3/snarkjs.git
    ```

You may need to install additional dependencies due to external libraries. Refer to their own README file for specific installation instructions.

## Usage
### Circuit setup
After installing `zkp_proof_ai_model`, its dependencies and the related external libraries, you can convert your ONNX models into Circom circuits and compute hash.

For example, to transpile the model in `model_dense.onnx` into a circom circuit, calculates witness with snarkjs and updates the circuit with the hash and the template for the hash computation

```bash
python conversion.py model_dense.onnx
```

The final circom circuit will be in the `output` directory.

If you want to transpile the model into a circom circuit with `--verbose` output, i.e. command line print of inputs and output of each layer, you can run:

```bash
python conversion.py model_dense.onnx -v
```

Moreover, if you want to transpile the model into a circom circuit with `--raw` output, i.e. no ArgMax at the end, you can run:

```bash
python conversion.py model_dense.onnx --raw
```

### Circuit usage
After created the circuit, you can use it with the inputs. 

```bash
python compute_witness.py input.json
```
export in json the witness with snarkjs:

then, check the result:

```bash
python check_result.py
```