# Data Curation: data quality analysis and readme creation proof of concept

## What is this?

This is a proof-of-concept application designed to explore data curation tasks using Large Language Models (LLMs).
It provides a web-based interface for workflows such as:
- **Improving Data Quality**: Analyzing datasets for quality issues.  It works with common tabular formats such as csv,
  tsv and Excel files
- **Readme Generation**: Creating README files from multiple source files or through a multi-stage process.

The project is intended for exploration and experimentation with LLM capabilities in the context of data curation.

## How do I use it?

The application runs as a web server using Gradio. Once running, you can access the interface through your web browser.

The interface is divided into tabs for different functionalities:
1. **Improving data quality**: Tools to check and improve the quality of your data.
2. **Readme from multiple files**: Generate a README by providing multiple input files.
3. **Multi stage readme creation**: A workflow to use more than one LLM (one feeding into another for creating a README.

The workflows are very simiilar with small differences:

1. **Choose your files** locally or give a DOI or dataset landing page URL from either Dryad or Zenodo.
  a. If using a URL or DOI, you may need to click the "Lookup DOI" button to obtain a list of files.
  b. After obtaining the list of files you may choose the files to work with by checking them.  For data quality, choose
     a readme (if available) and a tabular file such as tsv, csv or Excel file.  (For readme from multiple files it will
     try to find and retrieve tabular or existing files for you automatically.)
2. The prompting section has a default setup with system conditioning (basically how the system should act or the role) of the system
   and a user prompt). The prompts can be refined and saved which is what we're calling a "profile."
3. The profile management section allows useful prompts to be loaded or saved so the behavior of the AI agent can be
   customized to give different output which might be better or worse (in general) or for some specific domain, data type or use case.
4. If you choose to use "Frictionless" validation it will run a basic Frictionless Data tabular data validator against the tabular data file.
5. **Choose an LLM model (GPT, Gemini)** and click **Submit to LLM** for output and suggestions to appear on the right side.
   You may save or print the output after it finishes.

Current issues:
- The Llama model relies on AWS Bedrock configuration running within an AWS account (and running on an ECS instance) to work.
- Readme from multiple files will likely produce better output by saving tabular files locally as well as a copy/paste into a text
  file with the contents of the current landing page metadata.  (Just copy and paste the main content from the landing page
  metadata as text and don't worry about formatting). Include a readme if there already is one.
- Multi-stage readme creation sometimes overflows the allowed context size or token per minute limits of a LLM provider, especially
  if the output of the first LLM in the chain is large.  Also if your account has smaller limits than some more expensive
  or *professional* account types it may hit limits (and you may not be allowed to use newer models, either).


## Required configuration of other services

To use the application, you need access to LLM providers like OpenAI or Google Vertex AI (Gemini).

**After cloning the repo or copying the colab (see "How do I run it?" below)**

### Config values for running locally on a server

1.  **Configuration File**:
    - Copy `app/config_example.yaml` to `app/config.yaml`.
    - Fill in the required API keys and settings:
        ```yaml
        openai_api_key: "sk-..."
        google_project: "your-project-id"
        google_location: "us-central1"
        google_api_key: "..."
        dryad_api_key: "..."
        dryad_secret: "..."
        user_agent: "DataCurationExploration/0.3 (mailto:myemail@mydomain.com)"
        ```

2.  **Google Vertex AI**:
    - Ensure you have a Google Cloud project with Vertex AI enabled.
    - Set up authentication (e.g., `GOOGLE_APPLICATION_CREDENTIALS` environment variable pointing to your service account key file).

3.  **AWS (Optional)**:
    - If using AWS Bedrock, ensure your AWS credentials are configured in `~/.aws/config` or via environment variables.

4.  **Dryad API key/secret**:
    - Log in to your Dryad account, go to the "My Account" section and there is a button to set up an API account for your
      use.  Copy the "Account ID" value into `dryad_api_key` and "Secret" value into `dryad_secret`.

### Config values under Google colab

   - Set up the external services listed above under "running locally" and get the values for these items.
   - Go to https://colab.research.google.com/drive/1rcb9HgYxScVzRWhwVpqgavgv28YQbTEs?usp=sharing and then click
     *File* > *Save a copy in Drive*.
   - You should then fill in the configuration for the colab notebook using the key icon on the left side of the notebook.
   - Fill in the exact names shown above with your own values.



## How do I install it on a local machine or server?

### Prerequisites
- Python 3.12 or higher.
- `pip` or `pip-tools`.

You should install Python.  You can have multiple versions of Python installed on Linux-like systems by using *pyenv*.  You
may have a system version of python already installed (often called "python3") which may also work.

### Installation Steps

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/CDLUC3/datacur-explore.git
    cd datacur-explore
    ```

2.  **Install dependencies**:
    It is recommended to use a virtual environment. (create with `python -m venv venv` and activate with `source venv/bin/activate`)
    ```bash
    pip install -r requirements.txt
    ```
    Or if you are using `pip-tools`:
    ```bash
    pip-sync requirements.txt
    ```

3.  **Run the application**:
    You can run the application directly with Python:
    ```bash
    python main.py
    ```
    
    Or use the provided control script (Linux/macOS which may need small modifications in your environment):
    ```bash
    ./gradio_control.sh start
    ```

    By default, the app runs on `http://127.0.0.1:7860`. You can change the host and port using command-line arguments (see `python main.py --help`).

## How do I use it in colab?

Open the colab https://colab.research.google.com/drive/1rcb9HgYxScVzRWhwVpqgavgv28YQbTEs?usp=sharing

1. Create your own copy of the colab sheet for use and modification by clicking *File* > *Save a copy in Drive*
2. In your own copy click the key icon on the left side to fill in the key/value pairs for configuration and secrets (see above)
3. Play each code section of the worksheet (It should show a check mark after playing if successful).
4. After the last section you should see a public sharing URL shown in the output and you can use that to open the web application.

## What is Gradio and how is the code structured?

**Gradio** is an open-source Python library used to build machine learning demos and web applications quickly. It allows developers to create user interfaces for their models with just a few lines of code.

**Code Structure**:

The useful parts of the application live under the `app` directory.

- **`main.py`**: The entry point of the application. It parses command-line arguments and launches the Gradio app.
- **`app/common/`**: common utility functions used in many places.
- **`app/interface/`**: Contains the UI logic.
    - `app.py`: Defines the main application layout and tabs.
    - `pages/`: Contains the specific logic for each tab (e.g., `data_quality.py`, `readme_multi_file.py`).
    - `page_handlers/`: Contain event handlers for the UI
- **`app/config.py`**: Handles configuration loading from `config.yaml` or environment variables.
- **`app/llms/`**: Logic for interacting with different LLM providers.
- **`app/prompt_profiles/`**: contains some default profiles and additional profiles may be saved there.
- **`app/repositories/`**: contains code for interacting with the Dryad and Zenodo repositories.
- **`requirements.in` / `requirements.txt`**: Python dependency definitions.

Also see the [old README](./README-old.md) for older information that may still be useful.