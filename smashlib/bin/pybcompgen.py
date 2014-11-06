""" pybcompgen
"""
import sys
import subprocess
from subprocess import Popen, PIPE
import unicodedata

def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")

def complete(to_complete):
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

    # SPECIAL CASE: pagination
    if last_marker is None:
        # when this happens there are too many options,
        # ie bash is asking something like this:
        #   Display all 103 possibilities? (y or n)
        # last_marker is adjusted to cut one more line
        # off because the last line for pagination is
        # '--More--'
        last_marker = len(lines) - 2
        first_marker+=1

    complete_lines = lines[first_marker+2:last_marker-1]

    #SPECIAL-CASE: no completion options or only one option
    if not complete_lines:
        # NOTE:
        #   if there is only one option, readline simply applies it,
        #   which affects the current line in place.  apparently this
        #   results in tons of control-characters being dumped onto
        #   the line, and we have to clean those up for the output
        the_line = lines[first_marker+1:last_marker][0]
        the_line = remove_control_characters(unicode(the_line))
        tmp = the_line[the_line.find(to_complete)+len(to_complete):-4]
        result=to_complete.split()[-1]+tmp
        if '#' in result:
            # this seems to only happen for directories.  not sure why
            result = result[:result.find('#')]
        if result == to_complete.split()[-1]:
            #SPECIAL-CASE: no completion options at all.
            return []
        return [result]
    else:
        # there are multiple completion options
        completion_choices_by_row = [x.split() for x in complete_lines]
        completion_choices = reduce(lambda x,y:x+y, completion_choices_by_row)
        return completion_choices

if __name__=='__main__':
    # if being called from the command line, output json
    # so it is easier for another application to consume
    import json
    result = complete(sys.argv[-1])
    print json.dumps(result)
