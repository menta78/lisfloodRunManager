"""
  DOCS
    only 3 entries are called from lisflood:
      MasterInfo for --listoptions
      ScriptGenerator( LFSettingsFile,MasterCode)
      writeScript(ScriptOut) of ScriptGenerator
    in addition one can set dtdDirectory if you want
     the DTD's (lisflood.dtd and pcraster.dtd) in a single
     place on the system (Recommended)
     for example, in lisflood.py CW put:
      validate.dtdDirectory = LF_Path

     PB 16/09/2009
     - changed variable with to con  in line 74
       to be in line with Python 2.6
     - change line 400:  def allText(l)  to
       line 493 inside class ScriptGenerator
       def allText(self,l):
       to use the possibility of nested options 
       
     PB 16/03/2009
     - add  def Calendar(self):
       instead of the CalendarDayStart as day of year
       it is possible to set a starting date like 31.12.1989
       This date is translated to day of year in the PcRaster script
       Format of date must be day/month/year, and it must be another seperator than space 
       e.g. 20/12/2008 but doesnt matter if it is 20-12.8 or 20.12.08
"""
# hack set to 1 exclude validating pyXml
skipCheck=1


# base imports
import xml.dom.minidom
from xml.sax.handler import ContentHandler
from xml.sax.handler import EntityResolver
import os.path
import xml.sax
import string
import time,datetime

# imports needed to get a validating parser
#  unsure if these are standard in python packages or do
#  we need PyXML installed (http://pyxml.sourceforge.net/)
# python2.4-xml - XML tools for Python (2.4.x)
#  interestng xmldiff in python section



"""
 TODO
 1) not really only a validator it also collects all data
 2) the single ContentHandler is able to do both settings and master
      maybe in the future not a good idea for clearity
 3) issue warning if a lfuser/textvar is never used
 4) now still using 2 parsers in parse(), see notes there
 5) find DTD by Catalog setting, otherwise it must live in current directory
"""


# used as exception identifier
Error='ValidationError'


# set to path of directory where parsing
# want's a DTD found
dtdDirectory=""


class TextVar:
  """ What we want to know about a textvar element """
  def __init__(self,name,value):
    self.d_name     = name
    self.d_value    = value
    # set in addTextVarCommon
    self.d_firstDef ="unknown"
    # set in addTextVarCommon
    self.d_seqNr = -1
  # do you think my shoes are made of leather
  def substitute(self,varDict):
    # allow multiple substitions
    somethingChanged=1
    while somethingChanged:
     somethingChanged=0
     for i in varDict.keys():
       dollar="$(%s)" % varDict[i].d_name
       con  = varDict[i].d_value
       new   = self.d_value.replace(dollar,con)
       if new != self.d_value:
          self.d_value=new
          somethingChanged=1
    # $'s left!
    if self.d_value.find("$") != -1:
      raise Error, "'%s' has unknown textvar-$ constructs" % self.d_value


  def modelBinding(self):
    """ return as model binding statement with ; """
    name = self.d_name
    v = self.d_value
    #if name == "CalendarDayStart":
    #  v = "333"
    try:
     float(v)
    except ValueError:
     if v[0]!="\"":
      # not already quoted
      v = "\"%s\"" % v
    v = v.replace("\\","/")
    return "%s=%s;" % (self.d_name,v)


  def Calendar(self):
    if self.d_name == "CalendarDayStart":
      v = self.d_value
      try:
        float(v)
      except ValueError:
        d=v.replace('.','/')
        d=d.replace('-','/')
        self.d_value = d
        year=d.split('/')[-1:]
        if len(year[0])==4: formatstr="%d/%m/%Y"
        else: formatstr="%d/%m/%y"
        if len(year[0])==1:
          d=d.replace('/','.',1)
          d=d.replace('/','/0')
          d=d.replace('.','/')
        date=datetime.date(*time.strptime(d,formatstr)[0:3])
        self.d_value=str(int(date.strftime("%j")))


class Option:
  """ What we want to know about an lfoption element
  """
  def __init__(self,name):
    self.d_name     = name
    # if empty we do mean no choice is made by
    # default, all lfoption with that name are
    #  excluded
    # WARNING in the xml default is an 0/1 on/off value
    #         d_default is simply one of the d_choices
    #          values, or another if none of the d_choices
    #          is selected. A bit confusing
    self.d_default  = ""
    self.d_choices  = [ ]
    # park info from setoption element here
    self.d_setOption  = ""


  def info(self):
      """ info for list options option"""
      default = "noDefault"
      if len(self.d_default):
        default = "default=%s" % self.d_default
      return "%s choices=(%s) %s" % (self.d_name,string.join(self.d_choices,","),default)


  def set(self,attr):
    assert attr["name"] == self.d_name
    # this choice is the default
    if attr["default"] == "1":
      if self.d_default == "":
         self.d_default = attr["choice"]
      else:
         if self.d_default != attr["choice"]:
           raise Error, "previous default was '%s'" % self.d_default
    if attr["choice"] not in self.d_choices:
       self.d_choices.append(attr["choice"])


  # wrong see test Johan dynamicWave 30 june 2005
  # def selected(self,choice):
  #  assert choice in self.d_choices
  #  return choice == self.d_setOption or choice == self.d_default


  def selected(self,choice):
    assert choice != ""
    assert choice in self.d_choices
    if self.d_setOption == "":
      return choice == self.d_default
    return choice == self.d_setOption


