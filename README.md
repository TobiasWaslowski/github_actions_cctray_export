# Github Action CCTray Parser

The Github Action Result Retriever fetches data on Github Action runs and 
neatly packages them into an XML file that is coherent with the cctray standard.

## About CCTray

From the [cctray.org](https://cctray.org/v1/) website:


    Various Continuous Integration monitoring/reporting tools exist. 
    These tools work by polling Continuous Integration servers for summary information and presenting it appropriately to users.

    If a Continuous Integration server can offer a standard summary format,
    and a reporting tool can consume the same, then we get interoperability between reporting tools and CI Servers.

    Over the years the CCTray format has become the de-facto standard for this purpose.
    Many CI servers implement their own, richer, APIs but also implement the CCTray feed to support 
    various monitoring tools, including CCMenu.

It can be hard to integrate results from Github Actions into any kind of Dashboard right now.
Therefore, this tool can parse the Github Actions API and output a valid CCTray.xml.

### On the CCtray Format

Further from the [cctray.org](https://cctray.org/v1/) website:

A CCTray XML-file consists of single \<Projects> node, the document root, which contains 0 or many \<Project> nodes.
Each \<Project> may have the following attributes:

|name               |description|type|required|
|---                |---|---|---|
|name               |the name of the project                    |string     |yes   |
|activity           |the current state of the project	        |string enum : Sleeping, Building, CheckingModifications	|yes   |
|lastBuildStatus    |a brief description of the last build	    |string enum : Success, Failure, Exception, Unknown	        |yes   |
|lastBuildLabel     |a referential name for the last build	    |string     |no    |
|lastBuildTime      |when the last build occurred	            |DateTime   |yes   |
|nextBuildTime      |when the next build is scheduled to occur (or when the next check to see whether a build should be performed is scheduled to occur)	   |DateTime   |no   |
|webUrl             |a URL for where more detail can be found about this project	   |string(URL)   |yes   |

Currently, Github Actions statuses are being mapped to the CCTray parameters.
Right now, `lastBuildStatus` corresponds to `job.conclusion` and `activity` corresponds to `job.status`.
However, since slightly different terms are used in the CCTray standard and the Github Actions API,
some errors may be occuring here.

## Getting Started

As the project progresses, ideally you could run this as a Docker image. 
For now, however, you'll have to manually clone and run the script for yourself.

### Prerequisites

You'll need Python and possibly Pip on your machine. 

### Installing

After you've cloned the repository, you'll need to set the GITHUB_TOKEN environment variable.
Check the next step on how to generate that token.

You can either set the token in your .bash_profile, .bashrc or something similar, adding

``
    export GITHUB_TOKEN=${YOUR_GITHUB_TOKEN}
``

and then running ``source .bashrc`` or whatever your equivalent of that file might be.

Alternatively, you can just set that variable in the command line or a local config file 
of yours. Perspectivically, I'm gonna implement a more elegant solution for that issue, 
but this works for now.

### Using a Github Access Token for Maven

This project relies on certain artifacts that are hosted in the Github Package Registry.
Because they're hosted privately by the OttoPaymenthub organization, you're going to need Authorization to access them.

Go to Github > Settings > Developer Settings (at the very bottom) > Personal Access Tokens.
Click "Generate new token" and enable the following scopes:

    repo, user, workflow

Now copy the token and enable SSO for the OttoPaymenthub organization.
