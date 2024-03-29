"""

Contribution - Griatch 2011

This is a simple character creation commandset. A suggestion is to
test this together with menu_login, which doesn't create a Character
on its own. This shows some more info and gives the Player the option
to create a character without any more customizations than their name
(further options are unique for each game anyway).

Since this extends the OOC cmdset, logging in from the menu will
automatically drop the Player into this cmdset unless they logged off
while puppeting a Character already before.

Installation:

Import this module in game.gamesrc.basecmdset and
add the following line to the end of OOCCmdSet's at_cmdset_creation():
   
   self.add(chargen.OOCCmdSetCharGen)


"""

from django.conf import settings 
from src.commands.command import Command
from src.commands.default.general import CmdLook 
from src.commands.default.cmdset_ooc import OOCCmdSet
from src.objects.models import ObjectDB
from src.utils import utils, create

CHARACTER_TYPECLASS = settings.BASE_CHARACTER_TYPECLASS

class CmdOOCLook(CmdLook):
    """
    ooc look

    Usage:
      look
      look <character>

    This is an OOC version of the look command. Since a Player doesn't
    have an in-game existence, there is no concept of location or
    "self".

    If any characters are available for you to control, you may look
    at them with this command.
    """

    key = "look"
    aliases = ["l", "ls"]
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        """
        Implements the ooc look command

        We use an attribute _character_dbrefs on the player in order
        to figure out which characters are "theirs". A drawback of this
        is that only the CmdCharacterCreate command adds this attribute,
        and thus e.g. player #1 will not be listed (although it will work).
        Existence in this list does not depend on puppeting rights though,
        that is checked by the @ic command directly. 
        """

        # making sure caller is really a player 
        self.character = None
        if utils.inherits_from(self.caller, "src.objects.objects.Object"):
            # An object of some type is calling. Convert to player.
            #print self.caller, self.caller.__class__
            self.character = self.caller 
            if hasattr(self.caller, "player"):
                self.caller = self.caller.player

        if not self.character:            
            # ooc mode, we are players 

            avail_chars = self.caller.db._character_dbrefs
            if self.args:
                # Maybe the caller wants to look at a character
                if not avail_chars: 
                    self.caller.msg("You have no characters to look at. Why not create one?")
                    return                                             
                objs = ObjectDB.objects.get_objs_with_key_and_typeclass(self.args.strip(), CHARACTER_TYPECLASS)
                objs = [obj for obj in objs if obj.id in avail_chars]
                if not objs: 
                    self.caller.msg("You cannot see this Character.")
                    return 
                self.caller.msg(objs[0].return_appearance(self.caller))
                return 

            # not inspecting a character. Show the OOC info. 
            charobjs = []
            charnames = []
            if self.caller.db._character_dbrefs:
                dbrefs = self.caller.db._character_dbrefs                
                charobjs = [ObjectDB.objects.get_id(dbref) for dbref in dbrefs]
                charnames = [charobj.key for charobj in charobjs if charobj]
            if charnames: 
                charlist = "The following Character(s) are available:\n\n"
                charlist += "\n\r".join(["{w    %s{n" % charname for charname in charnames])                    
                charlist += "\n\n   Use {w@ic <character name>{n to switch to that Character."
            else:
                charlist = "You have no Characters."
            string = \
"""   You, %s, are an {wOOC ghost{n without form. The world is hidden
   from you and besides chatting on channels your options are limited.
   You need to have a Character in order to interact with the world.

   %s

   Use {wcreate <name>{n to create a new character and {whelp{n for a
   list of available commands.""" % (self.caller.key, charlist)
            self.caller.msg(string)

        else:
            # not ooc mode - leave back to normal look 
            self.caller = self.character # we have to put this back for normal look to work.
            super(CmdOOCLook, self).func()

class CmdOOCCharacterCreate(Command):
    """
    creates a character

    Usage: 
      create <character name>

    This will create a new character, assuming
    the given character name does not already exist. 
    """

    key = "create"
    locks = "cmd:all()"

    def func(self):
        """
        Tries to create the Character object. We also put an
        attribute on ourselves to remember it. 
        """

        # making sure caller is really a player 
        self.character = None
        if utils.inherits_from(self.caller, "src.objects.objects.Object"):
            # An object of some type is calling. Convert to player.
            #print self.caller, self.caller.__class__
            self.character = self.caller 
            if hasattr(self.caller, "player"):
                self.caller = self.caller.player

        if not self.args:
            self.caller.msg("Usage: create <character name>")
            return 
        charname = self.args.strip()
        old_char = ObjectDB.objects.get_objs_with_key_and_typeclass(charname, CHARACTER_TYPECLASS)
        if old_char:
            self.caller.msg("Character {c%s{n already exists." % charname)
            return 
        # create the character
        
        new_character = create.create_object(CHARACTER_TYPECLASS, key=charname)
        if not new_character:
            self.caller.msg("{rThe Character couldn't be created. This is a bug. Please contact an admin.")
            return 
        # make sure to lock the character to only be puppeted by this player
        new_character.locks.add("puppet:id(%i) or pid(%i) or perm(Immortals) or pperm(Immortals)" % 
                                (new_character.id, self.caller.id))

        # save dbref
        avail_chars = self.caller.db._character_dbrefs
        if avail_chars:
            avail_chars.append(new_character.id)
        else:
            avail_chars = [new_character.id]
        self.caller.db._character_dbrefs = avail_chars

        self.caller.msg("{gThe Character {c%s{g was successfully created!" % charname) 
        
        self.caller = new_character
        attributes = new_character.db.attributes
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
                confirm_good = MenuNode("confirm-good",  text="{rYou begin your journey down the path of light.{n", code="self.caller.set_alignment('good')")
                confirm_evil = MenuNode("confirm-evil", text="{rYou begin your journey down the path of darkness.{n", code="self.caller.set_alignment('evil')")
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


class OOCCmdSetCharGen(OOCCmdSet):
    """
    Extends the default OOC cmdset.
    """    
    def at_cmdset_creation(self):
        "Install everything from the default set, then overload"
        #super(OOCCmdSetCharGen, self).at_cmdset_creation()
        self.add(CmdOOCLook())
        self.add(CmdOOCCharacterCreate())

