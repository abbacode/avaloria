from src.utils import create, utils
from game.gamesrc.scripts.basescript import Script
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
            
    def at_repeat(self):
        attributes = self.obj.db.attributes
        """
        try:
            if attributes['buffed_health'] != 0:
                attributes['temp_health'] = attributes['buffed_health']
                self.obj.db.attributes = attributes
        except KeyError:
            pass

        try:
            if attributes['buffed_mana'] != 0:
                attributes['temp_mana'] = attributes['buffed_mana']
                self.obj.db.attributes = attributes
        except KeyError:
            pass
       
        for skill in self.obj.db.skills:
            if 'brawling' in skill.name:
                if self.db.brawling_level_last_seen != skill.db.level:
                    self.db.brawling_level_last_seen = skill.db.level
                    skill.update_attributes()
                    attributes['damage_bonus'] = skill.db.buff_amount
                    self.obj.db.attributes = attributes
            if 'spellweaving' in skill.name:
                if self.db.weaving_level_last_seen != skill.db.level:
                    self.db.weaving_level_last_seen = skill.db.level
                    skill.update_attributes()
                    attributes['spell_dmg_bonus'] = skill.db.buff_amount
                    self.obj.attributes = attributes
        """    

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

        if self.obj.db.group is None:
            self.obj.db.grouped = False
            
           

class CharacterBuff(Script):
    """
    Runs the duration of the buff applied, once done it cleans up attributes, etc.
    """
    
    def at_script_creation(self):
        self.key = "buff_sentinel"
        self.desc = "Buff timer scripts, cleans up things once a buff runs out."
        self.persistent = True
        self.interval = 1
        self.start_delay = False
    
    def at_repeat(self):
        character_effect_manager = self.obj.db.effect_manager
        character_effect_manager.check_effects()     
            
                        
