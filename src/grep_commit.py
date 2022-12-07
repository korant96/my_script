from calendar import c
from email.headerregistry import Address
from hmac import compare_digest
import os
import argparse

parser = argparse.ArgumentParser(description='搜索patch是否被包含进了源码中')

parser.add_argument('--output', '-o', help='patch生成路径', required=True)
parser.add_argument('--patch_income', '-p', help='patch来源路径', required=True)
parser.add_argument('--src_path', '-s', help='源码路径', required=True)
args = parser.parse_args()

# def test_for_sys(output, patch_income):
#     print('the output path is', output)
#     print('the patch_income path is', patch_income)

# def CmdLineArg():
#     test_for_sys(args.output, args.patch_income)

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
    f = open(file)
    lines = f.readlines()
    for i in lines:
        if "Subject: [PATCH]" in i:
            subject = i[16 : -1]
            break
    # print(subject)
    return subject.strip(' ')

def IsPatchInclued(subject, src):
    base_funciton = BaseFunction()

    ret = base_funciton.shell_command('cd ' + src + ' && ' + 'git log --oneline|grep "' + subject + '"')
    
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