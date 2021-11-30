import { getPythonPath } from '../getpythonpath';
import 'mocha';
const chai = require('chai');
const expect = chai.expect;

describe('getPythonPath.ts tests', function() {
  describe('Determine python path on a Microsoft or self-hosted agent', function() {
    it('Should return python path.', async function() {

      // Get the Python path
      expect(function () {getPythonPath}).to.not.throw();

      const pythonPath: string = await getPythonPath();
      console.log('pythonPath: ' + pythonPath);
      expect(pythonPath).to.include('python3');

    });
  });
});
