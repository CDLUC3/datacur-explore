# Data curation exploration code

The repo is for sharing small exploratory projects and shouldn't be considered robust
production code.

## Starting/stopping the gradio interfaces

ssh to the server under the role account (or sudo su - \<user\>) after logging in as yourself.

Once you're in the server you can use the following script to start and stop the gradio interfaces.
The script in the home directory of the role account. (~)

```bash
~/gradio-control.sh
```

## Actions for the script

- *start* will start the server on the port.
- *stop* will stop the server on the port.
- *status* will show the status of the server on the port.
- *restart* will stop and start the server on the port.

## Updating the libraries

The lightest weight way to handle locked dependencies right now is with `pip-tools`
which uses `requirements.in` as a list of dependencies and then writes `requirements.txt` 
as the locked version of libraries.  To install pip tools: `pip install pip-tools`.

We probably need more than just pip alone since for dependabot to function fully, it
needs to see the full set of dependencies and versions someplace and pip-tools will
do this without a lot of extra overhead.  In the future we may go towards a more
robust solution.

To create the locked version of the libraries:

```
pip-compile requirements.in  # creates requirements.txt
```

And to upgrade

```
pip-compile requirements.in --upgrade  # updates requirements.txt
```

To install the dependencies:

```
pip-sync requirements.txt
```

