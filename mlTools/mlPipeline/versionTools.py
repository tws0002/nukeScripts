# Copyright (c) 2009 The Foundry Visionmongers Ltd.  All Rights Reserved.

import nuke
import os.path
import re

def version_get(string, prefix, suffix = None):
  """Extract version information from filenames used by DD (and Weta, apparently)
  These are _v# or /v# or .v# where v is a prefix string, in our case
  we use "v" for render version and "c" for camera track version.
  See the version.py and camera.py plugins for usage."""

  if string is None:
    raise ValueError, "Empty version string - no match"
  
  regex = "[/_.]"+prefix+"\d+"
  matches = re.findall(regex, string, re.IGNORECASE)
  if not len(matches):
    msg = "No \"_"+prefix+"#\" found in \""+string+"\""
    raise ValueError, msg
  return (matches[-1:][0][1], re.search("\d+", matches[-1:][0]).group())

def version_set(string, prefix, oldintval, newintval):
  """Changes version information from filenames used by DD (and Weta, apparently)
  These are _v# or /v# or .v# where v is a prefix string, in our case
  we use "v" for render version and "c" for camera track version.
  See the version.py and camera.py plugins for usage."""

  regex = "[/_.]"+prefix+"\d+"
  matches = re.findall(regex, string, re.IGNORECASE)
  print matches
  if not len(matches):
    return ""

  # Filter to retain only version strings with matching numbers
  matches = filter(lambda s: int(s[2:]) == oldintval, matches)

  # Replace all version strings with matching numbers
  for match in matches:
    # use expression instead of expr so 0 prefix does not make octal
    fmt = "%%(#)0%dd" % (len(match) - 2)
    newfullvalue = match[0] + prefix + str(fmt % {"#": newintval})
    string = re.sub(match, newfullvalue, string)
  return string

def version_up():
  """All new version_up that uses the version_get/set functions.
  This script takes the render version up one in selected iread/writes."""
  
  n = nuke.selectedNodes()
  for i in n:
    _class = i.Class()
    # check to make sure this is a read or write op
    if _class == "Read" or _class == "Write" or _class == "Precomp":
      fileKnob = i['file']
      proxyKnob = i.knob('proxy')
      try:
        (prefix, v) = version_get(fileKnob.value(), 'v')
        v = int(v)
        fileKnob.setValue(version_set(fileKnob.value(), prefix, v, v + 1))
      except ValueError:
        # We land here if there was no version number in the file knob.
        # If there's none in the proxy knob either, just show the exception to the user.
        # Otherwise just update the proxy knob
        if proxyKnob and proxyKnob.value():
          (prefix, v) = version_get(proxyKnob.value(), 'v')
          v = int(v)
      
      if proxyKnob and proxyKnob.value():
        proxyKnob.setValue(version_set(proxyKnob.value(), prefix, v, v + 1))
      
      nuke.root().setModified(True) 

def version_down():
  """All new version_down that uses the version_get/set functions.
  This script takes the render version up one in selected iread/writes."""
  
  n = nuke.selectedNodes()
  for i in n:
    _class = i.Class()
    # check to make sure this is a read or write op
    if _class == "Read" or _class == "Write" or _class == "Precomp":
      fileKnob = i['file']
      proxyKnob = i.knob('proxy')
      try:
        (prefix, v) = version_get(fileKnob.value(), 'v')
        v = int(v)
        fileKnob.setValue(version_set(fileKnob.value(), prefix, v, v - 1))
      except ValueError:
        # We land here if there was no version number in the file knob.
        # If there's none in the proxy knob either, just show the exception to the user.
        # Otherwise just update the proxy knob
        if proxyKnob and proxyKnob.value():
          (prefix, v) = version_get(proxyKnob.value(), 'v')
          v = int(v)
      if proxyKnob and proxyKnob.value():
        proxyKnob.setValue(version_set(proxyKnob.value(), prefix, v, v - 1))
      nuke.root().setModified(True) 

def version_latest2():
  """All new version_down that uses the version_get/set functions.
  This script takes the render version up one in selected iread/writes."""
  
  n = nuke.selectedNodes()
  for i in n:
    _class = i.Class()
    # check to make sure this is a read or write op
    if _class == "Read":
      fileKnob = i['file']
      oVersion = fileKnob.value()
      lVersion = fileKnob.value()
      (prefix, v) = version_get(fileKnob.value(), 'v')
      print version_get(fileKnob.value(), 'v')
      v = int(v)
      for t in range(1,10):
        fileKnob.setValue(version_set(fileKnob.value(), prefix, v, v + t))
        if os.path.exists(fileKnob.evaluate()):
          lVersion = fileKnob.value()
          fileKnob.setValue(oVersion)
        if not os.path.exists(fileKnob.evaluate()):
          fileKnob.setValue(lVersion)
        


