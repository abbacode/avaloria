"""
Evennia menu system. 

Contribution - Griatch 2011

This module offers the ability for admins to let their game be fully
or partly menu-driven. Menu choices can be numbered or use arbitrary
keys. There are also some formatting options, such a putting options
in one or more collumns. 

The menu system consists of a MenuTree object populated by MenuNode
objects. Nodes are linked together with automatically created commands
so the player may select and traverse the menu. Each node can display
text and show options, but also execute arbitrary code to act on the
system and the calling object when they are selected.

There is also a simple Yes/No function supplied. This will create a
one-off Yes/No question and executes a given code depending on which
choice was made.

To test, import and add the CmdTestMenu command to the end of the default cmdset in
game.gamesrc.commands.basecmdset. The test command is also a good
example of how to use this module in code.

"""
from src.commands.cmdhandler import CMD_NOMATCH, CMD_NOINPUT
from src.commands.command import Command
from src.commands.cmdset import CmdSet
from src.commands.default.general import CmdLook 
from src.commands.default.help import CmdHelp 
from src.utils import utils

# imported only to make them available during execution of code blocks
from src.objects.models import ObjectDB
from src.players.models import PlayerDB


#
# Commands used by the Menu system 
# 

class CmdMenuNode(Command):
    """
    Parent for menu selection commands. 
    """
    key = "selection"
    aliases = []
    locks = "cmd:all()"
    help_category = "Menu"

    menutree = None
    code = None 

    def func(self):
        "Execute a selection"
        if self.code:
            try:
                exec(self.code)
            except Exception, e:
                self.caller.msg("%s\n{rThere was an error with this selection.{n" % e)
        else:
            self.caller.msg("{rThis option is not available.{n")

class CmdMenuLook(CmdLook):
    """
    ooc look

    Usage:
      look

    This is a Menu version of the look command. It will normally show
    the options available, otherwise works like the normal look
    command..
    """
    key = "look"
    aliases = ["l", "ls"]
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "implement the menu look command"
        if self.caller.db._menu_data:
            # if we have menu data, try to use that. 
            lookstring = self.caller.db._menu_data.get("look", None)
            if lookstring:
                self.caller.msg(lookstring)
                return 
        # otherwise we use normal look 
        super(CmdMenuLook, self).func()

class CmdMenuHelp(CmdHelp):
    """
    help 

    Usage:
      help

    Get help specific to the menu, if available. If not,
    works like the normal help command. 
    """
    key = "help"
    aliases = "h"
    locks = "cmd:all()"
    help_category = "Menu"
    
    def func(self):
        "implement the menu help command"
        if self.caller.db._menu_data:
            # if we have menu data, try to use that. 
            lookstring = self.caller.db._menu_data.get("help", None)
            if lookstring:
                self.caller.msg(lookstring)
                return
        # otherwise we use normal help 
        super(CmdMenuHelp, self).func()
            
class MenuCmdSet(CmdSet):
    """
    Cmdset for the menu. Will replace all other commands.
    This always has a few basic commands available. 

    Note that you must always supply a way to exit the 
    cmdset manually! 
    """
    key = "menucmdset"
    priority = 1
    mergetype = "Replace"    
    def at_cmdset_creation(self):
        "populate cmdset"
        self.add(CmdMenuLook())
        self.add(CmdMenuHelp())

#
# Menu Node system 
#

