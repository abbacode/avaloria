import random
from src.utils import create, utils
from game.gamesrc.objects.baseobjects import Object
from game.gamesrc.objects import copyreader


class QuestManager(Object):
    """
    This object is attached to the character and manages all quests received.
    """

    def at_object_creation(self):
        """
        Set some typical attributes from the management object.
        """
        self.db.active_quests = {}
        self.db.completed_quests = {}
        self.db.to_remove_in_active = {}
        self.db.character = None
        self.db.is_equipped = False
        

    def add_quest(self, quest_to_add):
        active_quests = self.db.active_quests
        active_quests['%s' % quest_to_add.name] = quest_to_add
        self.db.active_quests = active_quests

    def complete_quest(self, quest_to_remove):
        character = self.db.character
        character.msg("{yYou have completed the quest: %s!{n" % quest_to_remove.name)
        if quest_to_remove.db.exp_reward is not None:
            character.award_exp(quest_to_remove.db.exp_reward)
        
        if quest_to_remove.db.gold_reward is not None:
            character.award_gold(quest_to_remove.db.gold_reward)
        
        if quest_to_remove.db.loot_reward is not None:
            for item in quest_to_remove.db.loot_reward:
                item.move_to(character, quiet=False)

      
        if quest_to_remove.db.faction_reward is not None:
            print "trying deity faction crap"
            if not hasattr(quest_to_remove.db.faction, 'lower'):
                print "trying faction_indexing"
                if character.db.attributes['deity'] in "an'karith":
                    faction_index = quest_to_remove.db.faction.index("karith")
                elif character.db.attributes['deity'] in "green warden":
                    faction_index = quest_to_remove.db.faction.index("warden")
                else:
                    faction_index = quest_to_remove.db.faction.index(character.db.attributes['deity'])

                faction = quest_to_remove.db.faction[faction_index]
                print faction_index
                print faction
            else:
                faction = quest_to_remove.db.faction
                print faction
            if "an'karith" in faction:
                faction = 'karith'
            elif "green warden" in faction:
                faction = "warden"
            factions = character.db.factions
            factions[faction] += factions[faction] + quest_to_remove.db.faction_reward
            character.db.factions = factions
       
            
        quest_to_remove.db.completed = True
        completed_quests = self.db.completed_quests
        completed_quests[quest_to_remove.name] = quest_to_remove
        self.db.to_remove_in_active[quest_to_remove.name] = quest_to_remove
        self.db.completed_quests = completed_quests
        
    def complete_quest_objective(self, quest, objective):
        character = self.db.character
        character.msg("{yYou have completed a quest objective for %s!{n" % quest.name)
        quest.complete_objective(objective)
        
    def cleanup_completed_quests(self):
        to_remove = self.db.to_remove_in_active
        if len(self.db.to_remove_in_active) > 0:
            for quest in self.db.to_remove_in_active:
                print "attempting to remove the quest from active quests"
                self.remove_quest(self.db.to_remove_in_active[quest])
        to_remove = {}
        self.db.to_remove_in_active = to_remove

    def remove_quest(self, quest_to_remove):
        active_quests = self.db.active_quests
        del active_quests[quest_to_remove.name]
        self.db.active_quests = active_quests

    def check_quest_flags(self, mob=None, item=None):
        character = self.db.character
        print character.db.lair.db.structure_manager_id
        structure_manager = self.search(character.db.lair.db.structure_manager_id, location=character.db.lair, global_search=False)
        active_quests  = self.db.active_quests
        active_quests_temp = active_quests
        print "DEBUG->QuestManager.check_quest_flags: Checking active quests"
        for quest in active_quests_temp:
            quest_obj = active_quests[quest]
            quest_objectives = quest_obj.db.objectives
            print "DEBUG->QuestManager.check_quest_flags: Checking objectives for %s" % quest_obj.name
            for objective in quest_objectives:
                print "DEBUG->QuestManager.check_quest_flags: Checking %s" % objective
                if quest_objectives[objective]['completed']:
                    print "DEBUG->QuestManager.check_quest_flags: skipping"
                    continue
                if mob is not None:
                    if 'kill_%s' % mob.db.mob_type in quest_objectives[objective]['type']:
                        if 'kill_%s' % mob.db.mob_type in mob.aliases:
                            quest_obj.tick_counter_objective(objective, caller=self.db.character)
                    elif '%s' % quest_objectives[objective]['type'] in mob.aliases:
                        quest_obj.tick_counter_objective(objective, caller=self.db.character)
                    elif 'kill_%s' % mob.name.lower() in quest_objectives[objective]['type']:
                        quest_obj.tick_counter_objective(objective, caller=self.db.character) 
                    elif 'boss_mob' in mob.aliases and 'kill_boss' in quest_objectives[objective]['type']:
                        quest_obj.tick_counter_objective(objective, caller=self.db.character)
                    elif 'kill_%s' % mob.db.deity in quest_objectives[objective]['type']:
                        quest_obj.tick_counter_objective(objective, caller=self.db.character) 
                    elif 'kill_%s' % mob.location.db.dungeon_type in quest_objectives[objective]['type']:
                        quest_obj.tick_counter_objective(objective, caller=self.db.character)
                    elif 'kill' in quest_objectives[objective]['type']:
                        if 'kill' in mob.aliases and 'counter' in quest_objectives[objective].keys():
                            quest_obj.tick_counter_objective(objective, caller=self.db.character)                
                    
                if item is not None:
                    if 'gather_%s' % item.db.type in quest_objectives[objective]['type']:
                        quest_obj.tick_counter_objective(objective, caller=self.db.character)
                    elif 'gather_%s' % item.name.lower() in quest_objectives[objective]['type']:
                        quest_obj.tick_counter_objective(objective, caller=self.db.character)
                    elif 'build' in quest_objectives[objective]['type']:
                        if 'gold_mine' in quest_objectives[objective]['type']:
                            if "Gold Mine" in structure_manager.db.already_built:
                                quest_obj.tick_counter_objective(objective, caller=character)

                    
        self.cleanup_completed_quests()
                            
