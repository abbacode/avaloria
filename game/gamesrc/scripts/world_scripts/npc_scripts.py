import time, random
from src.utils import create
from game.gamesrc.scripts.basescript import Script
from game.gamesrc.objects.world.items import Armor, Weapon, Potion
from game.gamesrc.objects.world.skills import TrainingBook

class Merchant(Script):
    """
    Controls certain aspects of the merchant npc, such as inventory creation
    and maint.
    """
    def at_script_creation(self):
        self.persistent = True
        self.interval = 60
        self.start_delay = False
        
        
    def at_repeat(self):
        self.db.potions = self.obj.search('storage_potions', global_search=True, ignore_errors=True)
        self.db.weapons = self.obj.search('storage_weapons', global_search=True, ignore_errors=True)
        if len(self.obj.contents) < 1:
            if 'potions' in self.obj.db.merchant_type:
                for item in self.potions:
                    merchant_copy = item.copy()
                    merchant_copy.name = item.name
                    merchant_copy.move_to(destination=self.obj)
            elif 'weapons' in self.obj.db.merchant_type:
                for item in self.db.weapons:
                    merchant_copy = item.copy()
                    merchant_copy.name = item.name
                    merchant_copy.move_to(destination=self.obj)
    
        rn = random.random()
        if rn < .02:
            random_msgs = ["{y%s shuffles their feet in boredom.{n" % self.obj.name, "{y%s counts their earned money, smiling to themselves.{n" % self.obj.name,
                            "{m%s whispers to you: So are you gonna buy something or stare at me all day?{n" % self.obj.name ]
            msg = random.choice(random_msgs)
            self.obj.location.msg_contents(msg)
    
               
class TutorialNpc(Script):
    """
    This class represents the all the actions the tutorial npc you meet first in avaloria
    will have.  This npc exists merely to show the player the typical/most used commands
    and explain the lore somewhat.
    """
    def at_script_creation(self):
        self.persistent = True
        self.interval = 15
        self.start_delay = True
        
    def at_start(self):
        self.target = self.obj.db.target
        self.tutorial_started = False
        self.db.valid = True
        
    def is_valid(self):
        return self.db.valid

    def at_repeat(self):
        character = self.obj.db.target
        if character.db.attributes['alignment'] is None:
            return
        if self.tutorial_started is False:
            self.tutorial_started = True
            self.message = 1
            self.obj.tell_character(self.obj.db.target, "Hello there %s!  Looks like you are new in these parts.  Can you remember anything?" % self.obj.db.target.name)
        else:
            if self.message == 1: 
                long_message = """
I know why you are here.  Your God, %s sent you here.  He rebirthed you into the body 
you see before you now.  Times are dark in Avaloria young one.  The Deities wage war
upon not only each other, but each others followers.  Resources are scarce, and recently
the races who previously lived apart, with no interaction are coming to meet each other
for the first time in their recorded history.  You are tasked with spreading the word of
%s and amassing followers for their cause.
                """ % (character.db.attributes['deity'].title(), character.db.attributes['deity'].title())
                self.obj.tell_character(self.obj.db.target, long_message)
                self.message = 2
            elif self.message == 2:
                long_message = """
There are many challenges ahead of you, and many obstacles in your way. This plot of
land is gifted to you by your God.  It is your's to do what you will with it.  As you
can imagine, others covet this land.  They want it for their own, and more importantly
they want you out of the picture %s.  One of the many ways to enhance yourself is by
building up structures on this land and commiting to its defense.  You can do this
by calling upon the creation powers gifted to you by %s. (help @construct for details.)
                """ % (character.name, character.db.attributes['deity'])
                self.obj.tell_character(character, long_message)
                self.message = 3
            elif self.message == 3:
                long_message = """
Your deity has gifted you with a brief amount of their knowledge of the world.  This can
be referenced at any time by type help and hitting return.  This will give you a list of
command you may use to do things within the world of Avaloria.  To see the help entry for
a specific thing in the list, simply type help <item to view> where item to view is one of
valid commands (you don't need the carot's).  Try it now.
                """
                self.obj.tell_character(character, long_message)
                self.message = 4
            elif self.message == 4:
                long_message = """
Good, good.  Still so much to learn yet though my friend.  You are stark naked currently.
Let's fix that for you, shall we?"
                """
                self.obj.tell_character(character, long_message)
                clothes = create.create_object(Armor, key="Commoner Clothing", location=self.obj)
                clothes.db.armor_rating = 1
                clothes.db.desc = "Typical common outfit for an Avalorian, made from cloth."
                clothes.db.attribute_bonuses = {}
                clothes.move_to(character) 
                character.msg("The old man hands you a parcel of clothing.")
                self.obj.tell_character(character, "Use the {b[equip}{n {mcommand to put some clothes on.  (help equip).")
                self.obj.tell_character(character, "Also you may view your inventory with the 'inventory' command.")
                self.message = 5
            elif self.message == 5:
                long_message = """
Now that you are decent, we need to talk about your attributes.  You can view them with the
'show' command.  Try 'show attributes'.  You can also see some miscellaneous statistics with
'show stats'.  Once you learn skills, 'show skills' will list all the skills you have, and 
their levels.  Speaking of skills, here take this.
                """
                self.obj.tell_character(character, long_message)
                time.sleep(1)
                kick_training = create.create_object(TrainingBook, key="Training Manual: Kick", location=self.obj)
                kick_training.db.skill = 'kick'
                character.msg ("The old man hands you a leather bound book, worn around the edges.")
                kick_training.move_to(character)
                long_message = """
All skills in this world are learned by reading and understanding their use in their manuals
and training books.  Common skills will drop from low level monsters/opponents, while the more
powerful skills can only be attained by class specialization quests or boss drops.  Many evil
and good creatures alike covet these books. To learn the skill simply type 'use <book name>'.
So in this case: 'use training manaual: kick'. (help skills for more detailed information)
                """
                self.obj.tell_character(character, long_message)
                self.message = 6
            elif self.message == 6:
                long_message = """ I shall take my leave from you now, I imagine our paths shall
cross again one day, young one.  Remember, any help you need you can receive from your in game
help menu.  Just type 'help' and hit enter.
                """
                self.obj.tell_character(character, long_message)
                limbo = self.obj.search("Limbo", global_search=True)
                self.obj.move_to(limbo)
                self.db.valid = False
                self.obj.scripts.validate()       

