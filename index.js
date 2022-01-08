const core = require('@actions/core');
const github = require('@actions/github');
const exec = require('@actions/exec');

async function run() {
    let stdout = "";
    let stderr = "";
    let errorStatus = "false";

    const options = {};
    options.listeners = {
        stdout: (data) => {
            core.setOutput("stdout", data.toString());
            // stdout += data.toString();
        },
        stderr: (data) => {
            core.setOutput("stderr", data.toString());
            // stderr += data.toString();
        }
    };

    try {
        console.log(`running python file: ${__dirname}/app_inspect.py`);
        await exec.exec('python', ['-u', `${__dirname}/app_inspect.py`], options);
        // -u with python is to run python Unbuffered to stream the stdout
    } catch (error) {
        errorStatus = "true";
        core.setFailed(error);
    } finally {
        // core.setOutput("stdout", stdout);
        // core.setOutput("stderr", stderr);
        core.setOutput("error", errorStatus);
    }
}


try {
    console.log(`js file's directory: ${__dirname}`);
    run();
} catch (error) {
    core.setFailed(error.message);
}