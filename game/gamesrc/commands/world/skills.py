from src.utils import utils
from ev import CmdSet
from game.gamesrc.commands.basecommand import Command, MuxCommand


class CmdKick(Command):
    """
    Command used to kick a target.  Must be trained in kick.
    """
    key = "kick"
    aliases = ['Kick', 'KICK']
    locks = "cmd:holds(kick)" 
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
    aliases = ['Strike', 'STRIKE']
    locks = "cmd:holds(strike)"
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
    aliases = ['Rend', 'REND']
    locks = "cmd:holds(rend)"
    help_category = "Combat Skills"
    
    def func(self):
        caller = self.caller
        manager = caller.db.skill_log
        skill_obj = manager.find_item('rend')
        skill_obj.push_to_combat_queue()

class CombatSkillCmdSet(CmdSet):
    """
    Command set used to store combat skill commands.
    """
    key = "CombatSKillCmdSet"
    
    def at_cmdset_creation(self):
        self.add(CmdKick())
        self.add(CmdStrike())
        self.add(CmdRend())

