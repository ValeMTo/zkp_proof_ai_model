import json

def read_json_file(file_path, circuit_path):
    # Read the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Retrieve the first three results
    compilation = int(data[0])

    positions = find_word_positions(circuit_path, 'main.out')

    output =data[min(positions): max(positions)+1]

    incorrect_hash = int(data[max(positions) + 1])

    if (compilation == 1):
        print("Compilation successful")
        if (incorrect_hash == 1):
            print("Incorrect hash: the weights used are not the declared ones")
        else:
            print("Correct hash: the weights used are the declared ones")
    else:
        print("Compilation failed")
    
    return output

def find_word_positions(filename, word):
    positions = []

    with open(filename, 'r') as file:
        lines = file.readlines()

    for i in range(len(lines)):
        if word in lines[i]:
            positions.append(i+1)
    
    return positions

def main():
    output = read_json_file('./output/witness.json', './output/circuit.sym')

    print("Output:", output)

if __name__ == "__main__":
    main()