import random
import re
from src.utils import utils
from src.commands.cmdset import CmdSet
from game.gamesrc.commands.basecommand import Command, MuxCommand

class CmdInventory(MuxCommand):
    """
    Shows you what you are carrying, also showing what is equipped and what is 
    not.  Also prints out how much gold you are carrying.

    Usage: inventory
    """
    key = 'inventory'
    aliases = ['inv', 'i']
    help_category = 'general'
    locks = "cmd:all()"
    
    def func(self):
        "check inventory"
        items = self.caller.contents
        equipped = self.caller.db.equipment
        if not items:
            string = "You are not carrying anything."
        else:
            # format item list into nice collumns
            cols = [[],[]]
            for item in items:
                if item.db.is_equipped:
                    cols[0].append(item.name + " {g(Equipped){n")
                else:
                    cols[0].append(item.name)
                desc = item.db.desc
                if not desc:
                    desc = ""
                cols[1].append(utils.crop(str(desc)))
            # auto-format the columns to make them evenly wide
            ftable = utils.format_table(cols)
            string = "You are carrying:"
            for row in ftable:
                string += "\n " + "{C%s{n - %s" % (row[0], row[1])
        self.caller.msg(string)
        gold = self.caller.db.attributes['gold']
        exp_cur = self.caller.db.attributes['experience_currency']
        self.caller.msg("{CYou have: {y%s{n{C gold and {y%s{n {CExperience Currency.{n" % (gold, exp_cur))

class CmdTransmute(Command):
    """
    Call upon your divinely gifted power to transmute unwanted items into gold.
    
    Usage: transmute <object name> | transmute <object>, <object>...
    """
    key = 'transmute'
    aliases = ['sell']
    help_category = 'general'
    locks = "cmd:all()"
    
    def parse(self):
        if ',' in self.args:
            self.what = self.args.split(",")
        else:
            self.what = self.args.strip()
            self.caller.msg("args: %s" % self.what)

    def func(self):
        attributes = self.caller.db.attributes
        if len(self.args) < 1:
            self.caller.msg("Please supply the name of the item you want to transmute")
            return
        if hasattr(self.what, "strip"):
            item_obj = self.caller.search(self.what, global_search=False)
            gold_to_award = item_obj.db.value
            self.caller.msg("{CAs you concentrate the %s becomes gold coins in your hand." % item_obj.name)
            self.caller.award_gold(gold_to_award)
            item_obj.delete()
        else:
            for item in self.what:
                item_obj = self.caller.search(item.lstrip(), global_search=False)
                if item_obj is None:
                    return
                gold_to_award = item_obj.db.value
                self.caller.msg("{CAs you concentrate the %s becomes gold coins in your hand." % item_obj.name)
                self.caller.award_gold(gold_to_award)
                item_obj.delete()

class CmdLairTeleport(Command):
    """
    Use the magic bestowed upon you by your God to teleport back to your base
    of operations
    
    Usage:
        goto lair
    """
    key = 'goto'
    aliases = ['lair teleport']
    help_category = 'general'
    locks = "cmd:all()"

    def parse(self):
        self.what = self.args.strip()

    def func(self):
        if len(self.what) < 1:
            self.caller.msg("Please specify where you want to go")
            return
        if self.what == "lair":
            room_left = self.caller.location
            self.caller.msg("You concentrate your deity's energy to move you through space and time.")
            self.caller.move_to(self.caller.db.lair, quiet=True)
            room_left.msg_contents("%s disappears in a puff of smoke." % self.caller.name)
        else:
            self.caller.msg("You don't have a soul link to that location.")
            return
        
    
class CmdTalk(Command):
    """
    Attempt to talk to the given object, typically an npc who is able to respond
    to you.  Will return gracefully if the particular object does not support
    having a conversation with the character.
    
    Usage:
        talk to <npc|object name> <whatever yer message is>

    NOTE: Just because you can talk to an npc does not mean that they care about
    or know about what you are discussing with them.  Typically the control words
    will be very easy to spot.
    """
    key = 'talk'
    aliases = ['talk to', 't']
    help_category = 'general'
    locks = "cmd:all()"

    def parse(self):
        args = self.args.split()
        self.npc = args[0]
        args.remove(self.npc)
        self.message = ' '.join(args)

    def func(self):
        npc = self.caller.search(self.npc, global_search=False)
        if npc is not None:
            self.caller.msg("{mYou tell %s: %s{n" % (npc.name, self.message)) 
        args.remove(self.npc)
        self.message = ' '.join(args)

    def func(self):
        npc = self.caller.search(self.npc, global_search=False)
        if npc is not None:
            self.caller.msg("{mYou tell %s: %s{n" % (npc.name, self.message)) 
            npc.dictate_action(self.caller, self.message)  
        else:
            self.caller.msg("I don not see anyone around by that name.")
            return
            
        

