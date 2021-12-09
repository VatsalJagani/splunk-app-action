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
        await exec.exec('python', [`${__dirname}/app_inspect.py`], options);
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
    console.log(`js file's directory: ${__dirname}`);
    var walk    = require('walk');
    var files   = [];

    // Walker options
    var walker  = walk.walk(__dirname, { followLinks: false });
    // var walker  = walk.walk('C:\\Users\\vatsal\\Downloads', { followLinks: false });

    walker.on('file', function(root, stat, next) {
        // Add this file to the list of files
        files.push(root + '/' + stat.name);
        next();
    });

    walker.on('end', function() {
        files.forEach(element => {
            console.log(element)
        });
    });

    // run();
} catch (error) {
    core.setFailed(error.message);
}