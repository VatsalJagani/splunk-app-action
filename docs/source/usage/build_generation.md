# Build Generation

## Generate Splunk App/Add-on Build Artifact

The action automatically generates build artifacts from your GitHub repo.

```yaml
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_app"
```

- `app_dir` is optional if you want to generate the build from the repo root.
- Supports multiple Apps/Add-ons in a single repository.

```yaml
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_splunk_app"

- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "my_splunk_add-on"
```

## UCC Add-on Generator

- Supports Add-on build with UCC Add-on Generator (`ucc-gen`).
- Reference: [Splunk Add-on UCC Framework](https://splunk.github.io/addonfactory-ucc-generator/)
- The `app_dir` folder must have a sub-folder named `package` and a file named `globalConfig.json`.
- Use `ucc-gen init` locally before using this or `ucc-gen build` command.

```yaml
- uses: VatsalJagani/splunk-app-action@v4
  with:
    app_dir: "TA_my_addon"
    use_ucc_gen: true
```
