# GitHub Actions CI/CD Workflows

Automated testing, quality checks, builds, and releases using GitHub Actions.

## Workflows Overview

### 1. **Tests** (`tests.yml`)

Runs on every push to `main`/`develop` and on pull requests.

**What it does:**
- Tests on multiple Python versions (3.8, 3.9, 3.10, 3.11)
- Tests on multiple OS (Ubuntu, Windows, macOS)
- Runs pytest with coverage reporting
- Uploads coverage to Codecov
- Generates test report

**Matrix Strategy:**
```
OS: ubuntu-latest, windows-latest, macos-latest
Python: 3.8, 3.9, 3.10, 3.11
```

**Total Test Combinations:** 12 (optimized for cost)

**Outputs:**
- ✓ Test results
- ✓ Coverage reports
- ✓ JUnit XML test reports
- ✓ Codecov uploads

### 2. **Code Quality** (`code-quality.yml`)

Runs on every push to `main`/`develop` and on pull requests.

**What it does:**
- Black code formatting check
- isort import sorting check
- pylint linting
- flake8 style checking
- mypy type checking

**Key Features:**
- Non-blocking (doesn't fail PR)
- Shows suggestions in PR comments
- Continuous improvement focus

**Tools:**
```
- black: Code formatting
- isort: Import organization
- pylint: Static analysis
- flake8: Style enforcement
- mypy: Type checking
```

### 3. **Build** (`build.yml`)

Runs on push to `main` and on tag creation.

**What it does:**
- Builds Windows EXE
- Builds Linux executable
- Builds macOS app bundle
- Creates DMG for macOS
- Automatic release creation on tags

**Triggers:**
- Push to `main` branch
- Tag creation (`v*.*.*`)
- Manual trigger (workflow_dispatch)

**Outputs:**
- Artifacts available for 90 days
- Windows EXE (~200 MB)
- Linux binary (~200 MB)
- macOS app bundle (~400 MB)
- DMG installer (macOS)

### 4. **Release** (`release.yml`)

Runs when new version tags are pushed.

**What it does:**
- Creates GitHub Release
- Extracts changelog entries
- Generates release notes
- Prepares for PyPI (if configured)

**Trigger:**
```bash
git tag v1.0.0
git push origin v1.0.0
```

**Auto-Release Features:**
- Extracts from CHANGELOG.md
- Creates release page
- Attaches built binaries
- Publishes documentation

## Usage Examples

### Automatic Workflows

These run automatically on certain events:

```bash
# Push code → Triggers tests + quality checks
git push origin main

# Create tag → Triggers build + release
git tag v1.0.0
git push origin v1.0.0
```

### Manual Workflows

Some workflows can be triggered manually:

1. Go to **Actions** tab on GitHub
2. Select workflow (e.g., "Build Executables")
3. Click "Run workflow"
4. Select branch
5. Click "Run"

## Workflow Status Badges

Add to README.md:

```markdown
[![Tests](https://github.com/AdamWojciechowskiPL/Modbus-monitor/workflows/Tests/badge.svg)](https://github.com/AdamWojciechowskiPL/Modbus-monitor/actions/workflows/tests.yml)
[![Code Quality](https://github.com/AdamWojciechowskiPL/Modbus-monitor/workflows/Code%20Quality/badge.svg)](https://github.com/AdamWojciechowskiPL/Modbus-monitor/actions/workflows/code-quality.yml)
[![Build](https://github.com/AdamWojciechowskiPL/Modbus-monitor/workflows/Build%20Executables/badge.svg)](https://github.com/AdamWojciechowskiPL/Modbus-monitor/actions/workflows/build.yml)
```

## Accessing Artifacts

### From GitHub Actions Tab

1. Go to **Actions** tab
2. Click on workflow run
3. Scroll down to **Artifacts**
4. Download artifact

### From Command Line

```bash
# Download latest Windows build
gh run download -n modbus-monitor-windows

# Download specific run
gh run download <run-id> -n modbus-monitor-windows
```

## Environment Variables & Secrets

### Available in Workflows

```yaml
# Automatic
GITHUB_TOKEN      # GitHub authentication
GITHUB_REF        # Branch/tag ref
GITHUB_REPOSITORY # repo owner/name
```

### Custom Secrets (Optional)

To add secrets for PyPI publishing:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add:
   - `PYPI_API_TOKEN`: PyPI authentication
   - `CODECOV_TOKEN`: Codecov (optional)

## Performance & Cost

### Execution Time

```
Tests:         3-5 minutes (per matrix job)
Code Quality:  1-2 minutes
Build:         5-10 minutes (per OS)
Release:       1-2 minutes
```

### GitHub Actions Minutes

**Free tier:** 2,000 minutes/month

**Current usage per month (estimate):**
- Tests: 600 minutes (12 jobs × 5 min)
- Quality: 30 minutes
- Build: 150 minutes (3 OS × 5 min)
- **Total: ~780 minutes**

Well within free tier!

## Troubleshooting

### Workflow Not Running

**Check:**
- ✓ Workflow file in `.github/workflows/`
- ✓ Syntax is valid YAML
- ✓ Trigger conditions met (branch, tag, etc)
- ✓ Repository settings enabled Actions

### Tests Failing

**Common causes:**
- Missing dependencies (install in workflow)
- Python version mismatch
- Platform-specific issues
- Environment variables needed

**Debug:**
1. Click failed workflow
2. Expand step that failed
3. Check error output
4. Run locally: `pytest`

### Build Failing

**Common causes:**
- PyInstaller hidden imports missing
- System dependencies not installed
- Python version too old

**Fix:**
1. Add to `--hidden-import` in build.py
2. Install system libs in workflow
3. Update Python version

## Customization

### Add Python Version

Edit `.github/workflows/tests.yml`:

```yaml
matrix:
  python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
```

### Add OS Matrix

Edit build matrix to include more platforms:

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
```

### Customize Build Options

Edit `build.py` and update workflows:

```yaml
- name: Build
  run: python build.py --custom-option
```

## Best Practices

✅ **Keep workflows simple:** One concern per workflow
✅ **Use caching:** Cache pip dependencies
✅ **Set timeouts:** Prevent hanging jobs
✅ **Test locally first:** Run tests before pushing
✅ **Use status checks:** Require passing tests for PRs
✅ **Monitor costs:** Watch GitHub Actions usage
✅ **Document changes:** Update this file

## Related Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Artifacts & Caching](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)
- [Testing & Coverage](../tests/README.md)
- [Build Guide](../../BUILD.md)

## Support

For workflow issues:

1. Check workflow YAML syntax
2. Review error output in Actions tab
3. Test locally first
4. Check GitHub Actions status: https://www.githubstatus.com/

---

**Happy CI/CD!** 🚀
