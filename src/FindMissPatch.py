from calendar import c
from email.headerregistry import Address
from hmac import compare_digest
import os

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
        return res

    def clean(self):
        self.shell_command("rm tmp_file")

    def parse_file(self, file):
        f = open(base_address + file)
        line = f.readlines()
        file_dict = {}
        lines = 0
        for i in line:
            lines += 1
            # print(i)
            commit = i.split(' ')[0]
            subject = i[11:-1] + str(lines)
            file_dict[subject] = commit
        return file_dict

    def do_parse(self, branch, start = None, end = None):
        global org_branch, income_branch
        output_file = "org_tmp"
        gitfunciton = GitFunction()
        self.shell_command("cd " + org_branch_address)

        if not branch:
            output_file = "income_tmp"
            self.shell_command("cd " + income_branch_address)
         
        ret = gitfunciton.get_commit(output_file, start, end, branch)
        if ret :
            print("exc get %s commit failed"%(output_file))
        
        if branch:
            org_branch = self.parse_file(output_file)
        else:
            income_branch = self.parse_file(output_file)

    def compare(self, dict_1, dict_2, dict_output):
        for i in dict_1.keys():
            is_included = False
            org_key = i[0 : -2]
            for j in dict_2.keys():
                if org_key in j:
                    is_included = True
                    break
            if not is_included:
                dict_output[i] = dict_1[i]
        return dict_output

    def output_patch(self, dict):
        idx = 0
        header_length = len(patch_dir)
        for k in dict.keys():
            command = "cd " + org_branch_address + " && "
            idx += 1
            command += "git format-patch " + str(dict[k]) + " -1 -o" + patch_dir
            # print("command is %s"%(command))
            file_name = self.__shell_command(command)
            
            if idx <= 9:
                new_header = "000" + str(idx)
            elif 10 <= idx <= 99:
                new_header = "00" + str(idx)
            elif 100 <= idx <= 999:
                new_header = "0" + str(idx)
            elif 1000 <= idx <= 9999:
                new_header = str(idx)
            else:
                print("There are too many patches")
                exit()
            # print(len(patch_dir))
            file_name = file_name.replace("\n", "")
            file_name = file_name[header_length: ]
            new_name = new_header + file_name[4: ] 
            print("file_name is %s, new_name is %s"%(file_name, new_name))
            os.rename(patch_dir + file_name, patch_dir + new_name)


class GitFunction:
    def get_commit(self, output_file, start, end, branch):
        base_funciton = BaseFunction()
        address = org_branch_address
        if not branch:
            address = income_branch_address
        command = "cd " + address + " && git log --oneline "
        
        if start:
            command += str(start) + "~1.."
            tmp = "HEAD"
            if end:
                tmp = str(end)
            command += str(tmp)
        
        command += " --reverse > " + base_address + output_file
        
        return base_funciton.shell_command(command)



base_address = "/data/compare_res/"
patch_dir = base_address + "miss_patch/"
org_branch_address = "/data/workspace/kvm4.0_kernel/"
income_branch_address = "/data/workspace/tk4"
org_strat_commit = "8922c163a"
# org_end_commit = "500a95dda"
org_end_commit = None
income_strat_commit = "cfeca43f1fe9c4daf8763c4a720ec2ad4357e5f1"
org_branch = {}
income_branch = {}
compare_res = {}


if __name__=="__main__":
    base_funciton = BaseFunction()
    gitfunciton = GitFunction()
    ORG_BRANCH = True
    INCOME_BRANCH = False    

    print("Hello World")

    base_funciton.shell_command("mkdir "+ base_address)
    base_funciton.do_parse(ORG_BRANCH, org_strat_commit, org_end_commit)
    base_funciton.do_parse(INCOME_BRANCH)
    base_funciton.compare(org_branch, income_branch, compare_res)
    base_funciton.output_patch(compare_res)
    # base_funciton.clean()
