
import('./snarkjs/src/powersoftau_export_json.js').then((module) => {
    const wtnsExportJson = module.default;
    const wtnsFileName = './hash_computation/witness.wtns'; // Replace with process.argv[2];
    const jsonFileName = './hash_computation/witness.json'; // Replace with process.argv[3];
  
    // Call the function with the provided file names
    const w = wtnsExportJson(wtnsFileName);
    const bfj = require('bfj');
    const stringifyBigInts = require('my-library');

    // Assuming you have the `json` object available
    const json = bfj.stringify(stringifyBigInts(w), { space: 1 });
    bfj.write(jsonFileName, json);

  });