def version_latest():
  """Like version_up, but only goes up to the highest numbered version
  that exists.
  
  Works on all selected Read nodes, or all Read nodes if nothing is
  selected.
  
  Does not modify Write nodes."""
  print "test"
  class __KnobValueReplacer(object):
    def loop(self, knob):
      while True:
        print "loop"
        oVersion = knob.value()
        try:
          (prefix, v) = version_get(oVersion, 'v')
          v = int(v)
          nVersion = version_set(oVersion, prefix, v, v + 10)
          knob.setValue(nVersion)
          if os.path.exists(knob.evaluate()):
            print "found"
            return
          if not os.path.exists(knob.evaluate()):
            knob.setValue(oVersion)
          nuke.root().setModified(True) 
        
        except ValueError:
          pass
        try:
          (prefix, v) = version_get(oVersion, 'v')
          v = int(v)
          nVersion = version_set(oVersion, prefix, v, v + 9)
          knob.setValue(nVersion)
          if os.path.exists(knob.evaluate()):
            print "found"
            return
          if not os.path.exists(knob.evaluate()):
            knob.setValue(oVersion)
          nuke.root().setModified(True) 
        
        except ValueError:
          pass
        try:
          (prefix, v) = version_get(oVersion, 'v')
          v = int(v)
          nVersion = version_set(oVersion, prefix, v, v + 8)
          knob.setValue(nVersion)
          if os.path.exists(knob.evaluate()):
            print "found"
            return
          if not os.path.exists(knob.evaluate()):
            knob.setValue(oVersion)
          nuke.root().setModified(True) 
        
        except ValueError:
          pass
        try:
          (prefix, v) = version_get(oVersion, 'v')
          v = int(v)
          nVersion = version_set(oVersion, prefix, v, v + 7)
          knob.setValue(nVersion)
          if os.path.exists(knob.evaluate()):
            print "found"
            return
          if not os.path.exists(knob.evaluate()):
            knob.setValue(oVersion)
          nuke.root().setModified(True) 
        
        except ValueError:
          pass
        try:
          (prefix, v) = version_get(oVersion, 'v')
          v = int(v)
          nVersion = version_set(oVersion, prefix, v, v + 6)
          knob.setValue(nVersion)
          if os.path.exists(knob.evaluate()):
            print "found"
            return
          if not os.path.exists(knob.evaluate()):
            knob.setValue(oVersion)
          nuke.root().setModified(True) 
        
        except ValueError:
          pass
        try:
          (prefix, v) = version_get(oVersion, 'v')
          v = int(v)
          nVersion = version_set(oVersion, prefix, v, v + 5)
          knob.setValue(nVersion)
          if os.path.exists(knob.evaluate()):
            print "found"
            return
          if not os.path.exists(knob.evaluate()):
            knob.setValue(oVersion)
          nuke.root().setModified(True) 
        
        except ValueError:
          pass
        try:
          (prefix, v) = version_get(oVersion, 'v')
          v = int(v)
          nVersion = version_set(oVersion, prefix, v, v + 4)
          knob.setValue(nVersion)
          if os.path.exists(knob.evaluate()):
            print "found"
            return
          if not os.path.exists(knob.evaluate()):
            knob.setValue(oVersion)
          nuke.root().setModified(True) 
        
        except ValueError:
          pass
          
        try:
          (prefix, v) = version_get(oVersion, 'v')
          v = int(v)
          nVersion = version_set(oVersion, prefix, v, v + 3)
          knob.setValue(nVersion)
          if os.path.exists(knob.evaluate()):
            print "found"
            return
          if not os.path.exists(knob.evaluate()):
            knob.setValue(oVersion)
          nuke.root().setModified(True) 
        
        except ValueError:
          
          pass

        try:
          (prefix, v) = version_get(oVersion, 'v')
          v = int(v)
          nVersion = version_set(oVersion, prefix, v, v + 2)
          knob.setValue(nVersion)
          if os.path.exists(knob.evaluate()):
            print "found"
            return
          if not os.path.exists(knob.evaluate()):
            knob.setValue(oVersion)
            
          nuke.root().setModified(True) 
          
        except ValueError:
            pass
            
            
        try:
          (prefix, v) = version_get(oVersion, 'v')
          v = int(v)
          nVersion = version_set(oVersion, prefix, v, v + 1)
          knob.setValue(nVersion)
          if os.path.exists(knob.evaluate()):
            print "found"
            return
          if not os.path.exists(knob.evaluate()):
            knob.setValue(oVersion)
            return
          nuke.root().setModified(True) 
          
        except ValueError:
            return
          
  nodes = nuke.selectedNodes()
  if not nodes: nodes = nuke.allNodes()
  n = [i for i in nodes if i.Class() == "Read"]
  for i in n:
    __KnobValueReplacer().loop(i['file'])


def main():
    version_latest()