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

For AWS and Bedrock running locally you'll need to log in to the AWS console to make use of boto3.
The configuration is stored in `~/.aws/config`.

The config file looks something like this:

```ini
[profile uc3-dev-ops]
sso_session = uc3
sso_account_id = 1 # change this to the account id you are using
sso_role_name = role_name # change this to the role name you are using
region = us-west-2

[sso-session uc3]
sso_region = us-west-2
sso_start_url = https://cdlsso.awsapps.com/start#/
sso_registration_scopes = sso:account:access
```
Run the following commands to log in to the AWS console and allow boto3 access.
```bash
export AWS_PROFILE=uc3-dev-ops
aws sso login --profile uc3-dev-ops
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

# Add the file 'config.yaml' inside the gradio_gpt_gemini directory with contents as explained above.
# Add the key file for VertexAI outside the application directory and track where it is since you'll need to set an
# environment variable to point to it.
```

## Running the application

```bash
# we have a control start/stop script (example included in repo) called gradio_control.sh
# use start|stop|status|restart as arguments
./gradio_control.sh start
```

## Updating the application
```bash
cd ~/datacur-explore
git pull
```