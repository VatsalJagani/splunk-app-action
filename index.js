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
            stdout += data.toString();
        },
        stderr: (data) => {
            stderr += data.toString();
        }
    };

    try {
        await exec.exec('python', ['app_inspect.py'], options);
    } catch (error) {
        errorStatus = "true";
        core.setFailed(error);
    } finally {
        core.setOutput("stdout", stdout);
        core.setOutput("stderr", stderr);
        core.setOutput("error", errorStatus);
    }
}


try {
    run();
} catch (error) {
    core.setFailed(error.message);
}