# Overview

Welcome to **splunk-app-action**!

This documentation covers the usage, capabilities, and development of the custom GitHub Action for Splunk Apps and Add-ons. It is designed for ReadTheDocs and uses MyST/Markdown formatting.

## What does this GitHub Action do?


:::{mermaid}
graph TD
	A[Start] --> B([Push to GitHub])
	B --> C>Action Triggered]

	C --> D{Use UCC Gen?}
	D --> |Yes| E([ucc-gen build])
	E --> F([Optionally: Run User Defined Commands])

	D --> |No| F
	F --> G([Generate build with tar command])

	G --> H([App Inspect Check])
	H --> |Yes| I(Build Successful)
	H --> |No| J(Build Failed - App-Inspect Errors)

	I --> K{Is Add App Utilities?}
	J --> K

	K --> |Yes| L([Adding App Utilities])
	L --> M{Any changes to code?}
	M --> |Yes| N([Pull Request Created])
	M --> |No| O([Build Artifacts Created])
	N --> O

	K --> |No| O
:::

- Automatically generates Splunk App and Add-on builds
- Runs app-inspect checks (with the App-Inspect/Splunkbase API) on commit/push
- Performs Splunk cloud checks
- Supports UCC Generator for Add-ons
- Provides utilities for Splunk Apps and Add-ons
- Works in private repositories

See the following sections for details on capabilities, usage, inputs, troubleshooting, and release notes.
