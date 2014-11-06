""" pybcompgen
"""
import sys
import subprocess
from subprocess import Popen, PIPE
import unicodedata

def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")

def function(to_complete):
    cmd='''bash -c "printf 'echo MARKER\n{complete}\t\t\x01#\necho MARKER'|bash -i"'''.format(complete=to_complete)
    p1 = Popen(cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    out,err = p1.communicate()
    lines = err.split('\n')
    first_marker = None
    last_marker = None

    for i in range(len(lines)):
        line = lines[i]

        if line.strip().endswith('echo MARKER'):
            if first_marker is None:
                first_marker = i
            else:
                last_marker = i
    #print '#'*80
    #print out,err
    #print '#'*80
    complete_lines = lines[first_marker+2:last_marker-1]
    if not complete_lines:
        # either there are no completion options or
        # there was only one and readline just applied it
        the_line = lines[first_marker+1:last_marker][0]
        #the_command = the_line[the_line.rfind('#;')+1:]
        the_line = remove_control_characters(unicode(the_line))
        tmp = the_line[the_line.find(to_complete)+len(to_complete):-4]
        return [to_complete.split()[-1]+tmp]
    else:
        # there are multiple completion options
        completion_choices_by_row = [x.split() for x in complete_lines]
        completion_choices = reduce(lambda x,y:x+y, completion_choices_by_row)
        return completion_choices

if __name__=='__main__':
    print complete(sys.argv[-1])
