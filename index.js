const core = require('@actions/core');
const github = require('@actions/github');
const exec = require('@actions/exec');

let cli_arguments = process.argv
let python_file = cli_arguments[2]   // first cli argument

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
        console.log(`running python file: ${__dirname}/${python_file}`);
        await exec.exec('python', ['-u', `${__dirname}/${python_file}`], options);
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