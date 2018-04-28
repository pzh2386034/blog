#!/usr/bin/python
# -*- coding: utf-8 -*-
######################################################################
# Purpose:    calculate UT coverage of git commits' new code
# Useage:    ./ut_incremental_check.py
# Version:    Initial    Version    by wahaha02
######################################################################

__version__ = 'V1.0'
__author__ = 'panzehua'
__date__ = '2017-05-19'
__doc__ = '''
PURPOSE:
calculate UT coverage of git commits' new code

USAGE:
./ut_incremental_check.py  <monitor_c_files> <lcov_dir> <threshold>
example: 
./ut_incremental_check.py  '["source/soda/sp/lssp/i2c-v2/ksource"]' "coverage" 0.6

WORK PROCESS:
get changed file list between <since> and <until> , filter by <monitor_c_files> options;
get changed lines per changed file;
based on <lcov_dir>, search .gcov.html per file, and get uncover lines;
create report file:ut_incremental_check_report.html and check <threshold> (cover lines/new lines).

UT:
./ut_incremental_check.py ut
'''

__todo__ = '''
TODO LIST:
    1. support svn
    2. refactory html report by django web template
    3. add commit info in html report
    4. prompt user/commit/date info when mouse point to uncovered line
    5. ...
'''

from xml.etree.ElementTree import ElementTree,Element  
import sys, os, re
import json
import commands
from HTMLParser import HTMLParser
from pprint import *
from xml.etree.ElementTree import fromstring, ElementTree, Element
 
DEBUG = 0

def modifyXML(total_line, cov_line, module):
    tree = ElementTree()
    path = os.path.join(os.getcwd(), module, "lcov.xml")
#    path = "tmp/lcov.xml"
    tree.parse(path)
    root = tree.getroot()
    element_cov = Element("incre-coverage-line")
    element_cov.text = str(cov_line)
    element_tol = Element("incre-total-line")
    element_tol.text = str(total_line)
    root.append(element_tol)
    root.append(element_cov)
    tree.write(path, encoding="utf-8", xml_declaration=True)  

class GcovHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.uncovers = []
        self.covers = []
        self.islineNum = False
        self.lineNum = 0

    def handle_starttag(self, tag, attrs):
        if tag == "span":
            for a in attrs:
                if a == ('class', 'lineNum'):
                    self.islineNum = True
                if a == ('class', 'lineNoCov'):
                    self.uncovers.append(self.lineNum)
                if a == ('class', 'lineCov'):
                    self.covers.append(self.lineNum)
                    
    def handle_data(self, data):
        if self.islineNum:
            try:
                self.lineNum = int(data)
            except:
                self.lineNum = -1
            
    def handle_endtag(self, tag):
        if tag == "span":
            self.islineNum = False
    