class CmdUse(Command):
    """
    Attempt to use the given item. If the item can be used, your character
    will trye to use it.  This obviously can mean different things depending
    upon the situation.
    
    Usage:
        use <whatever you want to use>

    NOTE: The item must be an object within your general vicinity
    """
    key = 'use'
    aliases = ['u']
    help_category = "General"
    locks = "cmd:all()"

    def parse(self):
        if len(self.args) < 1:
            self.caller.msg("What did you want to use? (use <item to use|skill>)")
            return
        self.what = str(self.args.strip())

    def func(self):
        skill_manager = self.caller.db.skill_log
        skills = skill_manager.db.skills
        for skill in skills:
            skill_name = skill
            skill_obj = skills[skill]
            if self.what.lower() == skill_obj.name.lower():
                skill_obj.push_to_combat_queue()
                #skill.on_use(self.caller)
                return
        
        obj = self.caller.search(self.what, global_search=False)
        if obj is None:
            return
        if hasattr(obj, 'on_use'):
            obj.on_use(self.caller)
        else:
            self.caller.msg("Doesn't look like the %s is useable" % obj.name)
        return  

class CmdInspect(Command):
    """
    Gathers detailed information about things and people around you.
    Sees things that 'look' does not.
    
    Usage:
        inspect <thing to inspect>
    """
    key = 'inspect'
    aliases = ['ins', 'inpsect it']
    help_category = "General"
    locks = "cmd:all()"

    def parse(self):
        if len(self.args) < 1:
            self.caller.msg("What did you want to inspect? (inspect <item or thing to look at>)")
            return
        self.what = self.args.strip()

    def func(self):
            obj = self.caller.search(self.what, global_search=False)
            if obj is not None:
                self.caller.msg("{WInpection details:{n")
                if hasattr(obj, 'at_inspect'):
                    obj.at_inspect(looker=self.caller)
                else:
                    self.caller.msg("Nothing more is known about %s." % obj.name)
    
class CmdShow(Command):
    """
    Displays current values for information regarding your character
    Usage:
        show attributes|stats|equipment
    """
    key = 'show'
    aliases = ['score']
    help_category = "General"
    locks = "cmd:all()"

    def parse(self):
        if len(self.args) < 1:
            self.what = 'all'
        else:
            self.what = self.args.strip()
            
    def func(self):
        caller_effect_manager = self.caller.db.effect_manager
        if 'all' not in self.what:
            if 'attributes' in self.what:
                self.caller.display_attributes()
            elif 'stats' in self.what:
                self.caller.display_stats()
            elif 'equipment' in self.what:
                self.caller.display_equipped()
            elif 'skills' in self.what:
                manager = self.caller.db.skill_log
                manager.display_skills(self.caller)
            elif 'spells' in self.what:
                manager = self.caller.db.spellbook
                manager.display_spells(self.caller)
            elif 'buffs' in self.what or 'effects' in self.what:
                self.caller.display_effects()
        else:
            self.caller.character_summary()

class CmdLoot(Command):
    """
    Loots the corpse given.
    
    usage: loot <corpse>
    """
    key = 'loot'
    help_category = "General"
    locks = "cmd:all()"

    def parse(self):
        if len(self.args) < 1:
            m = "Loot what? Please specify what you want to loot. (usage: loot <corpse>)"
            self.caller.msg(m)
            return
        self.what = self.args.strip()

    def func(self):
        corpse = self.caller.search(self.what) 
        if corpse is not None:
            self.caller.loot(corpse=corpse)
        else:
            self.caller.msg("I didn't find the corpse specified")


class CmdLootChest(Command):
    """
    Loots the given item in a chest, or all items in the chest.  Only available when
    a chest object is open.
    """
    key = 'loot'
    help_category = "General"
    locks = "cmd:all()"
    
    def parse(self):
        if len(self.args) < 1:
            self.caller.msg("What chest did you want to loot?")
            return
        self.what = self.args.strip()
        
    def func(self):
        chest_obj = self.caller.search(self.what, global_search=False)
        if chest_obj is None:
            return
        if chest_obj.db.is_open is False:
            self.caller.msg("%s is not open! Open it first." % chest_obj.name)
            return
        chest_obj.give_contents(self.caller)
            
class CmdOpen(Command):
    """
    Open a closed object.  The object could be anything, chest, bag, door
    etc.  If you are able to open it, then it will be opened. If not, then
    well you can probably decipher it will stay shut.

    usage:
        open <object to open> | example: open large chest
    """
    key = 'open'
    help_category = "General"
    locks = "cmd:all()"
    
    def parse(self):
        if len(self.args) < 1:
            self.caller.msg("What object did you want to open?")
            return
        self.what = self.args.strip()
    
    def func(self):
        object = self.caller.search(self.what, global_search=False)
        if not object.access(self.caller, 'open'):
            self.caller.msg("You can't open that.  You probably need a key or it is locked.")
            return

        try:
            object.open_storage(self.caller)
        except AttributeError:
            self.caller.msg("Doesn't look like %s opens." % object.name)
            return