class MenuTree(object):
    """
    The menu tree object holds the full menu structure consisting of
    MenuNodes. Each node is identified by a unique key.  The tree
    allows for traversal of nodes as well as entering and exiting the
    tree as needed. For safety, being in a menu will not survive a
    server reboot.

    A menutree have two special node keys given by 'startnode' and
    'endnode' arguments. The startnode is where the user will start
    upon first entering the menu.  The endnode need not actually
    exist, the moment it is linked to and that link is used, the menu
    will be exited and cleanups run. The default keys for these are
    'START' and 'END' respectively. 

    """
    def __init__(self, caller, nodes=None, startnode="START", endnode="END"):
        """
        We specify startnode/endnode so that the system knows where to
        enter and where to exit the menu tree. If nodes is given, it
        shuld be a list of valid node objects to add to the tree.
        """
        self.tree = {}
        self.startnode = startnode
        self.endnode = endnode 
        self.caller = caller 
        if nodes and utils.is_iter(nodes):
            for node in nodes:
                self.add(node)

    def start(self):
        """
        Initialize the menu
        """
        self.goto(self.startnode)

    def add(self, menunode):
        """
        Add a menu node object to the tree. Each node itself keeps
        track of which nodes it is connected to.
        """
        menunode.init(self)
        self.tree[menunode.key] = menunode 

    def goto(self, key):
        """
        Go to a key in the tree. This sets up the cmdsets on the
        caller so that they match the choices in that node.
        """
        if key == self.endnode:
            # if we was given the END node key, we clean up immediately.
            self.caller.cmdset.delete("menucmdset")
            del self.caller.db._menu_data
            self.caller.execute_cmd("look")
            return 
        # not exiting, look for a valid code. 
        node = self.tree.get(key, None)
        if node: 
            if node.code:
                # Execute eventual code active on this
                # node. self.caller is available at this point.
                try:
                    exec(node.code)
                except Exception, e:
                    self.caller.msg("{rCode could not be executed for node %s. Continuing anyway.{n" % key) 
                    self.caller.msg("Exception: %s" % e)
            # clean old menu cmdset and replace with the new one
            self.caller.cmdset.delete("menucmdset")
            self.caller.cmdset.add(node.cmdset)
            # set the menu flag data for the default commands
            self.caller.db._menu_data = {"help":node.helptext, "look":str(node.text)}
            # display the node 
            self.caller.msg(node.text)
        else:
            self.caller.msg("{rMenu node '%s' does not exist - maybe it's not created yet..{n" % key)


class MenuNode(object):
    """
    This represents a node in a menu tree. The node will display its
    textual content and offer menu links to other nodes (the relevant
    commands are created automatically)

    """
    def __init__(self, key, text="", links=None, linktexts=None, 
                 keywords=None, cols=1, helptext=None, code=""):
        """
        key       - the unique identifier of this node.
        text      - is the text that will be displayed at top when viewing this node. 
        links     - a list of keys for unique menunodes this is connected to.
        linktexts - a list of texts to describe the links. If defined, need to match links list
        keywords  - a list of unique keys for choosing links. Must match links list. If not given, index numbers will be used.
        cols      - how many columns to use for displaying options.
        helptext  - if defined, this is shown when using the help command instead of the normal help index.
        code      - functional code. This will be executed just before this node is loaded (i.e. 
                    as soon after it's been selected from another node). self.caller is available
                    to call from this code block, as well as ObjectDB and PlayerDB. 
        """
        self.key = key
        self.cmdset = None
        self.links = links
        self.linktexts = linktexts
        self.keywords = keywords
        self.cols = cols
        self.code = code
                   
        # validate the input 
        if not self.links:
            self.links = []
        if not self.linktexts or (self.linktexts and len(self.linktexts) != len(self.links)):
            self.linktexts = []
        if not self.keywords or (self.keywords and len(self.keywords) != len(self.links)):
            self.keywords = []

        # Format default text for the menu-help command 
        if not helptext:            
            helptext = "Select one of the valid options"
            if self.keywords:
                helptext += " (" + ", ".join(self.keywords) + ")"
            elif self.links:
                helptext += " (" + ", ".join([str(i + 1) for i in range(len(self.links))]) + ")"
        self.helptext = helptext

        # Format text display 
        string = ""
        if text:
            string += "%s\n" % text

        # format the choices into as many collumns as specified
        choices = []
        for ilink, link in enumerate(self.links):
            if self.keywords:
                choice = "{g%s{n" % self.keywords[ilink]
            else:
                choice = "{g%i{n" % (ilink + 1) 
            if self.linktexts:
                choice += "-%s" % self.linktexts[ilink]
            choices.append(choice)
        cols = [[] for i in range(min(len(choices), cols))]
        while True:
            for i in range(len(cols)):
                if not choices:
                    cols[i].append("")
                else:
                    cols[i].append(choices.pop(0))
            if not choices:
                break 
        ftable = utils.format_table(cols)
        for row in ftable:
            string += "\n" + "".join(row)
        # store text 
        self.text = 78*"-" + "\n" + string.strip()

    def init(self, menutree):
        """
        Called by menu tree. Initializes the commands needed by the menutree structure.
        """        
        # Create the relevant cmdset 
        self.cmdset = MenuCmdSet()
        for i, link in enumerate(self.links):
            cmd = CmdMenuNode()
            cmd.key = str(i + 1)
            cmd.menutree = menutree
            # this is the operable command, it moves us to the next node. 
            cmd.code = "self.menutree.goto('%s')" % link
            if self.keywords:
                cmd.aliases = [self.keywords[i]]
            self.cmdset.add(cmd)                

    def __str__(self):
        "Returns the string representation."
        return self.text 


