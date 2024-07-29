# Vulnerability Evaluation and Log Management Application -- VELMA  

This tool assess the security of an application by searching for CVEs in the NVD online database.  
In order to work the tool must be given the service name (URL) and the service type. The service version is automatically retrieved if the module in search_modules.py has been implemented correctly. 

Before running the tool please take care to look up to `search_modules.py` to find if the tool supports the tool you want to scan. If not the tool will print a warning as the tool is not supported.

## I/O consideration
The input is given by the user through the command line.  
The output is a list of CVEs, if you want with the linked description, and their serverity. Moreover the tool compute the sum per risk category and print it at the very last of the reported CVEs list.  
The output is provided on the terminal but can also be provided in:
- TXT format
- PDF format

## Generating the example environment
I have provided an example environment through a `docker-compose.yaml` that allow to test easily how the tool works.  
You can start directly the docker-compose.yaml. This will not install automatically the services provided, but limits to just instantiate them, so expect errors.
You can also start a `env_gen.bat` / `env_gen.sh` (Windows / Linux) to generate automatically the environment also initializing it: MySQL, Wordpress and Joomla services will be automatically installed with the fixed set of configurations (localhost). You can also combine the docker-compose up before and then launch the batch/shell script to generate the environment, in this case simply it will limit to install the services since they are already instatiated.

**NOTE**: in this last case the script will also install automatically Wordpress updating it to the _latest_ version. If you prefer to hold the version, please do not run the automatic installation of wordpress (do the manual one).

## Starting the tool from Python
The tool can be started from the Python script "`tool/tool.py`" by providing the arguments as follows:

`python tool.py [OPTIONS --help] <service_name_1>::<service_type_1>::[configuration_file_1.json] <service_name_2>::<service_type_2>::[configuration_file_2.json] ...`

[OPTIONS] can be:  
`--verbose`: the tool will list also the description for each CVE found  
`--deep`: the tool will also analyze the server provider and the engine running under the service  
`--file <filename>`: the tool will output a specified file.txt with the results of the report  
`--pdf <pdfname>`: the tool will output a specified file.txt (default: "results.txt") and a file.pdf with the results of the report  
`--help`: the tool will output an help with the commands that the user can provide and a brief description of the tool

The configuration file in JSON format, is optional and can be specified for services that load a configuration file (e.g. MySQL).
If you pass a configuration file, please be sure that your function module for searching the version is supported with the loading of a configuration file, otherwise a standard version of the function, if exists, will be called without the configuration file.

**NOTE - 1**: configuration files are searched in the tool/configurations folder, please launch the script after cd into the folder, otherwise the configuration folder is not found.

**NOTE - 2**: the tool follows a "lazy fail" technique, so if the user provide a correct service_1 with its parameters but a wrong service_2 (e.g. omit the service_type_2), the tool will scan the first correct service anyway and will stop at the second, warning the usage of the command line tool.

## Starting the tool from batch / bash script
The tool can be started also from a batch / bash (Windows / Linux) script, with name `velma.bat` / `velma.sh`. This script provides a dockerization of the tool.  
The tool works as explained in previous section, so the arguments can be passed as it was a python call from the command line. Notice that the docker container will automatically delete itself after terminating the vulnerability assessment.

**NOTE**: if runned with the batch/shell script, the tool will be a docker container, so if the generation of pdf or file is requested, please take note that those file would be created within the container, so as this version provides, the docker container will automatically terminate and remove itself: also its files will be removed! If the desired behavior is another please change directly the batch/shell script removing the parameter `--rm` from `docker run` and inspect the container for those files.

### Windows / Linux compatibility
Please note that this tool has been tested primarly on Windows. Some tests have been also runned on Linux and the results of them will be described as follows, but it could be that shell scripts may encounter some errors:
- if runned in Linux, the first time both shell scripts have to be marked as executable (`chmod +x velma.sh`, `chmod +x env_gen.sh`)
- if runned in Linux you have to provide the "sudo" privileges to the shell script, otherwise docker won't start correctly
- as provided in the example environment, please notice that there is an insidious difference when talking about containers between Windows and Linux, that have been reported correctly in the scripts: in Windows the name of the containers are spaced with a dash (e.g. `env-example-joomla-1`), while in Linux are spaced with an underscore (e.g. `env-example_joomla_1`). So if any hand-crafted environment is added please notice this difference, otherwise the scripts may not work.

