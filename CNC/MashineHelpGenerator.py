import machine

f = open("HelpMachine.txt", "w")

def printClassInfo(name, desc):
    print >> f, name
    for i in desc.__dict__:
        if list(i)[0]!='_': print >> f,'--------', i
    print >> f, '\n\n'

d = machine.__dict__
for i in d:
    try:
        printClassInfo(i, d[i])
    except AttributeError:
        print >> f, 'Object has no attribute __dict__\n\n'
