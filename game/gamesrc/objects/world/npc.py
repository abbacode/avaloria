import random
from src.utils import utils, create
from gamesrc.objects.baseobjects import Object
from gamesrc.objects.menusystem import *
from gamesrc.objects.world.mob import Mob

class EnemyNpc(Mob):

    def at_object_creation(self):
        Mob.at_object_creation(self)
        self.db.roam = True
        self.db.dialogue = []
        self.db.combat_dialogue = []
        self.db.reanimate = False

    def death(self):
        self.db.pre_death_desc = self.db.desc
        self.db.desc = "A dead %s." % self.key
        self.db.pre_death_name = self.key
        self.key = "{rCorpse of %s{n" % self.key
        self.aliases = ['corpse', 'Corpse of %s' % self.key, self.key.lower()]
        self.db.lootable = True
        self.db.corpse = True
        self.db.reanimate = True
        self.db.in_combat = False
    
    def refresh_attributes(self):
        attributes = self.db.attributes
        attributes['temp_health'] = attributes['health']
        attributes['temp_mana'] = attributes['mana']
        self.db.attributes = attributes

    def reanimate(self):
        self.db.corpse = False
        self.db.lootable = False
        self.db.reanimate = False
        self.db.desc = self.db.pre_death_desc
        self.key = self.db.pre_death_name
        self.refresh_attributes()

    def roam(self):
        pass




    