class UTCover(object) :
    def __init__(self,  monitor, lcov_dir, thresh, module) :
        #self.since, self.until = since_until.split('..')
	self.since = "origin/master"
	status, sha_id = commands.getstatusoutput("git log --format='%H' -n 1")
	self.until = sha_id
        self.monitor = json.loads(monitor)
        self.lcov_dir = lcov_dir
        self.thresh = float(thresh)
	self.module = module
        
    def get_src(self):
        # self.since, self.until, self.monitor
        satus, output = commands.getstatusoutput("git diff --name-only %s %s" %(self.since, self.until))
        src_files = [f for f in output.split('\n') 
                        for m in self.monitor if m in f 
                        if os.path.splitext(f)[1][1:] in ['c', 'cpp'] and os.path.split(f)[1][-5:] not in ['T.cpp'] ]
        if DEBUG: pprint(src_files)
        return src_files
    
    def get_change(self, src_files):
        # self.since, self.until
        changes = {}
        for f in src_files:
            status, sha_id = commands.getstatusoutput("git log --format='%H' -n 1")
            if status:
                print "get sha_id failed, %s" %(status)
                sys.exit(1)
            #satus, output = commands.getstatusoutput("git log --oneline %s..%s %s | awk '{print $1}'" %(self.since, self.until, f))
	    #pprint(f)
	    file = f
	    #dir, file = os.path.split(f)
            satus, output = commands.getstatusoutput("git log --oneline origin/master..%s %s | awk '{print $1}'" %(sha_id, file))
            if status:
                print "get diff failed.retcode(%s)"  %(status)
                sys.exit(1)
            commits = output.split('\n')
	    #pprint(commits)
            cmd = "git blame --line-porcelain %s | grep -E '(%s)' | awk '{print $3}'" %(file, '|'.join(commits))
            satus, lines = commands.getstatusoutput(cmd)
            if status:
                print "get diff lines error, retcode(%s)" %(status)
                sys.exit(1)
            changes[f] = [ int(i) for i in lines.split('\n') if i.isdigit() ]

            
        if DEBUG: pprint(changes)
        return changes
    
    def get_ghp(self, f):
	#gcovfile =  + '.gcov.html'
	dir, f = os.path.split(f)
        gcovfile = os.path.join(self.lcov_dir, f + '.gcov.html')
	if not os.path.isfile(gcovfile):
	    print "file(%s) is not exit, when parse lcov" %(gcovfile)
	    sys.exit(1)
        if not os.path.exists(gcovfile):
            return None
            
        ghp = GcovHTMLParser()
        ghp.feed(open(gcovfile, 'r').read())

        return ghp
            
    def get_lcov_data(self, changes):
        # self.lcov_dir
        uncovers = {}
        lcov_changes = {}
        for f, lines in changes.items():
	    #f = os.path.split(f)[1]
            ghp = self.get_ghp(f)
            if not ghp:
                uncovers[f] = lines
                lcov_changes[f] = lines
                continue
        
            if DEBUG: print f, ghp.uncovers, ghp.covers, lines
            lcov_changes[f] = sorted(list(set(ghp.uncovers + ghp.covers) & set(lines)))
            uncov_lines = list(set(ghp.uncovers) & set(lines))
            if len(uncov_lines) != 0:
                uncovers[f] = sorted(uncov_lines)
            ghp.close()    
        
        return lcov_changes, uncovers
    
    def create_uncover_trs(self, uncovers):
        tr_format = '''
    <tr>
      <td class="coverFile"><a href="%(file)s.gcov.html">%(file)s</a></td>
      <td class="coverFile">%(uncov_lines)s </td>
    </tr>
    
        '''
        trs = ''
        for f,v in uncovers.items():
            gcovfile = os.path.join(self.lcov_dir, f + '.gcov.html')
            if os.path.exists(gcovfile):
                s = ''
                p = re.compile(r'^<span class="lineNum">\s*(?P<num>\d+)\s*</span>')
                for line in open(gcovfile, 'r').readlines():
                    ps = p.search(line)
                    if ps:
                        s += '<a name="%s">' %ps.group('num') + line + '</a>'
                    else:
                        s += line
                open(gcovfile, 'w').write(s)    

            data = {'file':f, 'uncov_lines':
                ", ".join(['<a href="%s.gcov.html#%d">%d</a>' %(f, i, i) for i in v])}
            trs += tr_format %data
            
        return trs
        
    def create_report(self, changes, uncovers):
        change_linenum, uncov_linenum = 0, 0
        for k,v in changes.items():
            change_linenum += len(v)
        for k,v in uncovers.items():
            uncov_linenum += len(v)
        
        cov_linenum = change_linenum - uncov_linenum
        coverage = round(cov_linenum * 1.0 / change_linenum 
                            if change_linenum > 0 else 1, 4)
        
        template = open('ut_incremental_coverage_report.template', 'r').read()
        data = {    'cov_lines':cov_linenum,
                    'change_linenum':change_linenum,
                    'coverage': coverage * 100,
                    'uncover_trs': self.create_uncover_trs(uncovers)}
	modifyXML(change_linenum, cov_linenum, self.module)
	print "=============================================increment coverage========================================================"
	print "                                                                                                                          "
	print "                                          total change: %d                                                                " %(change_linenum)
	print "                                          uncover change: %d                                                              " %(uncov_linenum)
	print "                                          cover change: %d                                                                " %(cov_linenum)
	print "                                          coverage rate: %0.2f%%                                                          " %(coverage*100)
	print "                                          threshold rate: %0.2f%%                                                         " %(self.thresh*100)
	print "                                                                                                                          "
	print "=============================================increment coverage========================================================"
        open(os.path.join(self.lcov_dir, 'ut_incremental_coverage_report.html'),
            'w').write(template %data)    
        
        return coverage
    
    def check(self):
        # main function
        src_files = self.get_src()
        changes = self.get_change(src_files)
        lcov_changes, uncovers = self.get_lcov_data(changes)
	coverage_ut = self.create_report(lcov_changes, uncovers)

        return 0 if coverage_ut >= self.thresh else 1
        
