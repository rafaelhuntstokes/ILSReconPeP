import sys
import os
import string
import argparse

def check_dir(dname):
    """Check if directory exists, create it if it doesn't"""
    if(dname[-1] != "/"):
        dname = dname + "/"
    direc = os.path.dirname(dname)
    try:
        os.stat(direc)
    except:
        os.makedirs(direc)
        print "Made directory %s...." % dname
    return dname

def pycondor_submit(exe_name, base_name, img_dir, input_file, over_dir, sleep_time = 1, priority = 5):
    '''
    submit a job to condor, write a sh file to source environment and execute command
    then write a submit file to be run by condor_submit
    '''

    print base_name

    ### set a condor path to be called later
    
    condor_path = "{0}".format(over_dir)
    exec_path = img_dir + "bin/" + exe_name

    out_macro_text = "#!/usr/bin/sh  \n" + \
                     "source " + str(os.getenv('ENV_FILE')) + "\n" + \
                     "source " + str(os.getenv('RAT_ROOT')) + "env.sh" + "\n" + \
                     "cd " + str(img_dir) + "\n" + \
                     str(exec_path) + " " + os.path.abspath(input_file) + " " + os.path.abspath(over_dir) + "/" + str(base_name) + ".root \n"                     

    sh_filepath = "{0}sh/".format(condor_path) + str(base_name).replace("/", "") + '.sh'
    if not os.path.exists(os.path.dirname(sh_filepath)):
        os.makedirs(os.path.dirname(sh_filepath))
    sh_file = open(sh_filepath, "w")
    sh_file.write(out_macro_text)
    sh_file.close()
    os.chmod(sh_filepath, 0o777)
    
    ### now create submit file
    error_path = os.path.abspath('{0}/error'.format(condor_path))
    output_path = os.path.abspath('{0}/output'.format(condor_path))
    log_path = os.path.abspath('{0}/log'.format(condor_path))
    submit_path = os.path.abspath('{0}/submit'.format(condor_path))

    universe = "vanilla"
    notification = "never"
    n_rep = 1
    getenv = "False" # "False"

    submit_filepath = os.path.join(submit_path, base_name)
    submit_filepath += ".submit"
    out_submit_text = "executable              = " + str(sh_filepath) + "\n" + \
                     "universe                = " + str(universe) + "\n" + \
                     "output                  = " + str(output_path) + "/" + str(base_name) + ".output\n" + \
                     "error                   = " + str(error_path) + "/" + str(base_name) + ".error\n" + \
                     "log                     = " + str(log_path) + "/" + str(base_name) + ".log\n" + \
                     "notification            = " + str(notification) + "\n" + \
                     "priority                = " + str(priority) + "\n" + \
                     "getenv                  = " + str(getenv) + "\n" + \
                     "queue "+str(n_rep)+"\n"

    ## check and create output path
    if not os.path.exists(os.path.dirname(submit_filepath)):
        os.makedirs(os.path.dirname(submit_filepath))
    out_submit_file = open(submit_filepath, "w")
    out_submit_file.write(out_submit_text)
    out_submit_file.close()


    command = 'condor_submit -batch-name \"' + base_name +'\" ' + submit_filepath
    print "executing job: " + command
    os.system(command)


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Launch a load of fits")
    parser.add_argument('exe', type=str, help='executable name')
    parser.add_argument('inputfile', type=str, help='path to rat ds file')
    parser.add_argument('outputname', type=str, help='output directory name')

    args = parser.parse_args()

    ## check if output and condor directories exist, create if they don't
    exe_name = args.exe
    input_file = args.inputfile
    img_dir = os.getenv('IMAGING_ROOT')
    data_dir = os.getenv('DATA_ROOT')
    base_name = args.outputname
    over_dir = check_dir(data_dir+base_name) 

    log_dir = check_dir("{0}/log/".format(over_dir))
    error_dir = check_dir("{0}/error/".format(over_dir))
    sh_dir = check_dir("{0}/sh/".format(over_dir))
    submit_dir = check_dir("{0}/submit/".format(over_dir))
    output_dir = check_dir("{0}/output/".format(over_dir))

    pycondor_submit(exe_name, base_name, img_dir, input_file, over_dir, sleep_time = 1, priority = 5)

