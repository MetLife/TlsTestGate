import * as tl from 'azure-pipelines-task-lib/task';
import { getPythonPath } from '../getpythonpath';
import 'mocha';
const chai = require('chai');
const assert = chai.assert;
const expect = chai.expect;

describe('getPythonPath.ts tests', function() {
  describe('Determine python path on a Microsoft or self-hosted agent', function() {
    it('Should return python path.', async function() {

      // These are the locations of the tool cache for Python 3.x.x on Microsoft hosted agents.
      // My code is asking for Python 3.8; however, due to semantic versioning I cannot test the
      // full path to Python3 because an upgrade from 3.8.6 to 3.8.7 would break the test unnecessarily
      const hostedToolCache: Array<string> = [
        'C:\\hostedtoolcache\\windows\\python\\3.8', // Windows
        '/opt/hostedtoolcache/Python/3.8',           // Linux
        '/Users/runner/hostedtoolcache/Python/3.8'   // OS X
      ];
      // Get the Python path
      const pythonPath: string = await getPythonPath();
      
      // Check to see if the first part of the path is in the pythonPath, which would indicate
      // that we are using a Microsoft hosted agent
      const pathMatch = hostedToolCache.filter(x => x.includes(pythonPath));

      if (pathMatch && pathMatch.length) {
        console.log('Microsoft hosted Python path: ' + pythonPath);
        expect(pythonPath).to.have.string(pathMatch);

      } else {
        const expectedPythonPath: string = tl.which('python3', true);
        console.log('Self-hosted Python path: ' + pythonPath);
        assert.equal(pythonPath, expectedPythonPath);

      }
    });
  });
});
