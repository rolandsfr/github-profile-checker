# GitHub profile checker
CLI utility written in Python for detecting weak spots in GitHub profiles

## Installation
Since the CLI is written in Python you will have to first install python itself
and then run
```bash
python -m pip install gpc-cli
```
After the installation you should have a ``gpc`` namespace available in your currently running user.

## Usage
This CLI implies 3 main types of commands:

### Authorization
To be able to fully scan your GitHub account, make sure to authorize through GitHub OAuth using
```bash
gpc login
```

### Profiles
You can also locally save and remove GitHub profiles you are willing to scan.  
Use
```bash
gpc profile add <username>
```
to locally save a profile.
You can also remove, list all and remove all profiles.
Use
```bash
gpc profile --help
```
to further explore this.

## Analysis
The analyzation command itself, that scans through the given profile and creates a summary that is stored in user's home directory in the gpc-data folder.
To create this summary, run
```bash
gpc analyze <username>
```
<b>NOTE:</b> You can omit the username argument if you are already authorized and want to deep-analyze your own profile.
<br/>You can also use this command with the ``--fl`` flag to generate summaries for all the locally saved profiles.

## Motivation
The CLI was created with a purpose of helping developers on GitHub to clean up their possibly 'messy' profiles and organize
their projects.  
If you are applying for any IT related job, make sure to <i>tidy</i> your profile and this CLI will make it a way easier and 
pleasant process.

<b>P.S.</b></br>
the CLI initializer word ``gpc`` is just an abbreviation for
<b>g</b>ithub-<b>p</b>rofile-<b>c</b>hecker

## License
[MIT](https://opensource.org/licenses/MIT)