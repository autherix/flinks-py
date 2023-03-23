# FLinks

FLinks will simultaneously run "RoboFinder" and "GoSpider" tools, merge the results with no duplicates, and then return the results.

# Prerequisites
- python3.6+
- GoSpider \[[Here+](https://github.com/jaeles-project/gospider)\]
- RoboFinder \[[Here+](https://git.mihanhosting.net/rezasarvani/robofinder)\]

# How To Config?
Clone configs.json, open it and tweak every setting based on your needs<br>
\[NOTE\]: Check that you have updated Python version in "python-command" key and RoboFinder path in "installation-path" key.

# How to configure python3 package requirements
1. In the project root directory, run the following command:
- `python3 -m venv .venv`
2. Activate the virtual environment:
- `source .venv/bin/activate`
3. Install the required packages:
- `python3 -m pip install -r requirements.txt`
And Ready!

### IS it necessary to use virtual environment every time running the script?
No, you can use the script without activating the virtual environment, but it is recommended to use it.

# How To Use?
1. Using Single Target
- python3.8 flinks.py -d "https://memoryleaks.ir"
2. Using a domain list file as input
- cat domain.txt | python3.8 flinks.py -d -
