<h1 align="center">GitHub profile checker</h1>
<p align="center">CLI utility written in Python for detecting weak spots in GitHub profiles</p>

<div align="center">
    
  <a href="">![Twitter URL](https://img.shields.io/twitter/url?url=https%3A%2F%2Fgithub.com%2Frolandsfr%2Fgithub-profile-checker)</a>
  <a href="">![PyPI](https://img.shields.io/pypi/v/gpc-cli)</a>
    
 </div>  
 </br>  
 
 ![](https://i.imgur.com/JhZPHV8.jpg)

## Installation
Since the CLI is written in Python you will have to first install python itself
and then run
```bash
pip install gpc-cli
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
You can also read more about ways to clean your GitHub profile in [this medium article](https://medium.com/@rolyuhh/making-your-github-profile-shine-again-b410e373731b).

## License
[MIT](https://opensource.org/licenses/MIT)
