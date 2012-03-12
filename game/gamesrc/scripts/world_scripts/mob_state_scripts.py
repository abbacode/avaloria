import random
import cProfile
from src.utils import create, utils
from game.gamesrc.scripts.basescript import Script
from game.gamesrc.commands.world import character_cmdset as character_cmdset
from game.gamesrc.commands.world import combat_cmdset as combat_cmdset


class Kos(Script):
    """
    This mob state is used for overly hostile and aggresive mobs that attack anyone
    on sight regardless of faction, level, name, gender.  Like a boss.
    """

    def at_script_creation(self):
        self.persistent = True
        self.interval = 60 
        self.start_delay = True
        self.desc = "Keeps the mob aggressive"

    def at_start(self):
        self.db.characters = []

    def at_repeat(self):
        if self.obj.db.in_combat is True:
            return

        if self.obj.db.corpse is True:
            return
        things_around_me = self.obj.location.contents
        characters = self.db.characters 
        if len(things_around_me) >= 1:
            for thing in things_around_me:
                if thing.has_player is not False: 
                    characters.append(thing) 
        else:
            return

        if len(characters) > 0:
            character = random.choice(characters) 
            #make sure the character is still in the room.  there is a small chance the script
            #ran while they were, then they left after self.db.characters was compiled.
            character_check = self.obj.search(character.name, global_search=False)
            if character_check is None:
                return
            chance = random.random()
            if chance < 0.10:
                if character:
                    if character.db.in_combat is True:
                        return
                    self.obj.location.msg_contents("%s turns towards %s and readies their weapon." % (self.obj.name, character.name))
                    character.db.target = self.obj
                    self.obj.begin_attack(character)
                    self.obj.db.in_combat = True 
            else:
                return

    def is_valid(self):
        if self.obj.db.corpse is True:
            return False
        else:
            return True

class MobSentinel(Script):
    """
    Makes a mob tick, much like the character sentinel for players.
    """
    def at_script_creation(self):
        self.key = "mob_sentinel"
        self.desc = "keeps track of enemy actions"
        self.interval = 5
        self.persistent = True

    def at_repeat(self):
        effect_manager = self.obj.db.effect_manager
        #follow_list = self.obj.db.follow_list
        effect_manager.check_effects()
        if self.obj.db.in_combat is True:
            #find the target, if none then get out of combat
            target = self.obj.db.target
            if target is not None: 
                if target.db.in_combat is True:
                    pass
                else:
                    self.obj.db.in_combat = False
                    self.obj.db.target = None
            else:
                self.obj.db.in_combat = False
                return
        else:
            return

    def is_valid(self):
        if self.obj.db.corpse is True:
            return False
        else:
            return True
    
                
        
class Brute(Script):
    """
    This script controls the behavior of a brute type mob.
    These mobs are typically melee based, and very aggressvive.
    You would typically pair this with the Kos script.
    """

    def at_script_creation(self):
        self.persistent = True
        self.interval = 3 
        self.desc = "Controls the behavior of brutes."
    
    def at_start(self):
        self.db.counters = {}
        self.db.skill_used = False

    def at_repeat(self):
        mob_skills = self.obj.db.skills
        mob_spells = self.obj.db.spells
        player_map = self.obj.location.db.player_map
        counters = self.db.counters
        random_number = random.random()

        if self.obj.db.in_combat is False:
            return

        if self.db.skill_used is True:
            counters['skill'] += 1
            self.db.counters = counters
            if counters['skill'] >= counters['skill_threshold']:
                self.db.skill_used = False
                return
            else:
                return

        if random_number < .10:
            for skill in mob_skills:
                if 'strike' in skill.name:
                    skill.on_use(self.obj)
                    counters['skill'] = 0
                    counters['skill_threshold'] = 5
                    self.db.skill_used = True
                    self.db.counters = counters
        elif random_number < .15:
            for skill in mob_skills:
                if 'kick' in skill.name:
                    skill.on_use(self.obj)
                    counters['skill'] = 0
                    counters['skill_threshold'] = 5
                    self.db.skill_used = True
                    self.db.counters = counters
        else:
            return        