class FindDTD(EntityResolver):
  def resolveEntity(self,publicId, systemId):
    """ try find DTD somewhere else if needed """
    if os.path.exists(systemId):
      return systemId
    tried = [ systemId ]
    if len(dtdDirectory):
      p=os.path.abspath(os.path.join(dtdDirectory,systemId))
      tried.append(p)
      if os.path.exists(p):
        return p
    if os.environ.has_key('PCRTREE'):
      # CW for PCRaster team test
      p=os.path.join(os.environ['PCRTREE'],"template","xml",systemId)
      tried.append(p)
      if os.path.exists(p):
        return p
    raise Error, "DTD not found, tried %s" % string.join(tried,",")


class BaseHandler(ContentHandler):
    def __init__(self,documentElementNameExpected=""):
      """ if documentElementNameExpected not empty then
          check as validation"""
      ContentHandler.__init__(self)
      self.d_documentNameElementExpected = documentElementNameExpected
      self.d_documentNameElementParsed = 0
      self.d_locator=None


      self.d_userTextVars = { }
      self.d_bindings = { }
      self.d_currentTextVars = self.d_userTextVars
      # options as found in the lfmodule elements
      self.d_options = { }
      # d_setOptions as found in lfoptions of settings file
      #  simple dictionary [name] = choice
      self.d_setOptions = { }
      # empty string means not in prolog
      self.d_prolog = ""


    def addTextVarCommon(self,newTextVar):
      """ common code for addTextVar and addProlog 
          error message for prolog is a bit off since it has
          no value attribute
      """
      newTextVar.d_firstDef= \
         "%s:%s" % (self.d_locator.getLineNumber(),self.d_locator.getColumnNumber())
      newTextVar.d_seqNr= len(self.d_currentTextVars)
      # do $-substitutions
      if self.d_currentTextVars == self.d_bindings:
        try:
         newTextVar.substitute(self.d_userTextVars)
         
         newTextVar.Calendar()
         
        except  Error, msg:
         self.attrError("value",msg)
      self.d_currentTextVars[newTextVar.d_name] = newTextVar


    def addTextVar(self,attr):
      name=attr["name"]
      # in both user and binding each name must be unique
      if self.d_currentTextVars.has_key(name):
        firstDef=self.d_currentTextVars[name]
        self.attrError("name","redefinition first at line:col %s" % firstDef.d_firstDef)
      self.addTextVarCommon(TextVar(name,attr["value"]))



    def addProlog(self, contents):
      """@prolog is a special d_bindings dictionary node.
         This special node with the name @prolog is
         to put the whole prolog in. The name @prolog is unique since @ is not
         accepted in pcrcalc as a valid identifiers"""
      self.addTextVarCommon(TextVar("@prolog",contents))
      # check if result contents after ($-stuff) has areamap and timer
      b= self.d_currentTextVars["@prolog"].d_value
      if b.find("areamap") == -1 or b.find("timer") == -1:
        self.error("prolog contents does not has an areamap and timer section")


    def addOption(self, attr):
      try:
       if not self.d_options.has_key(attr["name"]):
         self.d_options[attr["name"]] = Option(attr["name"])
       self.d_options[attr["name"]].set(attr)
      except Error, msg:
       # FTTB only error possible
       self.attrError("default",msg)


    def error(self,msg):
      raise xml.sax.SAXParseException(msg,Error,self.d_locator)
    def attrError(self,attrName,msg):
      self.error("attribute '%s': %s" % (attrName,msg))


    # the events called from parser
    def setDocumentLocator(self,locator):
      self.d_locator=locator


    def startElement(self, name, attr):
      # verify no attributes have an empty value
      for i in attr.items():
         if not len(i[1]):
            self.attrError(i[0],"empty attribute value not allowed")
      # check if expected document
      if not self.d_documentNameElementParsed:
        self.d_documentNameElementParsed=1
        if len(self.d_documentNameElementExpected):
         if self.d_documentNameElementExpected != name:
           self.error("expected '%s' as documentElement got '%s'" % \
            (self.d_documentNameElementExpected,name))


      if name == "textvar":
         self.addTextVar(attr)
      elif name == "setoption":
         self.d_setOptions[attr["name"]]=attr["choice"]
      elif name == "lfbinding":
         self.d_currentTextVars = self.d_bindings
      elif name == "prolog":
         # markStart
         self.d_prolog = " "
      elif name == "lfoption":
         self.addOption(attr)


    def endElement(self, name):
      if name == "prolog":
         # slice of the first markStart
         self.addProlog(self.d_prolog[1:])


    def characters(self, str):
      if len(self.d_prolog):
        self.d_prolog+=str


