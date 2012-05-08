#HEADER
from src.utils import create, search


#CODE (Crossroads NPC's)
crossroads = search.objects("The Crossroads", global_search=True)[0]
storage = search.objects("storage", global_search=True)[0]
npc  = create.create_object("game.gamesrc.objects.world.npc.Npc", key="Lilith Arynesa (Traveling Merchant)", location=crossroads)
desc = "A short, stocky Erelanian women with blonde hair down to the middle of her back.  She is dressed in the typical clothing \n"
desc += "of a travelling merchant along with the various knap sacks of the trade holding all sorts of goods for passers by and \n"
desc += "remote village dwellers alike.  As you look at her she beams a smile at you.\n"
npc.desc = desc
npc.db.trainer = False
npc.db.merchant = True
npc.db.merchant_type = "potions;roaming"

blacksmith_room = search.objects("Hammer and Anvil", global_search=True)[0]
blacksmith = create.create_object("game.gamesrc.objects.world.npc.Npc", key="Romero Grijanse (Blacksmith)", location=blacksmith_room)
desc = "Romero is a typical earthen, not much said but a whole lot done.  He is a tall, stocky fellow with reddish blonde hair that\n "
desc += "rests in a brain on his back.  As you look at him, his facial expression does not change the slightest.\n"
blacksmith.desc = desc
blacksmith.db.quest_giver = False
blacksmith.db.trainer = False
blacksmith.db.merchant = True
blacksmith.db.merchant_type = "weapons_and_armor"

herbalist_room = search.objects("Henry's Herbs", global_search=True)[0]
herbalist = create.create_object("game.gamesrc.objects.world.npc.Npc", key="Henry the Hermit (Potions)", location=herbalist_room)
desc = "This small fellow doesn\'t look like any of the races you have encountered on your journeys.  The folks in camp said that\n "
desc += " he showed up very early during the creation of the Crossroads outpost and has been here ever since.  His greasy unkempt\n "
desc += " hair falls over his eyes, making it very hard to see much of his face at all.  As you look at him he mumbles under his\n "
desc += " in an indecipherable language.\n"
herbalist.desc = desc
herbalist.db.quest_giver = False
herbalist.db.trainer = False
herbalist.db.merchant = True
herbalist.db.merchant_type = 'potions'
 
quest_npc = create.create_object("game.gamesrc.objects.world.npc.Npc", key="Julianne Veriandes", location=crossroads)
desc = "This woman has dirt smudged on her face and through her hair, she has a look of panic painted across\n"
desc += "her fair skinned face. Her red hair is matted and frizzy.  As you look at her she waves you down \n"
desc += "quite frantically."
quest_npc.aliases = [quest_npc.key]
quest_npc.name = "{Y!{n %s" % quest_npc.key
quest_npc.desc = desc
quest_npc.db.quests = ['An Item Of Importance','Have You Met The Slythain?', 'Have You Met The Green Warden?'] 
quest_npc.db.merchant = False
quest_npc.db.trainer = False
quest_npc.db.quest_giver = True

quest_npc = create.create_object("game.gamesrc.objects.world.npc.Npc", key="Dark Robed Man", location=crossroads)
desc = "You almost did not notice this darkly clad figure standing within an alleyway formed by the Armorer\n"
desc +="and Alchemist shop.  You recognize the robes as those of a An'Karith Monk.  He notices you and beckons."
quest_npc.desc = desc
quest_npc.aliases = [quest_npc.key]
quest_npc.name = "{Y!{n %s" % quest_npc.key
quest_npc.db.real_name = "Riatheron Giroyn"
quest_npc.db.quests = ['Light In The Dark', 'A Terrible Menace']
quest_npc.db.merchant = False
quest_npc.db.trainer = False
quest_npc.db.quest_giver = True
#copy items from storage

enemy_npc = create.create_object("game.gamesrc.objects.world.npc.EnemyNpc", key="Synesh Algreense", location=storage)
desc = "This man is clad is green robes, from head to toe.  You see no visible skin anywhere. He currently\n"
desc += "does not seem to notice your presence.  He seems to be very deep in thought, as you can hear him\n"
desc += "frantically whispering to himself."
enemy_npc.db.desc = desc
enemy_npc.db.actions = {'greeting': 'Ah, so you have come to test the will and power of the almighty Ssslyth have you?', 'taunt': "And don't come back!", 'mock': "You hit like a girl anyways!"}
enemy_npc.db.combat_dialogue = ['You know not whatssss you do little onesss.', 'Yesss, this is as I have sseen.', 'Come, meet your doom']
enemy_npc.db.dialogue = ['Thissss cannot be...', 'Why hasss the masster forsaken me?', 'No, no, thiisss must be wrong.']
enemy_npc.db.rating = 'hero'
enemy_npc.db.attributes['level'] = 4
enemy_npc.generate_stats()
enemy_npc.generate_rewards()
enemy_npc.update_stats()

