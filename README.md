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

### Installing and Prerequisites

In order to not bloat your Python installation, it is recommended to run this
project in a virtual environment. To do so, run

```
python -m venv venv && source bin/activate/venv
```

After that, install the dependencies using

```
python -m pip install -r requirements.txt
```

After that, edit the config.ini file to input your Github Organisation and Team
as well as your Github Access Token, which you can generate [here](https://github.com/settings/tokens).
Right now, this project is optimised for being used in an enterprise context where
you have a Github Organisation with several teams. If you have a different usecase,
please create an issue and I'll try creating a solution for that :)