## Interfacing with external tools
If you start the tool from the batch / bash script `velma.bat` / `velma.sh` you can also provide **as first argument**:
- `use_external <service_name>`  
This allow you to use also external tools on the service provided.  
Full command, for Windows to scan Wordpress service (from tool directory):  
`.\velma.bat use_external http://localhost http://localhost::wordpress`

**NOTE - 1**: this option works with one service at time (per command launch), this allows the user to specify a service that maybe he/she doesn't want to scan with VELMA tool but only with external ones; moreover if the user provide multiple services, this allows the user to specify the exact service between the others that want to scan with the external vulnerability assessment tools.

**NOTE - 2**: results of external tools are written in a file .txt (e.g, wp_scan.txt, dirbusters.txt), they are not translated to pdf format 


### External services currently present  
This is a list of the services currenly present:
- WPScan
- Dirbusters (please note that this tool could block in several way the script you are running depending on its exceptions or behaviors, I suggest to put it at the very last of the list)

## Extensibility
### Extensibility for supporting services
The tool can support several modules for different services, if they are correctly provided.  
Please follow the example to understand how to add a new service correctly and start a scan on it.

**Step 1**  
First of all identify the vendor of your service and the product name, then open the file cpe.py.  
Write you service as follows, after the last line of the service, do not exit the parenthesis:  
`"service_type": f"cpe:2.3:a:vendor_name:product_name:*",`  
for example:  
`"joomla": f"cpe:2.3:a:joomla:joomla:*",`  

**NOTE**: the "service type" will be the `<service_type>` string you will provide when calling the tool when passing the arguments `<service_name>::<service_type>`   

**Step 2**  
Open the search_modules.py and update the file by adding a new implemented function to retrieve correctly the version from that service. For example see the one for Joomla.  
If you like, update also the heading comment with the supported services.

**NOTE**: please check the name of your function, in order to make the tool work, the function name **must** be `search_<service_type>()`. So if I want to add Joomla retriever version, I need to implement the function `search_joomla()`.

**Step 3**  
Run your scan with the new service, for Joomla, directly interacting with the Python script for example:  
`python tool.py http://localhost:9999::joomla`

### Extensibility for external tools
The tool can be also extended by accessing to the `velma.bat` / `velma.sh` file and directly writing the `docker run <external_tool_image_name>` command with the name of the external tool that you want to use, take care of the fact that actually the tool picks just one argument for the external tools that is the `<service_name>` (URL).   

## Example of use
In the following I will show some example you can run with this tool:
- `python tool.py http://localhost:9999::joomla`, Python Module to scan Joomla listening at port 9999
- `python tool.py -d -v http://localhost::wordpress`, Python Module to scan Wordpress listening at port 80, scanning also for server and engine versions if present and with CVEs descriptions
- `.\velma.bat http://localhost:9999::joomla`, batch script to run a docker container with the tool to scan Joomla listening at port 9999
- `.\velma.sh http://localhost:9999::joomla`, equivalent but for bash
- `.\velma.bat -d -v http://localhost:9999::joomla`,  batch script to run a docker container with the tool to scan Joomla listening at port 9999, scanning also for server and engine versions if present and with CVEs descriptions
- `.\velma.bat use_external http://localhost -d -v http://localhost:9999::joomla`, as before but call also external tools (WPScan and Dirbuster)
- `.\velma.bat -d -v -p results.pdf http://localhost::wordpress`, batch script to run a docker container with the tool to scan Wordpress listening at port 80, scanning also for server and engine versions if present and with CVEs descriptions, printing also the results on a PDF file called "results.pdf".
- `.\velma.bat -d -v -f results.txt http://localhost::wordpress`, as before but printing the results on a TXT file called "results.txt".
- `.\velma.bat http://localhost::wordpress http://localhost:9999::joomla`, will run the scan on both services provided.
