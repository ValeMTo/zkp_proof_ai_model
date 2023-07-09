import json
import os
import re
from math import ceil
import string
import subprocess

def merge_jsons(json1, json2, output_path):
    if not os.path.exists(json1):
        print(f"File {json1} does not exist.")

    if not os.path.exists(json2):
        print(f"File {json2} does not exist.")

    with open(json1, 'r') as file1:
        try:
            data1 = json.load(file1)
        except json.JSONDecodeError:
            print(f"Could not decode JSON from {json1}")
    with open(json2, 'r') as file2:
        try:
            data2 = json.load(file2)
        except json.JSONDecodeError:
            print(f"Could not decode JSON from {json2}")

    # Merge the two JSON data
    merged_data = {**data1, **data2}

    # Convert the merged data back into JSON format
    merged_json = json.dumps(merged_data)

    with open(output_path, 'w') as file:
        file.write(merged_json)

def count_json_values(file_path):

    with open(file_path, 'r') as file:
        data = json.load(file)

    count = 0
    for key, value in data.items():
        if isinstance(value, list):
            for sub_value in value:
                if isinstance(sub_value, list):
                    count += len(sub_value)
                else:
                    count += 1
        else:
            count += 1
    return count

def add_merkle_tree(file_path, hash_number):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Insert 'include "./"' after the last include statement
    include_lines = [i for i, line in enumerate(lines) if 'include' in line]
    last_include_line = max(include_lines)
    lines.insert(last_include_line + 1, 'include \"./markle_tree.circom\";\n')

    # Insert 'signal' after the last include statement
    signal_lines=[]
    for i, line in enumerate(lines):
        if 'signal' in line:
            signal_lines.append(i)

    # Initialize an empty list to store the dimensions
    dimensions =  {}

    for line in lines:
        # Match lines that define signal inputs
        match = re.match(r'signal input (\w+)\[(.*?)\];', line)
        if match:
            # Extract the name and dimensions
            name = match.group(1)
            dims = list(map(int, match.group(2).split("][") ))

            # Store in the dictionary
            dimensions[name] = dims

    # Insert other lines after the last signal declaration
    last_signal_line = max(signal_lines)
    lines.insert(last_signal_line + 1, 'signal output incorrect_hash[1];\n')
    lines.insert(last_signal_line + 2, '\ncomponent merkleTree = MerkleTree();\n')
    lines.insert(last_signal_line + 3, '\nvar hash = '+ hash_number +';\n')

    alphabet = list(string.ascii_lowercase)
    lines.insert(last_signal_line + 4, 'var z=0;\n')  
    num = 5

    for layer, dims in dimensions.items():
        if 'in' != layer and 'out' != layer:
            array_format = ''
            close_format = ''
            for i, dim in enumerate(dims):
                lines.insert(last_signal_line + num, '\t'*(i) +'for (var '+alphabet[i]+'=0; '+alphabet[i]+'<'+str(dim)+'; '+alphabet[i]+'++) {\n')  
                array_format += '['+alphabet[i]+']'
                close_format += '\t'*(len(dims)-i-1)+'}\n'
                num = num + 1
            
            lines.insert(last_signal_line + num,'\t'*(len(dims)) +  'merkleTree.in[z] <== '+layer+array_format+';\n'+'\t'*(i+1)+'z = z + 1;\n' +close_format)
            num = num + 1
    lines.insert(last_signal_line + num, '\n\nvar difference = hash - merkleTree.hash;\nincorrect_hash[0] <== difference;\n')

    # Write the modified lines to a new file
    with open(file_path, 'w') as file:
        file.writelines(lines)

def flatten_weights(file_path, directory):
    # Open the weights JSON file
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Flattening the values
    flattened_data = []
    for key, values in data.items():
        for value in values:
            if isinstance(value, list):
                flattened_data.extend(value)
            else:
                flattened_data.append(value)

    # Creating the new dictionary
    new_data = {"in": flattened_data}

    # Save the flattened weights to a new JSON file
    with open(os.path.join('../'+directory, 'flattened_weights.json'), 'w') as f:
        json.dump(new_data, f)

    return os.path.join(directory, 'flattened_weights.json')

