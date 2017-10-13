#!/usr/bin/env python
'''
Extracted manufacturer's data from JEP standard.

But...

Standard is in a PDF file, and extraction (with okular) is kind
of wonky.
'''

srcf = 'jep106af.txt'
dstf = '../../playtag/bsdl/data/manufacturers.txt'

header = '''
#
# Data extracted from JEDEC publication JEP106-AF
#
'''

def readdata(srcf=srcf):
    src = open(srcf, 'rb').read().splitlines()
    bank = 0
    current = 0
    mfgs = []
    for line in src:
        tokens = line.split()
        if not tokens:
            continue
        if tokens[0].isdigit():
            next = int(tokens[0])
            line = line[len(tokens[0]):].lstrip()
            if next < current or line:
                assert len(mfgs) == current + bank * 126, (len(mfgs), bank, current, mfgs[-4:-1])
            if next < current:
                assert next == 1, next
                bank += 1
            current = next
            if line:
                mfgs.append(line)
        else:
            assert len(mfgs) <= current + bank * 126, (len(mfgs), bank, current, mfgs[-4:-1])
            mfgs.append(line)
    return mfgs

def writedata(data, header=header, dstf=dstf):
    f = open(dstf, 'wb')
    print >> f, header
    for i, company in enumerate(data):
        bank, index = divmod(i, 126)
        code = bank * 128 + index + 1
        assert code & 0x7f not in (0, 0x7f)
        print >> f, '{0:011b}   {1}'.format(code, company)
    f.close()

if __name__ == '__main__':
    writedata(readdata())
