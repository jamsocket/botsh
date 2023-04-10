# `botsh`

`botsh` is a task runner powered by OpenAI and Docker.

Invoke botsh by providing a task as a command line argument.

botsh will create a bare Ubuntu Docker container associated with
the current directory, or create one if one does not exist. botsh
will then attach the OpenAI API to a shell running in the container
to attempt to complete the given task.

The AI is explicitly told that it is allowed to install software,
and will typically install programs as needed to complete its task.
Installed software remains confined to the container.

When `botsh` is invoked, the current working directory is mounted
into the container and can be modified by programs the agent runs.
The filesystem outside of the current working directory is sealed
off from the container.

## Setup

`botsh` expects an OpenAI API key to be provided as the `OPENAI_API_KEY`
environment variable.

`botsh` also requires Docker to be running on the system.

## Examples

    # botsh "convert cat.jpg into a png file"

    # botsh "use a remote service to find my public ip and base64 encode it"