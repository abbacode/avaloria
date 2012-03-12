from src.commands.cmdset import CmdSet
from game.gamesrc.commands.basecommand import Command, MuxCommand


class CmdConstruct(MuxCommand):
    """
    This command is the main structure building command.  Depending on the switch
    given, the command will begin new construction, deposit money towards the next
    level of the structure, sell/or destroy the structure.

    usage:
        construct/switches <structure> <amount of gold to put in>

    switches:
        deposit: add money towards the next level of the structure
        begin: start building a new structure
        withdraw: take money from the structure and give to the player
            note: if you take out enough that it dips below the amount needed
            for level, the structure will de-level.
        destroy: reclaim all money spent and remove the structure from your lair.
        
    
    If called with no switches, it will display a list of buildable structures.
    """
    key = '@construct'
    aliases = ['construct', 'build', 'begin build', 'const']
    help_category = "General"
    locks = "cmd:all()"

    def func(self):
        if self.caller.location != self.caller.db.lair:
            self.caller.msg("{COnly useable in your lair.")
            return
        switches = self.switches
        lair = self.caller.location
        manager = self.caller.location.search(lair.db.structure_manager_id, global_search=False)
        self.structure = ""
        self.gold_to_add = None
        for arg in self.args.split():
            if arg.isdigit():
                if self.structure is None:
                    self.caller.msg("Please enter the amount of gold after the structure name.")
                    return
                self.gold_to_add = arg
            else:
                arg = arg.title()
                self.structure += "%s " % arg

        if self.gold_to_add is None:
            self.gold_to_add = 0
    
        self.structure = self.structure.strip()
        if switches:
            if 'begin' in switches:
                manager.begin_construction(self.gold_to_add, self.structure)
            elif 'deposit' in switches:
                structure = self.caller.search(self.structure, global_search=False)
                self.caller.spend_gold(self.gold_to_add)
                structure.award_gold(self.gold_to_add)
            elif 'withdraw' in switches:
                structure = self.caller.location.search(self.structure, global_search=False)
                self.gold_to_take = self.gold_to_add
                structure.withdraw_gold(self.gold_to_take)
                self.caller.award_gold(self.gold_to_take)
            elif 'destroy' in switches:
                structure = self.caller.location.search(self.structure, global_search=False)
                structure.destroy()
            elif 'list' in switches:
                manager.show_already_built()
            else:
                self.caller.msg("usage: construct/switches <structure> <amount of gold> (help construct for more details)")
        else:
            manager.show_buildable_list()
            
#CMD Sets

class BuildCmdSet(CmdSet):
    key = 'StructureManagerCommands'
    
    def at_cmdset_creation(self):
        self.add(CmdConstruct())