if len(sys.argv) == 1:
    print __doc__
    sys.exit(0)
if sys.argv[1] == 'ut':
    monitor, lcov_dir, threshold = ['["source/soda/sp/lssp/i2c-v2/ksource"]', "coverage", 0.8]
    test1 = ["b2016fdb..11440652", monitor, lcov_dir, threshold]
    if DEBUG: print "test1: ", test1
    ut = UTCover(*test1)
    src_files = ut.get_src()
    assert(src_files == [])
    changes = ut.get_change(src_files)
    assert(changes == {})
    lcov_changes, uncovers = ut.get_lcov_data(changes)
    assert(uncovers == {})
    rate = ut.create_report(changes, uncovers)
    assert(rate == 1)
    assert(ut.check() == 0)
    
    test2 = [
        "227b03259b33360e2309274f3927c38457d84dd3..79196baabed99661bd31a201ead6764f23a2884c", 
        monitor, lcov_dir, threshold]
    if DEBUG: print "test2: ", test2
    ut = UTCover(*test2)
    src_files = ut.get_src()
    assert(src_files == ['source/soda/sp/lssp/i2c-v2/ksource/bsp_i2c_dev.c', 'source/soda/sp/lssp/i2c-v2/ksource/chips/bsp_i2c_cfcuctrl.c', 'source/soda/sp/lssp/i2c-v2/ksource/chips/bsp_i2c_opt.c', 'source/soda/sp/lssp/i2c-v2/ksource/chips/bsp_i2c_pcie.c'])
    changes = ut.get_change(src_files)
    assert(changes ==  {'source/soda/sp/lssp/i2c-v2/ksource/chips/bsp_i2c_pcie.c': [78], 'source/soda/sp/lssp/i2c-v2/ksource/chips/bsp_i2c_cfcuctrl.c': [56, 57, 58, 59, 60, 130, 131, 132], 'source/soda/sp/lssp/i2c-v2/ksource/chips/bsp_i2c_opt.c': [68, 69, 115, 118, 124, 125, 126, 454, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 471, 721], 'source/soda/sp/lssp/i2c-v2/ksource/bsp_i2c_dev.c': [494, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652]})
    lcov_changes, uncovers = ut.get_lcov_data(changes)
    assert( lcov_changes == {'source/soda/sp/lssp/i2c-v2/ksource/chips/bsp_i2c_pcie.c': [78], 'source/soda/sp/lssp/i2c-v2/ksource/chips/bsp_i2c_cfcuctrl.c': [56, 57, 58, 59, 60, 130, 131, 132], 'source/soda/sp/lssp/i2c-v2/ksource/chips/bsp_i2c_opt.c': [125, 459, 461, 462, 471], 'source/soda/sp/lssp/i2c-v2/ksource/bsp_i2c_dev.c': [496, 498, 502, 503, 504, 625, 629, 630, 631, 633, 634, 636, 638, 639, 643, 644, 649, 650]}) 
    assert(uncovers == {'source/soda/sp/lssp/i2c-v2/ksource/chips/bsp_i2c_pcie.c': [78], 'source/soda/sp/lssp/i2c-v2/ksource/chips/bsp_i2c_cfcuctrl.c': [56, 57, 58, 59, 60, 130, 131, 132], 'source/soda/sp/lssp/i2c-v2/ksource/chips/bsp_i2c_opt.c': [125, 471], 'source/soda/sp/lssp/i2c-v2/ksource/bsp_i2c_dev.c': [502, 503, 504, 643, 644]})
    rate = ut.create_report(changes, uncovers)
    assert(0.8 > rate > 0.6)
    assert(ut.check() == 1)
    
    test3 = ['d98b93e705a227389e7cdc4b43252f4194a6cb7a..e8876ff5fe8ee0e61865315a67bd395f5d7f63f7 ',
            monitor, lcov_dir, threshold]
    if DEBUG: print "test3: ", test3
    ut = UTCover(*test3)
    assert(ut.check() == 0)    
    
    sys.exit(0)
    
ret = UTCover(*sys.argv[1:]).check()
sys.exit(ret)
