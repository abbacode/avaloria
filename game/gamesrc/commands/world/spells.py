from src.utils import utils
from src.commands.cmdset import CmdSet
from game.gamesrc.commands.basecommand import Command, MuxCommand


class CmdFireball(Command):
    """
    Quick command to cast a fireball.  Fireball is a fire based projectile that does
    1d10 direct damage on impact and another 1d10 damage over 10 seconds.
    """
    
    key = 'fireball'
    locks = "cmd:holds(fireball)"
    aliases = ['FIREBALL', 'Fireball']
    help_category = 'Spells'

    def func(self):
        if self.caller.db.in_combat:
            manager = self.caller.db.spellbook
            spell = manager.find_item('fireball')
            spell.db.target = self.caller.db.target
            spell.db.caller = self.caller
            spell.scripts.add("game.gamesrc.scripts.world_scripts.effects.CastDelay")
        else:
            self.caller.msg("To use the quick command you must be in combat.  Try the cast command to start a fight with a spell.")


class CmdMagicMissile(Command):
    """
    Quick command to cast a magic missile.  Magic Missile is an arcane based magical attack
    that does 1d4 (@level 1) direct damage to the target.
    """

    key = "magic missile"
    locks = "cmd:holds(magic missile)"
    aliases = ['mm', 'MAGIC MISSILE', 'Magic Missile']
    help_category = 'Spells'

    def func(self):
        if self.caller.db.in_combat:
            manager = self.caller.db.spellbook
            spell = manager.find_item('magic missile')
            spell.db.target = self.caller.db.target
            spell.db.caller = self.caller
            spell.scripts.add('game.gamesrc.scripts.world_scripts.effects.CastDelay')
        else:
            self.caller.msg("To use the quick command you must be in combat.  Try the cast command to start a fight with a spell.")


class SpellsCmdSet(CmdSet):
    """
    Command set used to store all spell quick commands
    """

    def at_cmdset_creation(self):
        self.add(CmdFireball())
        self.add(CmdMagicMissile())