class Npc(Object):

    def at_object_creation(self):
        """
        This is the default object that will be interacting with the character in the game
        world.  There are a few important bits here:
        trainer: Boolean value of whether this npc can train characters in skills.
        combatant: Boolean value of whether characters can attack this object.
        TODO: Tie in to attack command
        dialogue: A dictionary with scripted dialogue, i.e:
            dialogue = self.db.dialogue
            dialogue['first'] = 'some text to say first'
            dialogue['second'] = 'some text to say second'
            etc, etc.
        skills_trained: a list of strings representing the skills they can train.
        """
        self.aliases = ['npc_runner']
        self.db.desc = "Some type of being."
        self.db.race = 'human'
        self.db.attributes = { 'strength': 5, 'intelligence': 5, 'dexterity': 5, 'constitution': 5 }
        attributes = self.db.attributes
        attributes['health'] = ((self.db.attributes['constitution'] * 2) + 25)
        attributes['mana'] = self.db.attributes['intelligence'] * 2
        self.db.attributes = attributes
        attributes = self.db.attributes
        attributes['temp_health'] = self.db.attributes['health']
        attributes['temp_mana'] = self.db.attributes['mana']
        attributes['attack_rating'] = self.db.attributes['strength'] / 5
        attributes['armor_rating'] = self.db.attributes['dexterity'] / 5
        self.db.attributes = attributes
        self.db.real_name = self.name
        self.db.combatant = False
        self.db.trainer = True
        self.db.quest_giver = True
        self.db.merchant = True
        self.db.tutorial_npc = False
        self.db.merchant_type = None
        self.db.dialogue = {}
        self.db.skills_trained = ['kick', 'brawling', 'strike']
        self.db.quests = []
        self.db.target = None

    def do_dialog(self, caller, type):
        dialogue = self.db.dialogue
        if 'greeting' == type:
            message = dialogue['greeting']
            self.tell_character(caller, message)

    def update(self):
        if self.db.merchant:
            self.db.potions = self.search('storage_potions', global_search=True, ignore_errors=True)
            self.db.weapons = self.search('storage_weapons', global_search=True, ignore_errors=True)
            if len(self.contents) < 1:
                if 'potions' in self.db.merchant_type:
                    for item in self.potions:
                        merchant_copy = item.copy()
                        merchant_copy.name = item.name
                        merchant_copy.move_to(destination=self)
                elif 'weapons' in self.db.merchant_type:
                    for item in self.db.weapons:
                        merchant_copy = item.copy()
                        merchant_copy.name = item.name
                        merchant_copy.move_to(destination=self)

            rn = random.random()
            if rn < .02:
                random_msgs = ["{y%s shuffles their feet in boredom.{n" % self.name, "{y%s counts their earned money, smiling to themselves.{n" % self.name,
                            "{m%s whispers to you: So are you gonna buy something or stare at me all day?{n" % self.name ]
                msg = random.choice(random_msgs)
                self.location.msg_contents(msg)
                

    def dictate_action(self, caller, message):
        if 'train' in message or 'Train' in message:
            if self.db.trainer is True:
                self.train_character(caller)
            else:
                self.tell_character(caller, "I do not have anything to train you in.")
        elif 'quests' in message or 'quest' in message:
            self.create_quest_menu(caller)
            # just not sure yet what
        elif 'buy' in message or 'Buy' in message:
            self.create_merchant_menutree(caller)
        else:
            #try dialogue
            if len(self.db.dialogue.keys()) < 1:
                self.tell_character(caller, "I have nothing to say to the likes of you!")
            else:
                self.do_dialog(caller, type='greeting')
        
    def tell_character(self, caller, message):
        caller.msg("{b%s whispers{n:\n {C%s{n" % (self.name, message))

    def train_character(self, caller):
        self.create_trainer_menutree(caller)

    def create_trainer_menutree(self, caller):
        nodes = []
        have_skills = 0
        skills_and_costs = {}
        character_skills = [ i.name for i in caller.db.skills ]
        skills_i_can_train = []
        for skill in self.db.skills_trained:
            if skill in character_skills:
                skills_i_can_train.append('%s' % skill)

        for skill in caller.db.skills:
            skills_and_costs['%s'  % skill.name] = skill.db.cost_to_level
        skills_string = ''.join(["{b%s{n  Cost: {y%s{n gp\n" % (k.title(),v) for k, v in skills_and_costs.items()])
        skills_string = utils.dedent(skills_string)
        welcome_text = """
            Welcome {g%s{n!  I can train you in the following skills:
%s
        """ % (caller.name, skills_string)
        welcome_text = utils.dedent(welcome_text) 
        
        node0 = MenuNode("START", links=[k for k in skills_and_costs.keys()], linktexts=["Train %s" % k for k in skills_and_costs.keys()],  text=welcome_text)
        #do some logic to find out which skills the character has and add some nodes for them. 
        for skill in self.db.skills_trained:
            if skill in character_skills:
                have_skills = 1
                node = MenuNode("%s" % skill, links=['END'], linktexts=['Exit Training Menu'], code="self.caller.level_skill('%s')" % skill )
                #caller.msg("node.code looks like: %s" % node.code)
                nodes.append(node)
        #if we don't have skills then gracefully return.
        if have_skills != 1:
            self.tell_character(caller, "You have not trained any skills yet." % self.name)
            return
 
        nodes.append(node0)
        menu = MenuTree(caller=caller, nodes=nodes)
        
        menu.start()

    def create_merchant_menutree(self, caller):
        if len(self.contents) < 1:
            self.tell_character(caller, "I do not have anything for sale currently.")
            return
        nodes = []
        items_for_sale = self.contents
        character_attributes = caller.db.attributes
        items_string = '\n '.join(["{b%s{n   Cost: {y%s{n" % (i.name, i.value) for i in items_for_sale])
        welcome_text = """
            Hello there %s!  Browse my goods:
%s
        """ % (caller.name, items_string)
        welcome_text = utils.dedent(welcome_text)
        root_node = MenuNode("START", links=[i.name for i in items_for_sale], linktexts=["Buy %s" % i.name for i in items_for_sale], text=welcome_text)
        for item in items_for_sale:
            confirm_buy_node = MenuNode("buy-%s" % item.name, links=["END"], linktexts=['Exit Merchant Menu'], code="self.caller.buy_from_merchant(item='%s', merchant='%s')" % (item.name, self.name) ) 
            item_node = MenuNode("%s" % item.name, links=["buy-%s" % item.name, "START", "END"], linktexts=["Buy %s" % item.name, "Back to Merchant Inventory", "Exit Merchant Menu"], text="Do you want to buy the %s?" % item.name)
            nodes.append(confirm_buy_node)
            nodes.append(item_node)
        nodes.append(root_node)
        menu = MenuTree(caller=caller, nodes=nodes)
        menu.start()

    def sell_item(self, item, caller):
        if caller.db.attributes['gold'] < item.db.value:
            return
        msg = "{bYou purchase the {n%s {bfor {y%s{n{b gold.{n" % (item.name, item.db.value)
        self.tell_character(caller, msg)
        item.move_to(caller, quiet=False)
    
    def create_quest_menu(self, caller):
        if len(self.db.quests) < 1:
            self.tell_character(caller, "I have no work for you at the moment adventurer.")
            return
        nodes = []
        quests = self.db.quests
        checked_quests = []
        character = caller
        character_quest_log = character.db.quest_log
        active_quests = character_quest_log.db.active_quests
        completed_quests = character_quest_log.db.completed_quests
        storage = self.search('storage', global_search=True)
        for quest in quests:
            print quest
            quest_obj = storage.search('%s' % quest.title(), global_search=False, ignore_errors=True)[0]
            if quest_obj.db.repeatable:
                checked_quests.append(quest)
                continue
            if quest.lower() in [ q.lower() for q in active_quests.keys()]:
                continue
            if quest.lower() in [ q.lower() for q in completed_quests.keys()]:
                continue
            if quest_obj.db.prereq is not None:
                if quest_obj.db.prereq.title() not in completed_quests.keys():
                    continue 
                
            self.tell_character(caller, "%s quests in the list. %s" % (len(quests), quest))
            checked_quests.append(quest)
        if len(checked_quests) < 1:
            self.tell_character(caller, "I have no more work for you adventurer.")
            return
                 
        quests_string = '\n'.join(["{y!{n {g%s" % i for i in quests])
        welcome_text = """
Hello %s, my name is %s.  I am looking for some help with some things today, 
perhaps you could spare some time? 
        """ % (caller.name, self.db.real_name)
        root_node = MenuNode("START", links=[i for i in checked_quests], linktexts=["{y!{n %s" % i for i in checked_quests], text = welcome_text)
        for quest in checked_quests:
            caller.msg("Looking for: %s" % quest)
            quest_obj = storage.search('%s' % quest, global_search=False, ignore_errors=True)[0]
            caller.msg("%s" % quest_obj.name)
            confirm_quest_node = MenuNode("confirm-%s" % quest, links=['END'], linktexts=['Exit Quest Menu'], code="self.caller.accept_quest('%s')" % quest, text="You have accepted the quest!")
            quest_node = MenuNode("%s" % quest, links=['confirm-%s' % quest, 'START'], linktexts=['Accept %s' % quest, "I want to talk about something else."], text=quest_obj.db.long_description)
            nodes.append(confirm_quest_node)
            nodes.append(quest_node)
        nodes.append(root_node)
        menu = MenuTree(caller=caller, nodes=nodes)
        menu.start()
    
        