#
# A simple yes/no question. Call this from a command to give object
# a cmdset where they may say yes or no to a question. Does not
# make use the node system since there is only one level of choice. 
# 

def prompt_yesno(caller, question="", yescode="", nocode="", default="N"):
    """
    This sets up a simple yes/no questionnaire. Question will
    be asked, followed by a Y/[N] prompt where the [x] signifies 
    the default selection. 
    """

    # creating and defining commands
    cmdyes = CmdMenuNode()    
    cmdyes.key = "yes"
    cmdyes.aliases = ["y"]
    # this will be executed in the context of the yes command (so self.caller will be available)
    cmdyes.code = "self.caller.cmdset.delete('menucmdset')\ndel self.caller.db._menu_data\n" + yescode

    cmdno = CmdMenuNode()    
    cmdno.key = "no"
    cmdno.aliases = ["n"]
    # this will be executed in the context of the no command
    cmdno.code = nocode + "\nself.caller.cmdset.delete('menucmdset')\ndel self.caller.db._menu_data"

    errorcmd = CmdMenuNode()
    errorcmd.key = CMD_NOMATCH
    errorcmd.code = "self.caller.msg('Please choose either Yes or No.')"    

    defaultcmd = CmdMenuNode()
    defaultcmd.key = CMD_NOINPUT
    defaultcmd.code = "self.caller.execute_cmd('%s')" % default

    # creating cmdset (this will already have look/help commands)
    yesnocmdset = MenuCmdSet()
    yesnocmdset.add(cmdyes)
    yesnocmdset.add(cmdno)
    yesnocmdset.add(errorcmd)
    yesnocmdset.add(defaultcmd)

    # assinging menu data flags to caller. 
    caller.db._menu_data = {"help":"Please select Yes or No.", 
                            "look":"Please select Yes or No."}
    # assign cmdset and ask question 
    caller.cmdset.add(yesnocmdset)
    if default == "Y":
        prompt = "[Y]/N"
    else:
        prompt = "Y/[N]"
    prompt = "%s %s: " % (question, prompt)
    caller.msg(prompt)

#
# Menu command test
#

class CmdMenuTest(Command):
    """
    testing menu module

    Usage: 
      menu 
      menu yesno 

    This will test the menu system. The normal operation will produce
    a small menu tree you can move around in. The 'yesno' option will
    instead show a one-time yes/no question.

    """

    key = "menu"
    locks = "cmd:all()"
    help_category = "Menu"
    def func(self):
        "Testing the menu system"
        
        if not self.args or self.args != "yesno":
            # testing the full menu-tree system            

            node0 = MenuNode("START", text="Start node. Select one of the links below. Here the links are ordered in one column.", 
                             links=["node1", "node2", "END"], linktexts=["Goto first node", "Goto second node", "Quit"])
            node1 = MenuNode("node1", text="First node. This node shows letters instead of numbers for the choices.", 
                             links=["END", "START"], linktexts=["Quit", "Back to start"], keywords=["q","b"])
            node2 = MenuNode("node2", text="Second node. This node lists choices in two columns.", 
                             links=["node3", "START"], linktexts=["Set an attribute", "Back to start"], cols=2)
            node3 = MenuNode("node3", text="Attribute 'menutest' set on you. You can examine it (only works if you are allowed to use the examine command) or remove it. You can also quit and examine it manually.", 
                             links=["node4", "node5", "node2", "END"], linktexts=["Remove attribute", "Examine attribute", 
                                                                                  "Back to second node", "Quit menu"], cols=2, 
                             code="self.caller.db.menutest='Testing!'")
            node4 = MenuNode("node4", text="Attribute 'menutest' removed again.",
                             links=["node2"], linktexts=["Back to second node."], cols=2, 
                             code="del self.caller.db.menutest")
            node5 = MenuNode("node5", links=["node4", "node2"], linktexts=["Remove attribute", "Back to second node."], cols=2, 
                             code="self.caller.msg('%s/%s = %s' % (self.caller.key, 'menutest', self.caller.db.menutest))")            

            menu = MenuTree(self.caller, nodes=(node0, node1, node2, node3, node4, node5))        
            menu.start()
        else:        
            "Testing the yesno question"
            prompt_yesno(self.caller, question="Please answer yes or no - Are you the master of this mud or not?", 
                         yescode="self.caller.msg('{gGood for you!{n')", 
                         nocode="self.caller.msg('{GNow you are just being modest ...{n')", 
                         default="N")