def check(fileName):
 """ check syntax of file acording to DTD"""
 if not skipCheck:
  try:
      # validating parser
      import xml.sax.sax2exts
      vp = xml.sax.sax2exts.XMLValParserFactory.make_parser()
      vp.setEntityResolver(FindDTD())
      vp.parse(fileName)
  except xml.sax.SAXParseException, exception:
      # explicit convert exception to string
      raise Error, ("%s" % exception)


def parse(fileName,docEl=""):
  """never call from outside except in unit test"""
  try:
      # we do it in two parsers, since the stock PyXML
      #  xmlproc validating parser has a bug in not setting
      #  setDocumentLocator, patch available in newsgroup


      check(fileName)


      # semantic parser and data collector
      sp = xml.sax.make_parser()
      handler = BaseHandler(docEl)
      sp.setContentHandler(handler)
      sp.setEntityResolver(FindDTD())
      sp.parse(fileName)


      return handler


  except xml.sax.SAXParseException, exception:
      # explicit convert exception to string
      raise Error, ("%s" % exception)


class SettingsInfo:
  """ validate settings xml and return 
      setOptions(),bindings() and prolog()"""
  def __init__(self,settingsFile,full=0):
    """will raise validate.Error in case of error"""
    docEl=""
    if full: docEl="lfsettings"
    h = parse(settingsFile,docEl)
    self.d_setOptions = h.d_setOptions
    # turn dictionary into list and find prolog
    self.d_bindings= []
    self.d_prolog=""
    for i in h.d_bindings.items():
      if i[0] == "@prolog":
        self.d_prolog=i[1].d_value
      else:
        self.d_bindings.append(i[1])
    def cmpSeqNr(e1,e2):
      return cmp(e1.d_seqNr,e2.d_seqNr)
    self.d_bindings.sort(cmpSeqNr)


  # dictionary of [name]=choice from setoption elements
  def setOptions(self):
    return self.d_setOptions
  def bindings(self):
    """list of TextVar objects in order of definition in lfbinding
       and all substitutions from user section already done"""
    return self.d_bindings
  def prolog(self):
    return self.d_prolog


class MasterInfo:
  """ validate master xml and return options() """
  def __init__(self,masterFile,full=0):
    """will raise validate.Error in case of error"""
    docEl=""
    if full: docEl="lisflood"
    h = parse(masterFile,docEl)
    self.d_options = h.d_options
  def setSetOptions(self, setOptions):
    """update options with setOptions from settings file
       may raise Error(name) with name of setoption not present
    """
    for name in setOptions.keys():
      if not self.d_options.has_key(name):
        raise Error, name
      self.d_options[name].d_setOption = setOptions[name]
  def options(self):
    """dictionary with lfoption:@name as index and Option object as value
        retrieved from all lfoption elements found"""
    return self.d_options


def forEachNode(n, o):
 o(n)
 for  c in n.childNodes:
    forEachNode(c,o)


def forEachElement(e, o):
 o(e)
 for  c in e.childNodes:
  if c.nodeType == c.ELEMENT_NODE:
    forEachElement(c,o)



class Strip:
  """ strip all
        - whitespace only nodes and comments
        - comments and processing instructions
  """
  def __call__(self,e):
   # make a copy since we change the list in the loop
   l = e.childNodes[:]
   for c in l:
    if c.nodeType in [ c.TEXT_NODE,  c.CDATA_SECTION_NODE]:
       if not len(c.nodeValue.strip()):
         e.removeChild(c)
    if c.nodeType in [ c.COMMENT_NODE,  c.PROCESSING_INSTRUCTION_NODE]:
        e.removeChild(c)


class XmlToAscii:
  """ strip dataEnvelop's raise Error if encoded"""
  def __init__(self):
    self.d_ascii=""
  def __call__(self,n):
    if n.nodeType in [ n.TEXT_NODE,  n.CDATA_SECTION_NODE]:
       self.d_ascii += n.nodeValue
    if n.nodeName == "dataEnvelop":
       assert n.getAttribute("encoding") != "pcrseal"