class CmdEquip(Command):
    """
    This attempts to equip items on the character. If no arguements are
    given, then it picks the first item for each slot it finds and equips
    those items in their respective slots.

    usage: 
        equip <item to equip>
    
    aliases: wield, equip item, e
    """
    key = 'equip'
    aliases = ['equip item', 'wield', 'e']
    help_category = "General"
    locks = "cmd:all()"

    def parse(self):
        if len(self.args) < 1:
            self.what = None
        else:
            self.what = self.args.strip()

    def func(self):
        if self.what is not None:
            obj = self.caller.search(self.what, global_search=False)
            if not obj:
                self.caller.msg("Are you sure you are carrying the item you are trying to equip?")
            else:
                self.caller.equip_item(ite=obj, slot=obj.db.slot)
                obj.on_equip()
        else:
            self.caller.equip_item(ite=None,slot=None)


class CmdUnEquip(Command):
    """
    This will unequip the item specified or unequip all items if no target
    is specifified.
    
    usage:
        unequip <slot>

    Available slots: weapon, armor
    """
    key = 'unequip'
    aliases = [ 'ue' ]
    help_category = "General"
    locks = "cmd:all()"
    
    def parse(self):
        if len(self.args) < 1:
            self.what = None
        else:
            self.what = self.args.strip()

    def func(self):
        if self.what is not None:
            obj = self.caller.search(self.what, global_search=False, ignore_errors=True)
            if not obj:
                self.caller.unequip_item(ite=self.what)
            else:
                self.caller.unequip_item(ite=obj.db.slot)
        else:
            self.caller.unequip_item()


class CmdAddTo(Command):
    """
    Start the menu to add attribute points to your attributes.
    usage:
        points
    """
    key = 'points'
    aliases = ['add to', 'add', 'attributes']
    help_category = "General"
    locks = "cmd:all()"

    def func(self):
        self.caller.create_attribute_menu(caller=self.caller)

class CmdSkills(Command):
    """
    Start the menu to advance skill ranks
    """
    key = 'skills'
    help_category = "general"
    locks = "cmd:all()"

    def func(self):
        manager = self.caller.db.skill_log
        if len(manager.db.skills) < 1:
            self.caller.msg("You have no skills.")
            return
        manager.generate_skill_menu(self.caller)


class CmdQuestLog(MuxCommand):
    """
    The questlog command is used to view your chracters current quests,
    and objectives for those quests.
    
    usage: @questlog/<switches> <questname>
    
    switches:
        objectives - lists out the objectives for said quest
        completed - lists the quests you have completed

    if given no switches, a short display of the questlog will be given
    which shows the quest name and its short description.
    
    To get the most verbose detail on a quest use the 'help' command.
    example: help <questname>
    """
    key = '@questlog'
    aliases = ['questlog']
    help_category = "General"
    locks = "cmd:all()"

    def func(self):
        switches = self.switches
        quest = self.args.strip()
        quest_manager = self.caller.db.quest_log
        if quest_manager is None:
            self.caller.msg("No Quest Manager found.")
            self.caller.msg("This shouldn't happen.  Contact an admin.")
            return
        if switches:
            if 'objectives' in switches:
                quest_manager.quest_objectives_display(self.caller, quest)
            elif 'completed' in switches:
                quest_manager.completed_quests_view(self.caller)
        else:
            quest_manager.quest_log_short_display(self.caller)     
            return
                 
    
#character class command sets
class FreeAttributePointsState(CmdSet):
    """
    This state is activated when there are attribute ponts to spend
    and deactivated when there are not
    """
    key = 'FreeAttributePoints'
    
    def at_cmdset_creation(self):
        self.add(CmdAddTo())

class AlignmentChoiceSet(CmdSet):
    """
    This is just a set for the alignment choice command: choose
    """
    key = 'AlignmentChoiceSet'
    
    def at_cmdset_creation(self):
        self.add(CmdChoose())
    
class CharacterCommandSet(CmdSet):
    """
    These are the base character commands that all characters recv
    on login
    """
    key = 'CharacterClassCommands'

    def at_cmdset_creation(self):
        self.add(CmdShow())     
        self.add(CmdInventory())
        self.add(CmdTransmute())
        self.add(CmdLairTeleport())
        self.add(CmdEquip())
        self.add(CmdUnEquip())
        self.add(CmdInspect())
        self.add(CmdLoot())
        self.add(CmdUse())
        self.add(CmdTalk())
        self.add(CmdOpen())
        self.add(CmdQuestLog())
        self.add(CmdSkills())

class ChestCommandSet(CmdSet):
    """
    Chest command set
    """
    key = 'ChestCommandSet'

    def at_cmdset_creation(self):
        self.add(CmdLootChest)

