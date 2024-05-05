[![Build](https://github.com/WhoKnowsWhoCares/Huggingface_TextSummary/actions/workflows/build-test.yml/badge.svg?branch=master)](https://github.com/WhoKnowsWhoCares/Huggingface_TextSummary/actions/workflows/build-test.yml) [![Docker Build](https://github.com/WhoKnowsWhoCares/Huggingface_TextSummary/actions/workflows/docker-build-deploy.yml/badge.svg?branch=master)](https://github.com/WhoKnowsWhoCares/Huggingface_TextSummary/actions/workflows/docker-build-deploy.yml) [![Deploy by Runner](https://github.com/WhoKnowsWhoCares/Huggingface_TextSummary/actions/workflows/registry-pull.yml/badge.svg?branch=master)](https://github.com/WhoKnowsWhoCares/Huggingface_TextSummary/actions/workflows/registry-pull.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

# TextSummary - service for text processing with api on FastApi and Gradio interface.

Dedicated service for Summarization and Sentiment of the text. For it, I use dockerized FastAPI server with simple Gradio interface. Additionally, there are lazy loading for ML models to release resources and verification to prevent bots from constantly using this service. API available through basic authentication.

You could check sevice on [Huggingface Spaces](https://huggingface.co/spaces/asFrants/TextSummarization)

---

## How to install

### Install software via terminal

First of all you need to have [Poetry](https://python-poetry.org/)

```
pip install poetry
```

### Clone github project, install dependencies

```
 git clone https://github.com/WhoKnowsWhoCares/Huggingface_TextSummary TextSummary \
 cd ./TextSummary \
 poetry install
```

### Configure .env file

Rename .env_template to .env and fill variables:

- `SITE_KEY, SECRET_KEY` - constants for recaptcha v2 from [google](https://www.google.com/recaptcha/about/)
- `API_***` - constants for API authorization
- `CAPTCHA***` - secrets on images from ./staric/images/\*
- `PORT` - port for the service

## To run

```
poetry run python run.py
```