#    def check_prereqs(self):
          
    def find_quest(self, quest):
        active_quests = self.db.active_quests
        if quest in active_quests:
            quest = active_quests[quest]
            return quest
        else:
            return None

    def quest_log_short_display(self, caller):
        active_quests = self.db.active_quests
        if len(active_quests) < 1:
            caller.msg("You have no active quests currently.")
            return
        titles = '{{c{0:<25} {1:<65} {2:<5}{{n'.format('Name', 'Description', 'Level')
        caller.msg(titles)
        caller.msg('{C-----------------------------------------------------------------------------------------------------{n')
        m = ""
        for quest in active_quests:
            quest_obj = active_quests[quest]
            m += '{{C{0:<25}{{n {1:<65} {2}\n{{n'.format(utils.crop(quest_obj.name,width=25), quest_obj.db.short_description, quest_obj.db.quest_level) 
        caller.msg(m)
        caller.msg('{C-----------------------------------------------------------------------------------------------------{n')
        caller.msg("For more detailed information, try help <questname>")
   
    def completed_quests_view(self, caller):
        completed_quests = self.db.completed_quests
        completed_number = len(completed_quests)
        if len(completed_quests) < 1:
            caller.msg("You have no completed quests.")
            return
        titles = '{{c{0:<25} {1:<30} {2}{{n'.format('Name', 'Description', 'Level')
        caller.msg(titles)
        caller.msg('{c--------------------------------------------------------------------{n')
        m = ""
        for quest in completed_quests:
            quest_obj = completed_quests[quest]
            m += '{{C{0:<25}{{n {1:<30} {2}\n{{n'.format(quest_obj.name, quest_obj.db.short_description, quest_obj.db.quest_level)
        caller.msg(m)
        caller.msg('{c--------------------------------------------------------------------{n')
        caller.msg("{CCompleted Quests:{n %s" % completed_number)
        

    def quest_objectives_display(self, caller, quest):
        caller.msg("%s" % quest.title())
        quest = self.find_quest(quest.title())
        if quest is None:
            caller.msg("You are not on any quest named: %s" % quest)
            return
        else:
            titles = '{0:<25} {1:<10}'.format('Short Description', 'Progress')
            caller.msg(titles)
            caller.msg("{c------------------------------------------------------------------")
            objectives_message = quest.format_objectives()
            caller.msg(objectives_message)
            caller.msg("{c------------------------------------------------------------------")

    
class Quest(Object):
    """
    Typical quest object.
    """
    def at_object_creation(self):
        self.db.level_requirement = 1
        self.db.prereq = None
        self.db.repeatable = False
        self.db.gold_reward = 10
        self.db.exp_reward = 10
        self.db.loot_reward = []
        self.db.faction_reward = 10
        self.db.faction = None
        self.db.objectives = {}
        self.db.quest_level = 1
        self.db.quest_type = None
        self.db.long_description = ""
        self.db.short_description = "Something short, and sweet"
        self.db.exclusions = None
        self.db.completed = False

    def set_quest_aliases(self):
        if 'kill' in self.db.quest_type:
            self.aliases = ['kill']
        elif 'gather' in self.db.quest_type:
            self.aliases = ['gather']
        elif 'fedex' in self.db.quest_type:
            self.aliases = ['fedex']
        elif 'explore' in self.db.quest_type:
            self.aliases = ['explore']
        
    def add_objective(self, objectives_dict):
        objectives = self.db.objectives
        objectives[objectives_dict['objective_name']] = objectives_dict
        self.db.objectives = objectives
    
    def complete_objective(self, objectives, objective, caller):
        objectives[objective]['completed'] = True
        print objectives
        caller.msg("{yYou have completed a quest objective!{n")
        self.check_objectives(objectives,caller)

    def tick_counter_objective(self, objective, caller):
        objectives = self.db.objectives
        objectives[objective]['counter'] = objectives[objective]['counter'] + 1
        caller.msg("{yQuest objective advanced! %s: %s/%s{n" % (objectives[objective]['objective_name'], objectives[objective]['counter'], objectives[objective]['threshold']))
        if objectives[objective]['counter'] > objectives[objective]['threshold']:
            objectives[objective]['counter'] = objectives[objective]['threshold']

        if objectives[objective]['counter'] >= objectives[objective]['threshold']:
            self.complete_objective(objectives, objective, caller)
        self.db.objectives = objectives

    def check_objectives(self, objectives, caller):
        quest_log = caller.db.quest_log
        is_false = False
        for objective in objectives:
            if objectives[objective]['completed'] is False:
                is_false = True
                return
        if is_false is not True:
            self.db.completed = True
            quest_log.complete_quest(self)
    
    def set_description(self, copy_file):
        self.db.long_description = copyreader.read_file(copy_file)
        
        
    def add_help_entry(self):
        entry = create.create_help_entry(self.name, self.db.long_description, category="Quests", locks="view:holds(%s)" % self.name)
        
    def format_objectives(self):
        objectives = self.db.objectives
        m = ""
        for objective in objectives:
            m += '{{C{0:<30}{{n {{r{1}/{2}{{n\n'.format(objectives[objective]['objective_name'], objectives[objective]['counter'], objectives[objective]['threshold'])
        return m 
    