aspect_of_karith = create.create_object("game.gamesrc.objects.world.npc.Npc", key="Aspect of An'karith", location=storage)
desc = "This transluscent visage shows an old man, hunched over with a cane.  His white beard flows to the floor.  He looks upon you kindly."
aspect_of_karith.db.desc = desc
m = "Welcome young one, I have been expecting you to awake for some time now.  Avaloria is in grave danger young hero.\n"
m += "Currently the spiritual world is at war.  The newest God of our realm, Slyth has seemingly grown ever powerful\n"
m += "and has begun his assertion, or attempt at assertion of power.  The nearest lands are those of the Green Warden\n"
m += "so naturally those are the first he is attacking.  You play a very special part in all of this.  A very special\n"
m += "part indeed.  I have some tasks for you.  Ask me about {Gquests{n {Cto learn more."
aspect_of_karith.db.dialogue = { 'greeting': m }
aspect_of_karith.db.quests = ['Unnatural Things', 'Seal of Seals', 'Dark Places', 'Construct a Mine', 'Construct a Training Ground', 'A Few Good Men']
aspect_of_karith.db.merchant = False
aspect_of_karith.db.trainer = False
aspect_of_karith.db.quest_giver = True


aspect_of_karith = create.create_object("game.gamesrc.objects.world.npc.Npc", key="Aspect of Slyth", location=storage)
desc = "This transluscent visage shows an old man, hunched over with a cane.  His white beard flows to the floor.  He looks upon you kindly."
aspect_of_karith.db.desc = desc
m = "Welcome young one, I have been expecting you to awake for some time now.  Avaloria is in grave danger young hero.\n"
m += "Currently the spiritual world is at war.  The newest God of our realm, Slyth has seemingly grown ever powerful\n"
m += "and has begun his assertion, or attempt at assertion of power.  The nearest lands are those of the Green Warden\n"
m += "so naturally those are the first he is attacking.  You play a very special part in all of this.  A very special\n"
m += "part indeed.  I have some tasks for you.  Ask me about {Gquests{n {mto learn more."
aspect_of_karith.db.dialogue = { 'greeting': m }
aspect_of_karith.db.quests = ['Unnatural Things', 'Seal of Seals', 'Dark Places', 'Construct a Mine', 'Construct a Training Ground', 'A Few Good Men']
aspect_of_karith.db.merchant = False
aspect_of_karith.db.trainer = False
aspect_of_karith.db.quest_giver = True


aspect_of_karith = create.create_object("game.gamesrc.objects.world.npc.Npc", key="Aspect of Kaylynne", location=storage)
desc = "This transluscent visage shows an old man, hunched over with a cane.  His white beard flows to the floor.  He looks upon you kindly."
aspect_of_karith.db.desc = desc
m = "Welcome young one, I have been expecting you to awake for some time now.  Avaloria is in grave danger young hero.\n"
m += "Currently the spiritual world is at war.  The newest God of our realm, Slyth has seemingly grown ever powerful\n"
m += "and has begun his assertion, or attempt at assertion of power.  The nearest lands are those of the Green Warden\n"
m += "so naturally those are the first he is attacking.  You play a very special part in all of this.  A very special\n"
m += "part indeed.  I have some tasks for you.  Ask me about {Gquests{n {mto learn more."
aspect_of_karith.db.dialogue = { 'greeting': m }
aspect_of_karith.db.quests = ['Unnatural Things', 'Seal of Seals', 'Dark Places', 'Construct a Mine', 'Construct a Training Ground', 'A Few Good Men']
aspect_of_karith.db.merchant = False
aspect_of_karith.db.trainer = False
aspect_of_karith.db.quest_giver = True


aspect_of_karith = create.create_object("game.gamesrc.objects.world.npc.Npc", key="Aspect of the Green Warden", location=storage)
desc = "This transluscent visage shows an old man, hunched over with a cane.  His white beard flows to the floor.  He looks upon you kindly."
aspect_of_karith.db.desc = desc
m = "Welcome young one, I have been expecting you to awake for some time now.  Avaloria is in grave danger young hero.\n"
m += "Currently the spiritual world is at war.  The newest God of our realm, Slyth has seemingly grown ever powerful\n"
m += "and has begun his assertion, or attempt at assertion of power.  The nearest lands are those of the Green Warden\n"
m += "so naturally those are the first he is attacking.  You play a very special part in all of this.  A very special\n"
m += "part indeed.  I have some tasks for you.  Ask me about {Gquests{n {mto learn more."
aspect_of_karith.db.dialogue = { 'greeting': m }
aspect_of_karith.db.quests = ['Unnatural Things', 'Seal of Seals', 'Dark Places', 'Construct a Mine', 'Construct a Training Ground', 'A Few Good Men']
aspect_of_karith.db.merchant = False
aspect_of_karith.db.trainer = False
aspect_of_karith.db.quest_giver = True
