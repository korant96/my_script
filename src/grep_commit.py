from calendar import c
from email.headerregistry import Address
from hmac import compare_digest
import os
import argparse

parser = argparse.ArgumentParser(description='搜索patch是否被包含进了源码中')

parser.add_argument('--output', '-o', help='the output path', required=True)
parser.add_argument('--patch_income', '-p', help='the patch income path', required=True)
parser.add_argument('--src_path', '-s', help='source code path', required=True)
parser.add_argument('--debug' , '-d', help='entre debug mode', action='store_true')
args = parser.parse_args()

class BaseFunction:
    def shell_command(self, command):
        ret = os.system(command)
        if ret :
            print("exec %s failed"%(command))
        return ret

    def __shell_command(self, command):
        result = os.popen(command)
        res = result.read()
        # print("__shell_command res is %s"%(res))
        if not res:
            print("exec %s failed"%(command))

def ParsePatchSubject(file):
    subject = ""

    if args.debug:
        print("file path is :" + file)
    f = open(file)
    lines = f.readlines()
    for i in lines:
        if "Subject" in i and "PATCH" in i:
            if args.debug:
                print("Subject line is: " + i)
            subject_start_idx = 0
            for j in i:
                if j == ']':
                    break
                else:
                    subject_start_idx += 1
            subject = i[subject_start_idx + 1 : -1]
            break
    # print(subject)
    return subject.strip(' ')

def IsPatchInclued(subject, src):
    base_funciton = BaseFunction()
    ret = 1
    command = 'cd ' + src + ' && ' + "git log --oneline|grep '" + subject + "'"
    if args.debug:
        print("shell command is: " + command)
        input()
    if subject != "":
        ret = base_funciton.shell_command('cd ' + src + ' && ' + "git log --oneline|grep '" + subject + "'")
    
    if ret:
        return False
    else:
        return True
    # print(ret)

def OutputMissedPatch(org_patch_path, output_path):
    base_funciton = BaseFunction()

    base_funciton.shell_command("cp " + org_patch_path + " " + output_path)

if __name__=="__main__":
    # CmdLineArg()
    files= os.listdir(args.patch_income)
    for file in files:
        file_path = args.patch_income + "/" + file
        subject = ParsePatchSubject(file_path)
        if not IsPatchInclued(subject, args.src_path):
            OutputMissedPatch(file_path, args.output)
        # print(subject)