class FirstLogin(Script):
    """
    This runs only once on login and allows players to choose their alignment.
    """

    def at_script_creation(self):
        self.key = 'character_first_login'
        self.desc = "Grabs info from player on first login to put in the character class"
        self.persistent = True
        self.interval = 2 
        self.repeats = 1
        self.start_delay = True
        self.db.first_run = True
    
    def at_repeat(self):
        attributes = self.obj.db.attributes
        nodes = []
        copy_dir = '/var/mud/evennia/game/gamesrc/copy/'
        for option in ['race', 'deity', 'alignment', 'gender']:
            if 'race' in option:
                for race in ['bardok', 'erelania', 'the unknowns', 'earthen', 'gerdling']:
                    confirm_node = MenuNode("confirm-%s" % race, links=['deity'], linktexts=['Choose your deity.'], code="self.caller.set_race('%s')" % race)
                    nodes.append(confirm_node)
                    if 'bardok' in race:
                        text = copyreader.read_file("%s/races/bardok_desc.txt" % copy_dir)
                        race_node = MenuNode("%s" % race, text=text, links=['confirm-bardok', 'race'], linktexts=['Confirm Race Selection', 'Back to Races'])
                    elif 'erelania' in race:
                        text = copyreader.read_file("%s/races/erelania_desc.txt" % copy_dir)
                        race_node = MenuNode("%s" % race, text=text, links=['confirm-erelania', 'race'], linktexts=['Confirm Race Selection', 'Back to Races'])
                    elif 'gerdling' in race:
                        text = copyreader.read_file("%s/races/gerdling_desc.txt" % copy_dir)
                        race_node = MenuNode("%s" % race, text=text, links=['confirm-gerdling', 'race'], linktexts=['Confirm Race Selection', 'Back to Races'])
                    elif 'earthen' in race:
                        text = copyreader.read_file("%s/races/earthen_desc.txt" % copy_dir)
                        race_node = MenuNode("%s" % race, text=text, links=['confirm-earthen', 'race'], linktexts=['Confirm Race Selection', 'Back to Races'])
                    nodes.append(race_node)
                text = copyreader.read_file("%s/races/races_desc.txt" % copy_dir)
                root_race_node = MenuNode("%s" % option, text=text, links=['bardok', 'erelania', 'gerdling', 'earthen'], linktexts=['The Bardok', 'The Erelania', 'The Gerdling', 'The Earthen']) 
                nodes.append(root_race_node)
            elif 'deity' in option:
                deities = ['ankarith', 'slyth', 'green warden', 'kaylynne']
                for deity in deities:
                    confirm_node = MenuNode('confirm-%s' % deity, links=['gender'], linktexts=['Choose your gender.'], code="self.caller.set_deity('%s')" % deity)
                    nodes.append(confirm_node)
                    if 'karith' in deity:
                        text = copyreader.read_file("%s/deities/ankarith_desc.txt" % copy_dir)
                        deity_node = MenuNode("%s" % deity, text=text, links=['confirm-ankarith', 'deity'], linktexts=['Confirm Deity Selection', 'Back to Deities'])
                        #self.obj.msg("links: %s,   linktexts: %s" % (deity_node.links, deity_node.linktexts))
                    elif 'slyth' in deity:
                        text = copyreader.read_file("%s/deities/slyth_desc.txt" % copy_dir)
                        deity_node = MenuNode("%s" % deity, text=text, links=['confirm-slyth', 'deity'], linktexts=['Confirm Deity Selection', 'Back to Deities'])
                    elif 'green warden' in deity:
                        text = copyreader.read_file("%s/deities/greenwarden_desc.txt" % copy_dir)
                        deity_node = MenuNode("%s" % deity, text=text, links=['confirm-green warden', 'deity'], linktexts=['Confirm Deity Selection', 'Back to Deities'])
                    elif 'kaylynne' in deity:
                        text = copyreader.read_file("%s/deities/kaylynne_desc.txt" % copy_dir)
                        deity_node = MenuNode("%s" % deity, text=text, links=['confirm-kaylynne', 'deity'], linktexts=['Confirm Deity Selection', 'Back to Deities'])
                    nodes.append(deity_node) 
                deity_node_text = copyreader.read_file("%s/deities/deities_desc.txt" % copy_dir)
                root_deity_node = MenuNode("deity", text=deity_node_text, links=['ankarith', 'slyth', 'green warden', 'kaylynne'], 
                        linktexts=['An\'Karith', 'Slyth of the Glade', 'The Green Warden', 'Kaylynne'])
                nodes.append(root_deity_node)
            elif 'gender' in option:
                confirm_male = MenuNode("confirm-gender-male", links=['alignment'], linktexts=['Choose the path you walk.'], code="self.caller.set_gender('male')")
                confirm_female = MenuNode("confirm-gender-female", links=['alignment'], linktexts=['Choose the path you walk.'], code="self.caller.set_gender('female')")
                nodes.append(confirm_male)
                nodes.append(confirm_female)
                text = """
--{rGender Selection{n--
Please select which gender you would like to be:

                """
                gender_node = MenuNode("gender", text=text, links=['confirm-gender-male', 'confirm-gender-female'], 
                                        linktexts=['Male', 'Female'])
                nodes.append(gender_node)
            elif 'alignment' in option:
                confirm_good = MenuNode("confirm-good", links=['END'], linktexts=['Begin your journey.'], text="{rYou begin your journey down the path of light.{n", code="self.caller.set_alignment('good')")
                confirm_evil = MenuNode("confirm-evil", links=['END'], linktexts=['Begin your journey.'], text="{rYou begin your journey down the path of darkness.{n", code="self.caller.set_alignment('evil')")
                nodes.append(confirm_good)
                nodes.append(confirm_evil)
                text = """
--{rAlignment Selection{n--
Which path to do you desire to walk?

                """
                alignment_node = MenuNode("alignment", text=text, links=['confirm-evil', 'confirm-good', 'START'], 
                                            linktexts=['Path of Darkness', 'Path of Light', 'Back to Customization'])
                nodes.append(alignment_node)
        start_node = MenuNode("START", text="{bWelcome to Avaloria.  Please proceed through the menu to customize your character.{n",
                        links=['race' ], linktexts=['Choose your race.']) 
        nodes.append(start_node)
        node_string = ' '.join([node.key for node in nodes])
        self.obj.msg("{mDEBUG: nodes: %s{n" % node_string)
        menutree = MenuTree(caller=self.obj, nodes=nodes)
        menutree.start()
    
    def is_valid(self):
        if self.obj.db.attributes['alignment'] is not None:
            return False
        else:
            return True

    def at_stop(self):
        self.obj.cmdset.add(character_cmdset.CharacterCommandSet)
        self.obj.cmdset.add(combat_cmdset.DefaultCombatSet)
        self.obj.cmdset.add(structure_cmdset.BuildCmdSet)
        self.obj.cmdset.delete(character_cmdset.AlignmentChoiceSet)
