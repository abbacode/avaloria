from src.utils import create, utils
from ev import Script
from game.gamesrc.commands.world import character_cmdset as character_cmdset
from game.gamesrc.commands.world import combat_cmdset as combat_cmdset
from game.gamesrc.commands.world import structure_cmdset as structure_cmdset
from game.gamesrc.objects.menusystem import *
from game.gamesrc.objects import copyreader

class CharacterSentinel(Script):
    """
    Checks various counters and flags on characters and fires off actions
    depending on what it finds.
    """

    def at_script_creation(self):
        self.key = "character_sentinel"
        self.desc = "Makes routine checks on Characters"
        self.persistent = True
        self.interval = 3
        self.start_delay = True
        self.db.points_flag = False
        self.db.brawling_level_last_seen = 0
        self.db.weaving_level_last_seen = 0
        self.db.prompt_sent = False
            
    def handle_no(self):
        pass

    def at_repeat(self):
        attributes = self.obj.db.attributes

        if self.obj.db.attributes['attribute_points'] > 0:
            if self.db.points_flag is False:
                self.obj.cmdset.add(character_cmdset.FreeAttributePointsState)
                self.obj.msg("{CYou have unspent attribute points.  Type 'points' to spend them.{n")
                self.db.points_flag = True
            else:
                pass 
        else:
            self.obj.cmdset.delete(character_cmdset.FreeAttributePointsState)
            self.db.points_flag = False
         
        if attributes['temp_health'] < attributes['health'] and self.obj.db.in_combat is False:
            percentage_to_heal = int(attributes['health'] * .02) + 1
            attributes['temp_health'] = attributes['temp_health'] + percentage_to_heal
            if attributes['temp_health'] > attributes['health']:
                attributes['temp_health'] = attributes['health']
            self.obj.db.attributes = attributes
        
        if attributes['temp_mana'] < attributes['mana'] and self.obj.db.in_combat is False:
            percentage_to_heal = int(attributes['mana'] * .02) + 1
            attributes['temp_mana'] = attributes['temp_mana'] + percentage_to_heal
            if attributes['temp_mana'] > attributes['mana']:
                attributes['temp_mana'] = attributes['mana']
            self.obj.db.attributes = attributes

        if attributes['temp_balance'] < attributes['balance'] and self.obj.db.in_combat is False:
            if attributes['temp_balance'] == attributes['balance']:
                pass
            else:
                attributes['temp_balance'] += 1
            self.obj.db.attributes = attributes

        cflags = self.obj.db.flags
        prompt_sent = self.db.prompt_sent
        if cflags['tutorial_started'] and not prompt_sent and not cflags['tutorial_done']:
            prompt_yesno(self.obj, question="Would you like to continure the Avaloria Tutorial?", yescode="self.caller.do_tutorial()", nocode="", default="N")
            self.db.prompt_sent = True
            prompt_sent = True
            
        if not cflags['tutorial_done'] and not prompt_sent:
            prompt_yesno(self.obj, question="Would you like to go through the Avaloria Tutorial?", yescode="self.caller.do_tutorial()", nocode="", default="N")
            self.db.prompt_sent = True

            
           
        if 'Battle On!' in self.obj.db.quest_log.db.completed_quests.keys() and not cflags['tutorial_done']:
            cflags['tutorial_done'] = True 
            self.db.flags = cflags
        if self.obj.db.group is None:
            self.obj.db.grouped = False
