/* tslint:disable:linebreak-style no-unsafe-any no-submodule-imports no-relative-imports no-console */
/**
 * There are four parts to the extension: Base URL, port, DNS server, and decision
 * @baseURL - url to scan.
 * @port (optional) - port to scan (default is 443)
 * @dnsserver dnsserver to use (default is 8.8.8.8)
 * @decision whether or not to fail the task on failed test
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
        const decision: boolean = <boolean>tl.getBoolInput('decision', true);

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

        const pypath: string = await getPythonPath();
        console.log('PYTHON PATH: ' + `${pypath}`);

        // Install setuptools and wheel
        const pythonsetup: trm.ToolRunner = tl.tool(pypath);
        pythonsetup.arg('-m');
        pythonsetup.arg('pip');
        pythonsetup.arg('install');
        pythonsetup.arg('--upgrade');
        //pythonsetup.arg('--user');
        pythonsetup.arg('pip');
        pythonsetup.arg('setuptools');
        pythonsetup.arg('wheel');
        const setuptoolsinstall: number = await pythonsetup.exec();
        tl.setResult(tl.TaskResult.Succeeded, tl.loc('pipReturnCode', setuptoolsinstall));

        // Install dnspython, junitparser, and sslyze
        const python3: trm.ToolRunner = tl.tool(pypath);
        python3.arg('-m');
        python3.arg('pip');
        python3.arg('install');
        python3.arg('--upgrade');
        //python3.arg('--user');
        python3.arg('dnspython==2.0.0');
        python3.arg('junitparser');
        python3.arg('sslyze==3.0.8');
        const pipinstall: number = await python3.exec();
        tl.setResult(tl.TaskResult.Succeeded, tl.loc('pipReturnCode', pipinstall));

        // Run the scan and generate the results
        const scan: trm.ToolRunner = tl.tool(pypath);
        scan.arg(path.join(__dirname, './python/scanner.py'));
        scan.arg('--dns');
        scan.arg(`${dnsserver}`);
        scan.arg('--target');
        scan.arg(`${hostname}`);
        scan.arg('--port');
        scan.arg(`${port}`);
        scan.arg('--decision');
        scan.arg(`${testDecision}`);
        const test: number = await scan.exec();
        tl.setResult(tl.TaskResult.Succeeded, tl.loc('scanReturnCode', test));

        return;

    } catch (err) {
        tl.error(err.message);
        tl.setResult(tl.TaskResult.Failed, tl.loc('taskFailed', err.message));

        return;
    }
}

run();
