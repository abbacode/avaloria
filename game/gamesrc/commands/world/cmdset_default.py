"""
This module ties together all the commands of the default command set. 
"""
from src.commands.cmdset import CmdSet
from src.commands.default.muxcommand import MuxCommand
from src.commands.default import general, help, admin, system
from src.commands.default import comms, building
from src.commands.default import batchprocess

class CmdFriends(MuxCommand):
    """
    Displays all friends currently online.  Also allows for the addition and deletion of new friends.

    usage: @friends/switches
        -add: add the person given as a friend
        -remove: remove the person given as a friend
    """
    key = "@friends"
    help_category = 'general'
    locks = "cmd:all()" 
    
    def parse(self):
        self.what = self.args

    def func(self):
        switches = self.switches
        friendslist_player = self.caller.player
        friendslist = friendslist_player.db.friends_list
        if switches:
            if 'add' in switches:
                friends_list.add(self.caller, self.what)
            elif 'remove' in switches:
                friends_list.remove(self.caller, self.what)
        else:
            friendslist.list_friends(self.caller)

class DefaultCmdSet(CmdSet):
    """
    Implements the default command set.
    """
    key = "DefaultMUX"
    priority = 0

    def at_cmdset_creation(self):
        "Populates the cmdset"

        # The general commands
        self.add(general.CmdLook())
        self.add(general.CmdHome())
        self.add(general.CmdWho())
        self.add(general.CmdInventory())
        self.add(general.CmdPose())
        self.add(general.CmdNick())
        self.add(general.CmdGet())
        self.add(general.CmdDrop())
        self.add(general.CmdSay())
        self.add(general.CmdAccess())
        self.add(CmdFriends())

        # The help system
        self.add(help.CmdHelp())
        self.add(help.CmdSetHelp())

        # System commands
        self.add(system.CmdReload())
        self.add(system.CmdReset())
        self.add(system.CmdShutdown())
        self.add(system.CmdPy())
        self.add(system.CmdScripts())        
        self.add(system.CmdObjects())
        self.add(system.CmdService())
        self.add(system.CmdVersion())
        self.add(system.CmdTime())
        self.add(system.CmdServerLoad())
        self.add(system.CmdPs())
        
        # Admin commands
        self.add(admin.CmdBoot())
        self.add(admin.CmdDelPlayer())
        self.add(admin.CmdEmit())
        self.add(admin.CmdNewPassword())
        self.add(admin.CmdPerm())
        self.add(admin.CmdWall())

        # Building and world manipulation
        self.add(building.CmdTeleport())
        self.add(building.CmdSetObjAlias())
        self.add(building.CmdListCmdSets())
        self.add(building.CmdDebug())    
        self.add(building.CmdWipe())
        self.add(building.CmdSetAttribute())        
        self.add(building.CmdName())
        self.add(building.CmdDesc())
        self.add(building.CmdCpAttr()) 
        self.add(building.CmdMvAttr()) 
        self.add(building.CmdCopy())
        self.add(building.CmdFind())
        self.add(building.CmdOpen())
        self.add(building.CmdLink())
        self.add(building.CmdUnLink())
        self.add(building.CmdCreate())        
        self.add(building.CmdDig())
        self.add(building.CmdTunnel())
        self.add(building.CmdDestroy())
        self.add(building.CmdExamine())
        self.add(building.CmdTypeclass())
        self.add(building.CmdLock())
        self.add(building.CmdScript())
        self.add(building.CmdHome())
        
        # Batchprocessor commands
        self.add(batchprocess.CmdBatchCommands())
        self.add(batchprocess.CmdBatchCode())
