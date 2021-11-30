/* tslint:disable:linebreak-style no-unsafe-any no-submodule-imports no-relative-imports no-console */
/**
 * There are four parts to the extension: Base URL, port, DNS server, and decision
 * @baseURL - url to scan.
 * @port (optional) - port to scan (default is 443)
 * @dnsserver dnsserver to use (default is 8.8.8.8)
 * @failBuild whether or not to fail the task on failed test
 */

import * as tl from 'azure-pipelines-task-lib/task';
import * as trm from 'azure-pipelines-task-lib/toolrunner';
import * as isIp from 'is-ip';
import * as path from 'path';
import * as url from 'url';
import { getPythonPath } from './getpythonpath';

async function run(): Promise<void> {
    try {
        tl.setResourcePath(path.join(__dirname, 'task.json'));

        const baseURL: string = <string>tl.getInput('baseURL', true);
        const port: string = <string>tl.getInput('port', true);
        const dnsserver: string = <string>tl.getInput('dnsserver', true);
        const decision: boolean = <boolean>tl.getBoolInput('failBuild', true);

        // Get failTaskOnFailedTests preference
        let testDecision: string;
        if (decision === false) {
            testDecision = 'pass';
        } else {
            testDecision = 'fail';
        }

        // Check targetdomain formatting
        let hostname: string | null = baseURL;
        if (hostname.startsWith('http')) {
            const myURL: url.UrlWithStringQuery = url.parse(hostname);
            hostname = myURL.hostname;
        }

        // Check port number
        if (Number(port) > 65535) {
            throw new Error(tl.loc('portNotValid'));
        }

        // Validate the DNS server formatting
        if (!isIp.v4(dnsserver)) {
            throw new Error(tl.loc('dnsserverNotValid'));
        }

        // Get Python 3 path
        const pyPath: string = await getPythonPath();
        console.log('PYTHON PATH: ' + `${pyPath}`);

        try {
            // Install setuptools and wheel
            const pythonsetup: trm.ToolRunner = tl.tool(pyPath);
            pythonsetup.arg('-m');
            pythonsetup.arg('pip');
            pythonsetup.arg('install');
            pythonsetup.arg('--upgrade');
            pythonsetup.arg('pip');
            pythonsetup.arg('setuptools');
            pythonsetup.arg('wheel');
            await pythonsetup.exec();
            tl.setResult(tl.TaskResult.Succeeded, 'python setup was successful.');

        } catch (err: any) {

            return tl.setResult(tl.TaskResult.Failed, 'python setup failed.');
        }

        try {
            // Install dnspython, junitparser, and sslyze
            const packageSetup: trm.ToolRunner = tl.tool(pyPath);
            packageSetup.arg('-m');
            packageSetup.arg('pip');
            packageSetup.arg('install');
            packageSetup.arg('-r');
            packageSetup.arg(path.join(__dirname, 'requirements.txt'));
            //packageSetup.arg('--upgrade');
            //packageSetup.arg('dnspython==2.0.0');
            //packageSetup.arg('junitparser==1.6.3');
            //packageSetup.arg('sslyze==3.1.0');
            await packageSetup.exec();
            tl.setResult(tl.TaskResult.Succeeded, 'Python package install was successful.');
        
        } catch (err) {

            return tl.setResult(tl.TaskResult.Failed, 'Python package install failed.');
        }

        try {

            // Run the scan and generate the results
            const scan: trm.ToolRunner = tl.tool(pyPath);
            scan.arg(path.join(__dirname, './python/scanner.py'));
            scan.arg('--dns');
            scan.arg(`${dnsserver}`);
            scan.arg('--target');
            scan.arg(`${hostname}`);
            scan.arg('--port');
            scan.arg(`${port}`);
            scan.arg('--decision');
            scan.arg(`${testDecision}`);
            await scan.exec();
            
            return tl.setResult(tl.TaskResult.Succeeded, 'Scan ran successfully.');
        
        } catch (err) {
            tl.setResult(tl.TaskResult.Failed, 'Scan was unsuccessful.');

        }

    } catch (err: any) {
        tl.error(err.message);
        tl.setResult(tl.TaskResult.Failed, tl.loc('taskFailed', err.message));

    }
}

run();
