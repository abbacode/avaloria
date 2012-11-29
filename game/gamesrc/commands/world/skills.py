from src.utils import utils
from ev import CmdSet
from game.gamesrc.commands.basecommand import Command, MuxCommand


class CmdKick(Command):
    """
    Command used to kick a target.  Must be trained in kick.
    """
    key = "kick"
    locks = "cmd:has_skill(kick)" 
    help_category = "Combat Skills"

    def func(self):
        caller = self.caller
        manager = caller.db.skill_log
        skill_obj = manager.find_item('kick')
        skill_obj.push_to_combat_queue()
        
class CmdStrike(Command):
    """
    Command used to perform a somewhat powerful melee blow. 
    """
    key = "strike"
    locks = "cmd:has_skill(strike)"
    help_category = "Combat Skills"
   
    def func(self):
        caller = self.caller
        manager = caller.db.skill_log
        skill_obj = manager.find_item('strike')
        skill_obj.push_to_combat_queue()


class CmdRend(Command):
    """
    Command used to quick use the Rend skill.
    """
    key = 'rend'
    locks = "cmd:has_skill(rend)"
    help_category = "Combat Skills"
    
    def func(self):
        caller = self.caller
        manager = caller.db.skill_log
        skill_obj = manager.find_item('rend')
        skill_obj.push_to_combat_queue()

class CmdShieldBash(Command):
    """
    Command used to quick call the 'shield bash' ability.
    """
    key = 'shield bash'
    aliases = 'sb'
    help_category = "Combat Skills"
    
    def func(self):
        caller = self.caller
        manager = caller.db.skill_log
        so = manager.find_item('shield bash')
        so.push_to_combat_queue()

class CmdCripple(Command):
    """
    Command used to quick call the 'Crippling Strike' skill.
    """
    key = 'cripple'
    help_category = "Combat Skills"
    
    def func(self):
        caller = self.caller
        manager = caller.db.skill_log
        so = manager.find_item('crippling strike')
        so.push_to_combat_queue()



class CombatSkillCmdSet(CmdSet):
    """
    Command set used to store combat skill commands.
    """
    key = "CombatSKillCmdSet"
    
    def at_cmdset_creation(self):
        self.add(CmdKick())
        self.add(CmdStrike())
        self.add(CmdRend())
        self.add(CmdCripple())
        self.add(CmdShieldBash())

