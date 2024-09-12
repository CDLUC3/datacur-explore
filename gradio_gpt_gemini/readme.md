# Demo setup

## Preliminaries

You need to have accounts for access to the OpenAI API and the Gemini API (VertexAI).

You'll need to create a project in VertexAI and enable access with Google Cloud IAM in the control panel.

Be sure your project is working and then follow steps at
https://cloud.google.com/docs/authentication/provide-credentials-adc#on-prem for the on-premises setup to get a key
file with the access information you need.

The key file will go somewhere on the server outside the application directory.

For OpenAI, you'll need to create an account and get an API key. Put the key in config.yaml which gets read at startup.

```yaml
openai_api_key: "sk-proj-yourapikey"
```

## Server manual install -- python

```bash
# Install pyenv
curl https://pyenv.run | bash

# get Ashley to yum install libraries needed to do python installs with pyenv
sudo yum install gcc glibc glibc-common gd gd-devel -y
sudo yum install -y openssl-devel bzip2-devel zlib-devel readline-devel sqlite-devel libffi-devel xz-devel gdbm-devel ncurses-devel libuuid-devel

# Install python 3.10.13
pyenv install 3.10.13
```

## Application "install"

```bash
# Clone the repo
git clone https://github.com/CDLUC3/datacur-explore.git

# to update to the latest version of the main branch
cd datacur-explore
git pull

# Add the file 'config.yaml' inside the  gradio_gpt_gemini directory with contents as explained above.
# Add the key file for VertexAI outside the application directory and track where it is since you'll need to set an
# environment variable to point to it.
```

## Running the application

```bash
cd datacur-explore/gradio_gpt_gemini  # if you're not already in here
screen -S gradio_gpt_gemini # create a screen session so you can leave it running in the background
GOOGLE_APPLICATION_CREDENTIALS=../../path/to/google/file.json python app.py --listen=0.0.0.0
# ALT-A, D to detach from the screen session
```

## Updating the application
```bash
screen -x  # reattach to the screen session
# CTRL-C to stop the application
git pull
GOOGLE_APPLICATION_CREDENTIALS=../../path/to/google/file.json python app.py --listen=0.0.0.0
```