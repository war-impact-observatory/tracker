# Contributing to War Impact Observatory

Thank you for your interest in contributing! This project thrives on community input — from data corrections to new impact channels to better visualizations.

## Ways to Contribute

### 1. Data Corrections & Additions
- Spot an error in our numbers? Open an issue with the `data-correction` label.
- Have a better data source? Propose it with evidence of reliability and access.
- Want to add a country beyond G20? See the data schema in `data/schema/schema.json`.

### 2. Code Improvements
- Pipeline scripts in `pipeline/` are Python 3.10+.
- Dashboard is a self-contained React SPA in `index.html`.
- Follow existing code style. Add comments for non-obvious logic.
- All pipeline changes must include test data in `data/test/`.

### 3. Methodology
- Propose new impact channels via GitHub Discussions.
- Improve uncertainty quantification — confidence intervals, sensitivity analysis.
- Peer review existing models — we welcome published economists and researchers.

### 4. Media & Translation
- Translate the press snippet or Twitter thread into other languages.
- Create chart cards or infographics for specific regions.
- Write analysis pieces using our data (with attribution).

## Getting Started

```bash
# Clone the repo
git clone https://github.com/war-impact-observatory/tracker.git
cd tracker

# Install Python dependencies
pip install -r pipeline/requirements.txt

# Run the pipeline locally
python pipeline/merge_and_validate.py

# Open the dashboard
open index.html
```

## Pull Request Process

1. Fork the repo and create a branch from `main`.
2. Make your changes with clear commit messages.
3. Update documentation if your change affects methodology or data schema.
4. Open a PR with a description of what changed and why.
5. Two maintainer approvals required for methodology changes; one for code/data.

## Code of Conduct

- Be respectful and constructive.
- This is a data project, not a political platform. Keep discussions evidence-based.
- No personal attacks, no partisan framing of data.
- We welcome disagreement on methodology — that's how science works.

## Data Submission Guidelines

If submitting new data:
- Provide the source URL and access date.
- Include the raw data file and a description of any transformations.
- Specify the license of the source data.
- Follow the schema in `data/schema/schema.json`.

## Questions?

- GitHub Discussions for methodology and project direction.
- Issues for bugs, data corrections, and feature requests.
- Email: warimpactobservatory@protonmail.com
