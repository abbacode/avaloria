import random
from src.utils import utils
from ev import CmdSet, Command
from game.gamesrc.objects.menusystem import *

class CmdCon(Command):
    """
    This command allows you to size up and opponent and give you and idea
    of whether you can defeat them in combat or not.

    usage:
        con <enemy>
    """

    key = 'con'
    aliases = ['sizeup', 'judge']
    help_category = "General"   
    locks = "cmd:all()"

    def parse(self):
        self.what = self.args.strip()

    def func(self):
        if len(self.args) < 1:
            self.caller.msg("What did you want to size up? (con <baddy to size up>)")
            return
        obj = self.caller.search(self.what, use_nicks=True)
        if obj is not None:
            obj.at_inspect(looker=self.caller)
        else:
            self.caller.msg("Could not find %s anywhere around you. Perhaps you are hallucinating?" % self.what)
            return

class CmdFlee(Command):
    """
    This command will allow you to attempt to flee from combat.  If you flee, you will
    be moved to an adjacent room, and combat will be ceased.  This doesn't mean the
    creature you were fighting won't try to come and find you...

    Usage: flee
    """
    key = 'flee'
    help_category = "General"
    locks = "cmd:all()"
    
    def func(self):
        if self.caller.db.in_comabat is not True:
            self.caller.msg("You must be in combat to flee...")
            return
        obj = self.caller
        zone_manager = obj.location.db.manager
        zone_map = zone_manager.db.path_map
        player_map = zone_manager.db.player_map
        target = self.obj.db.target
        mob_follow_list = target.db.follow_list
        if obj not in mob_follow_list:
            mob_follow_list.append(obj)
        target.db.follow_list = mob_follow_list
        obj.db.in_combat = False
        target.db.in_combat = False
        obj.scripts.validate()
        self.caller.msg("You successfully disengage from combat and flee!")

class CmdAttack(Command):
    """
    This command launches you into battle with the given target, until one
    of you lays dead on the floor.
    
    usage:
        attack <mob|player character>
    
    Hint: you may want to use the [con] command you find out if you even stand
    a chance battling the target
    """

    key = 'attack'
    aliases = ['kill', 'fight', 'battle']
    help_category = "General"
    locks = "cmd:all()"

    def parse(self):
        self.what = self.args.strip()
    
    def func(self):
        if len(self.args) < 1 and self.caller.db.in_combat is False:
            self.caller.msg("What did you want to attack? Surely not yourself.")
            return
        player_combat_queue = self.caller.db.combat_queue
        if self.caller.db.in_combat is True:
            if len(player_combat_queue) == 4:
                self.caller.msg("Can't queue up more than four actions.")
                return
            player_combat_queue.append('attack') 
            self.caller.db.combat_queue = player_combat_queue
            self.caller.msg("\'attack\' action added to your combat queue.")
            return
        #find the target in the location the player is in
        obj = self.caller.search(self.what, use_nicks=True)
        if obj is not None:
            #if we found an object then start fighting it
            if hasattr(obj, 'mob_type'):
                self.caller.begin_attack(opponent=obj)
            else:
                self.caller.msg("Thats probably a bad idea...")
                return
        else:
            self.caller.msg("I don't see anything around here named: %s" % self.what)
            return

class CmdDefend(Command):
   """
    This command queues up a defend action in your combat queue.  Only useable
    while actively engaging in combat.
    
    usage: defend
   """
   key = 'defend'
   help_category = "General"
   locks = "cmd:all()"

   def func(self):
       if self.caller.in_combat is not True:
           self.caller.msg("Only useable in combat.")
           return
       else:
           player_combat_queue = self.caller.db.combat_queue
           if len(player_combat_queue) == 4:
               self.caller.msg("You may only queue up to 4 actions at once.")
           else:
               player_combat_queue.append('defend')
               self.caller.msg("Queued the defend action in your combat_queue")
           self.caller.db.combat_queue = player_combat_queue


class CmdCast(Command):
    """
    The cast command allows you to cast the various spells that your character
    knows.

    usage:
        cast <spell name>
    """
    key = 'cast'
    help_category = "General"
    locks = "cmd:all()"
    
    def parse(self):
        self.what = self.args.split()
        self.spellname = ""
        self.character = ""
        self.name_start = False
        for i in self.what:
            #self.caller.msg("DEBUG: i == %s" % i )
            if self.name_start is True:
                if len(self.character) < 1:
                    self.character += "%s" % i
                else:
                    self.character += " %s" % i
                
            else: 
                if 'on' in i:
                    self.name_start = True
                else:
                    self.spellname += "%s " % i
#        self.caller.msg("{rDEBUG:{n Spellname == %s" % self.spellname)
        self.character = self.character.rstrip()
                

    def func(self):
        if len(self.args) < 1:
            self.caller.msg("What did you want to cast?")
            return
        manager = self.caller.db.spellbook
        spells = manager.db.spells
        spell_obj = manager.find_item(self.spellname.title())
        if not spell_obj:
            self.caller.msg("That is not a valid spell, or you just do not know it yet.")
            return
        if self.character is not None:
            spell_obj.db.caller = self.caller
            spell_obj.db.target = self.character
            spell_obj.scripts.add("game.gamesrc.scripts.world_scripts.effects.CastDelay")
        else:
            spell_obj.db.caller = self.caller
            spell_obj.scripts.add("game.gamesrc.scripts.world_scripts.effects.CastDelay")

#CmdSets

class DefaultCombatSet(CmdSet):
    key = 'DefaultCombatCommandSet'
    
    def at_cmdset_creation(self):
        self.add(CmdCon())
        self.add(CmdAttack())
        self.add(CmdFlee())
        self.add(CmdCast())
        self.add(CmdDefend())
    