def write_markle_tree(nInput, output):
    # Open a file in write mode
    file = open(os.path.join(output, "markle_tree.circom"), "w")

    # Write data to the file
    file.write("pragma circom 2.0.0;\n")
    file.write("\n")

    file.write("include \"../circomlib/circuits/poseidon.circom\";\n")
    file.write("\n")

    file.write("template MerkleTree() {\n")
    file.write("    signal input in[" + str(nInput) + "];\n")
    file.write("    signal output hash;\n")
    file.write("\n")

    levels = []
    tmp = nInput
    while tmp > 1:
        levels.append(tmp)
        tmp = ceil(tmp/2)
    print(levels)

    file.write("    component treeHashes_" + str(0) + "["+str(levels[0])+"];\n")
    file.write("    for (var i = 0; i < " + str(levels[0]) + "; i++) {\n")
    file.write("        treeHashes_" + str(0) + "[i] = Poseidon(1);\n")
    file.write("    }\n")

    for i in range(1, len(levels)):
        file.write("    component treeHashes_" + str(i) + "["+str(levels[i])+"];\n")
        file.write("    for (var i = 0; i < " + str(levels[i]) + "; i++) {\n")
        file.write("        treeHashes_" + str(i) + "[i] = Poseidon(2);\n")
        file.write("    }\n")
    file.write("    component treeHashes_" + str(len(levels)) + " = Poseidon(2);\n")

    file.write("\n")


    file.write("    for (var i = 0; i < " + str(nInput) + "; i++) {\n")
    file.write("        treeHashes_0[i].inputs[0] <== in[i];\n")
    file.write("    }\n")
    file.write("\n")


    for i in range(1, len(levels)):
        if levels[i-1]%2 == 0 :
            levels_len = levels[i]
        else:
            levels_len = levels[i]-1

        file.write("    for (var i = 0; i < " + str(levels_len) + "; i++) {\n")
        file.write("        treeHashes_" + str(i) + "[i].inputs[0] <== treeHashes_"+str(i-1)+"[2*i].out;\n")
        file.write("        treeHashes_" + str(i) + "[i].inputs[1] <== treeHashes_"+str(i-1)+"[2*i+1].out;\n")
        file.write("    }\n")

        if levels[i-1]%2 == 1 :
            file.write("    treeHashes_" + str(i) + "["+str(levels_len)+"].inputs[0] <== treeHashes_"+str(i-1)+"["+str(levels_len*2)+"].out;\n")
            file.write("    treeHashes_" + str(i) + "["+str(levels_len)+"].inputs[1] <== treeHashes_"+str(i-1)+"["+str(levels_len*2)+"].out;\n")
            levels[i-1] = levels[i-1] + 1
        file.write("\n")

    print(levels)

    file.write("    treeHashes_" + str(len(levels)) + ".inputs[0] <== treeHashes_"+str(len(levels)-1)+"[0].out;\n")
    file.write("    treeHashes_" + str(len(levels)) + ".inputs[1] <== treeHashes_"+str(len(levels)-1)+"[1].out;\n")
    file.write("\n")

    file.write("    hash <== treeHashes_"+ str(len(levels)) +".out;\n")
    file.write("}\n")

    # Close the file
    file.close()

    return os.path.join(output, "markle_tree.circom")

def calculate_hash(merkle_tree_path, weights_path):
    # Open the merkle tree JSON file
    with open(merkle_tree_path, 'r') as file:
        lines = file.readlines()

    directory = 'hash_computation'
    if not os.path.exists(directory):
        os.makedirs(directory)
        print("Directory created:", directory)
    else:
        print("Directory already exists:", directory)

    os.chdir(directory)

    with open('hash_computation.circom', 'w') as new_file:
        new_file.writelines(lines)
        new_file.write('\ncomponent main = MerkleTree();\n')

    # Create the command to run the compilation
    compile_code('circom', 'hash_computation.circom', ['--r1cs', '--wasm', '--sym', '-l', '../'])
    
    #Flatten the weights
    flatten_weights_path = flatten_weights('../'+ weights_path, 'hash_computation')

    os.chdir('hash_computation_js')

    # Create the command to run the witness generation
    compile_code('node', 'generate_witness.js', ['hash_computation.wasm',  '../flattened_weights.json',  '../witness.wtns'])

    #No permission to snarkjs in the docker container
    """
    # Move to the parent directory
    os.chdir('../')

    # Create the command to run the hash computation
    compile_code('snarkjs', 'wtns export json', [ 'hash_computation/witness.wtns', 'hash_computation/witness.json'])

    # Open the witness JSON file
    with open('witness.json', 'r') as file:
        file_content = file.read()

    # Parse the file content as a JSON array
    data = json.loads(file_content)

    # Retrieve the second element
    hash = data[1]
        
    return hash

    """

def compile_code(language, sourcecode, args):
    # Define the command to execute
    command = [language, sourcecode] + args

    # Execute the command and wait for it to complete
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output, error = process.communicate()

    # Check if the command was successful
    if process.returncode == 0:
        print("Compilation successful!")
        print("Output:", output.decode())
    else:
        print("Compilation failed.")
        print("Error:", error.decode())

