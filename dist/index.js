/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ 389:
/***/ ((module) => {

module.exports = eval("require")("@actions/core");


/***/ }),

/***/ 103:
/***/ ((module) => {

module.exports = eval("require")("@actions/exec");


/***/ }),

/***/ 977:
/***/ ((module) => {

module.exports = eval("require")("@actions/github");


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __nccwpck_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		var threw = true;
/******/ 		try {
/******/ 			__webpack_modules__[moduleId](module, module.exports, __nccwpck_require__);
/******/ 			threw = false;
/******/ 		} finally {
/******/ 			if(threw) delete __webpack_module_cache__[moduleId];
/******/ 		}
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/compat */
/******/ 	
/******/ 	if (typeof __nccwpck_require__ !== 'undefined') __nccwpck_require__.ab = __dirname + "/";
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be isolated against other modules in the chunk.
(() => {
const core = __nccwpck_require__(389);
const github = __nccwpck_require__(977);
const exec = __nccwpck_require__(103);

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
})();

module.exports = __webpack_exports__;
/******/ })()
;