class PcrXmlScript:
    """ xml scripts recognized by pcrcalc """
    def __init__(self,masterFile):
     self.d_doc = xml.dom.minidom.parseString(
            """<?xml version="1.0" encoding="ISO-8859-1"?>
               <!DOCTYPE runTimeSeal PUBLIC '-//PCRaster//Generic//' 'pcraster.dtd'>
               <runTimeSeal xmlns='http://www.pcraster.nl/xml'
                            version='1' fromPublicFile='%s'/>""" % masterFile)
     self.d_docEl = self.d_doc.documentElement


    def dom(self):
      return self.d_doc


    def add(self,contents,encoding):
      """ add dataEnvelop iff contents is not empty
           encoding if empty then default text      """
      if not len(contents):
        return
      d = self.d_doc.createElement("dataEnvelop");
      c = self.d_doc.createTextNode(contents+"\n");
      d.appendChild(c)
      if not len(encoding):
        encoding="text"
      assert encoding in [ "text", "pcrseal" ]
      d.attributes["encoding"] = encoding
      self.d_docEl.appendChild(d)



class ScriptGenerator:
  def __init__(self,settingsFile,masterFile,full=1):
    """will raise validate.Error in case of error"""
    self.d_settingsInfo = SettingsInfo(settingsFile,full)
    self.d_masterInfo   = MasterInfo(masterFile,full)
    self.d_masterDom    = xml.dom.minidom.parse(masterFile)
    self.d_masterFileName = masterFile
    forEachElement(self.d_masterDom, Strip())


    # put setoption things into Option's of MasterInfo
    try:
     self.d_masterInfo.setSetOptions(self.d_settingsInfo.setOptions())
    except Error, name:
       raise Error, "setoption '%s' from '%s' not present in '%s'" % \
             (name,settingsFile,masterFile)


  def __del__(self):
    self.d_masterDom.unlink()


  def docEl(self):
    return self.d_masterDom.documentElement


  def isSealed(self,dom):
    for d in dom.getElementsByTagName("dataEnvelop"):
      if d.getAttribute("encoding") == "pcrseal":
        return 1;
    return 0

  def allText(self,l):
    """ concat of all text children """
    textContents=""
    for c in l.childNodes:
     if c.nodeName == "lfoption":

      subtext=self.selectOption(c)
      #  name = c.attributes["name"].value
      #  choice = c.attributes["choice"].value
      #  subtext=""
      #  for subc in c.childNodes:
      #    if self.d_masterInfo.d_options[name].selected(choice):
      #      subtext += subc.nodeValue
      textContents += subtext
        
     else:
       if c.nodeType in [ c.TEXT_NODE,  c.CDATA_SECTION_NODE]:
         textContents += c.nodeValue
    return textContents



  def selectOption(self, l):
    assert l.nodeName == "lfoption"
    name   = l.attributes["name"].value
    choice = l.attributes["choice"].value
    if self.d_masterInfo.d_options[name].selected(choice):
      return self.allText(l)
    return ""
  def processModule(self, script,m):
    for c in m.childNodes:
      if c.nodeName == "lfoption":
        script.add(self.selectOption(c),c.getAttribute("encoding"))
      else:
        assert c.nodeName in [ "#cdata-section", "#text" ]
        script.add(c.nodeValue,m.getAttribute("encoding"))


  def resultXmlScript(self):
    """ create xml script from possible sealed (public) masterFile
         this will create an xml file with runTimeSeal as document element
    """
    # create the result
    script = PcrXmlScript(self.d_masterFileName)


    # front matter before initial
    front = [ "binding" ]
    for b in self.d_settingsInfo.bindings():
      front.append(b.modelBinding())
    # areamap / timer
    front.append(self.d_settingsInfo.prolog())
    script.add(string.join(front,"\n"),"text");


    moduleList   = self.d_masterDom.getElementsByTagName("lfmodule")
    sectionOrder = [ "initial", "dynamic" ]
    for s in sectionOrder:
      # section name
      script.add(s,"text")
      for m in moduleList:
        # find initial or dynamic (s) within lfmodule (m)
        mbl=m.getElementsByTagName(s)
        assert len(mbl) < 2
        if len(mbl):
           self.processModule(script,mbl[0])
    return script.dom()


  def resultAsciiScript(self):
    """ create ascii script from non sealed masterFile """
    # simply create an resultXmlScript() select it's textNode's
    xmlDom = self.resultXmlScript()
    if self.isSealed(xmlDom):
     raise Error, \
        "pcrseal input (encoding=pcrseal) illegal when using resultAsciiScript()"
    xmlToAscii = XmlToAscii()
    forEachNode(xmlDom,xmlToAscii)
    return xmlToAscii.d_ascii


  def writeScript(self, scriptFileName):
    xmlDom = self.resultXmlScript()
    if self.isSealed(xmlDom):
      contents= xmlDom.toxml()
    else:
      contents = self.resultAsciiScript()
    open(scriptFileName,"w").write(contents)
