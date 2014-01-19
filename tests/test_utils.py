#!/usr/bin/env python

"""
test pox's higher-level shell utilities
"""
import os

def test():
    '''test(); script to test all functions'''
    from pox import pattern, getvars, expandvars, convert, replace, \
                    index_join, findpackage, remote, parse_remote, \
                    select, selectdict, env, homedir, username

   #print('testing pattern...')
    assert pattern(['PYTHON*','DEVELOPER']) == 'PYTHON*;DEVELOPER'
    assert pattern([]) == ''

   #print('testing getvars...')
    bogusdict = {'PYTHIA_STUFF':'${DV_DIR}/pythia-${PYTHIA_VERSION}/stuff',
                 'MIKE_VERSION':'1.0','MIKE_DIR':'${HOME}/junk',
                 'DUMMY_VERSION':'6.9','DUMMY_STUFF':'/a/b',
                 'DV_DIR':'${HOME}/dev', 'PYTHIA_VERSION':'0.0.1'}
    home = homedir()
    assert getvars(home) == {}
    d1 = {'DV_DIR': '${HOME}/dev', 'PYTHIA_VERSION': '0.0.1'}
    d2 = {'MIKE_DIR': '${HOME}/junk'}
    assert getvars('${DV_DIR}/pythia-${PYTHIA_VERSION}/stuff',bogusdict) == d1
    assert getvars('${MIKE_DIR}/stuff',bogusdict) == d2
    assert getvars('${HOME}/stuff') == {'HOME': homedir()}

   #print('testing expandvars...')
    assert expandvars(home) == homedir()
    x = '${ASDFQWEGQVQEGQERGQEVQEEEVCQERGWEGWEFGW}/stuff'
    assert expandvars(x) == x
    x = '${HOME}/junk/${HOME}/dev/stuff'
    assert expandvars('${MIKE_DIR}/${DV_DIR}/stuff',bogusdict) == x
    assert expandvars('${DV_DIR}/${PYTHIA_VERSION}',secondref=bogusdict) == \
           expandvars('${DV_DIR}/${PYTHIA_VERSION}',bogusdict,os.environ)
    assert expandvars('${HOME}/stuff') == ''.join([homedir(), '/stuff'])

   #print('testing convert...')
    source = 'test.txt'
    f = open(source,'w')
    f.write('this is a test file.'+os.linesep)
    f.close()
    assert convert(source,'mac',verbose=False) == convert(source,verbose=False)
    assert convert(source,'foo',verbose=False) > 0

   #print('testing replace...')
    replace(source,{' is ':' was '})
    replace(source,{'\sfile.\s':'.'})
    f = open(source,'r')
    assert f.read() == 'this was a test.'
    f.close()
    os.remove(source)

   #print('testing index_join...')
    fl = ['begin ','hello ','world ','string ']
    assert index_join(fl,'hello ','world ') == 'hello world '

   #print('testing findpackage...')
    assert not findpackage('python','aoskvaosvoaskvoak',all=True,verbose=False)
    p = findpackage('lib/python*',env('HOME',all=False),all=False,verbose=False)
    if p: assert 'lib/python' in p

   #print('testing remote...')
    myhost = 'login.cacr.caltech.edu'
    assert remote('~/dev') == '~/dev'
    assert 'localhost' in remote('~/dev',loopback=True)
    thing = '@login.cacr.caltech.edu:~/dev'
    assert remote('~/dev',host=myhost,user=username()).endswith(thing)

   #print('testing parse_remote...')
    destination = 'danse@%s:~/dev' % myhost
    x = ('-l danse', 'login.cacr.caltech.edu', '~/dev')
    assert parse_remote(destination,login_flag=True) == x
    destination = 'danse@%s:' % myhost
    assert parse_remote(destination) == ('danse', 'login.cacr.caltech.edu', '')
    destination = '%s:' % myhost
    x = ('', 'login.cacr.caltech.edu', '')
    assert parse_remote(destination,login_flag=True) == x
    destination = 'test.txt'
    x = ('', 'localhost', 'test.txt')
    assert parse_remote(destination,loopback=True) == x

   #print('testing select...')
    test = ['zero','one','two','three','4','five','six','seven','8','9/81']
    assert select(test) == ['three', 'seven']
    assert select(test,minimum=True) == ['4', '8']
    assert select(test,reverse=True,all=False) == 'seven'
    assert select(test,counter='/',all=False) == '9/81'
    test = [[1,2,3],[4,5,6],[1,3,5]]
    assert select(test) == test
    assert select(test,counter=3) == [test[0], test[-1]]
    assert select(test,counter=3,minimum=True) == [test[1]]

   #print('testing selectdict...')
    x = {'MIKE_VERSION': '1.0', 'DUMMY_VERSION': '6.9'}
    assert selectdict(bogusdict,minimum=True) == x
    x = {'DUMMY_STUFF': '/a/b', 'PYTHIA_STUFF': '${DV_DIR}/pythia-${PYTHIA_VERSION}/stuff'}
    assert selectdict(bogusdict,counter='/') == x
    assert len(selectdict(bogusdict,counter='/',all=False)) == 1
    return

if __name__=='__main__':
    test()


# End of file 
