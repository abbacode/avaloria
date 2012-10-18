#HEADER
from src.utils import create, search
from game.gamesrc.objects.world.quests import Quest

#CODE (Generating quests)

storage = search.objects('storage')[0]
copy_dir = '/var/mud/evennia/game/gamesrc/copy/'
tutorial_quest = create.create_object(Quest, key="Tutorial Slaughter", location=storage)
tutorial_quest.set_description('%squests/tutorial1.txt' % copy_dir)
tutorial_quest.db.gold_reward = 50
tutorial_quest.db.exp_reward = 200
objective = { 'objective_name': 'Kill something Evil.',  'counter': 0, 'threshold': 1, 'completed': False, 'type': 'kill' }
tutorial_quest.add_objective(objective)

tutorial_quest = create.create_object(Quest, key="Tutorial Gather", location=storage)
tutorial_quest.set_description('%squests/tutorial_gather.txt' % copy_dir)
tutorial_quest.db.gold_reward = 25
tutorial_quest.db.exp_reward = 300
objective = { 'objective_name': 'Gather an Item.', 'counter': 0, 'threshold': 1, 'completed': False, 'type': 'gather_weapon' }
tutorial_quest.add_objective(objective)

#CODE (Marshlands Quests)
storage = search.objects('storage')[0]
copy_dir = '/var/mud/evennia/game/gamesrc/copy/'

slythain_nuisance = create.create_object(Quest, key="Have You Met The Slythain?", location=storage)
slythain_nuisance.set_description("%s/quests/slythain_nuisance.txt" % copy_dir)
slythain_nuisance.short_description = "Kill Slythain Soldiers"
slythain_nuisance.db.level = 3
slythain_nuisance.db.gold_reward = 45
slythain_nuisance.db.exp_reward = 255
slythain_nuisance.db.faction = 'warden'
slythain_nuisance.db.faction_reward = 15
slythain_nuisance.db.exclusions = "deity:slyth"
objective = { 'objective_name': 'Kill 3 Slythain', 'counter': 0, 'threshold': 3, 'completed': False, 'type': 'kill_slythain' }
slythain_nuisance.add_objective(objective)

quest = create.create_object(Quest, key="Hunt The Hunters", location=storage)
quest.db.short_description = "Kill Slythain Hunters"
quest.set_description('%s/quests/hunt_the_hunters.txt' % copy_dir)
quest.db.level = 3
quest.db.gold_reward = 75
quest.db.exp_reward = 450
quest.db.faction = 'warden'
quest.db.faction_reward = 30
quest.db.exclusions = "deity:slyth"
quest.db.prereq = "Have You Met The Slythain?"
objective = {'objective_name': 'Kill 5 Slythain Hunters', 'counter': 0, 'threshold': 5, 'completed': False, 'type': ['kill_young slythain hunter', 'kill_mature slythain hunter', 'kill adolescent_slythain hunter'] }
quest.add_objective(objective)

warden_nuisance = create.create_object(Quest, key="Have You Met The Green Warden?", location=storage)
warden_nuisance.db.short_description = 'Kill Warden soldiers'
warden_nuisance.set_description('%s/quests/warden_nuisance.txt' % copy_dir)
warden_nuisance.db.level = 3
warden_nuisance.db.gold_reward = 45
warden_nuisance.db.exp_reward = 255
warden_nuisance.db.faction = 'slyth'
warden_nuisance.db.faction_reward = 15
warden_nuisance.db.exclusions = "deity:green warden"
objective = { 'objective_name': 'Kill 3 Warden Creatures', 'counter': 0, 'threshold': 3, 'completed': False, 'type': 'kill_warden'}
warden_nuisance.add_objective(objective)

find_necklace = create.create_object(Quest, key="An Item Of Importance", location=storage)
find_necklace.db.short_description = 'Find the Family heirloom.'
find_necklace.set_description('%s/quests/item_of_importance.txt' % copy_dir)
find_necklace.db.gold_reward = 100
find_necklace.db.level = 4
find_necklace.db.prereq = 'Have You Met The Slythain?;Have You Met The Green Warden?'
find_necklace.db.exp_reward = 300
find_necklace.db.faction = ['karith', 'warden', 'kaylynne', 'slyth']
find_necklace.db.faction_reward = 45
find_necklace.db.exclusions = "none:none"
objective = { 'objective_name': 'Find Julianne\'s Family Heirloom', 'counter': 0, 'threshold': 1, 'completed': False, 'type': 'gather_family heirloom'}
find_necklace.add_objective(objective)

light_in_the_dark = create.create_object(Quest, key="Light In The Dark", location=storage)
light_in_the_dark.short_description = 'Kill Creatures in Marshlands.'
light_in_the_dark.aliases = ['light in the dark', 'light in', 'Light In The Dark']
light_in_the_dark.set_description("%s/quests/light_in_the_dark.txt" % copy_dir)
light_in_the_dark.db.level = 4
light_in_the_dark.db.gold_reward = 40
light_in_the_dark.db.exp_reward = 300
light_in_the_dark.db.exclusions = "none:none"
light_in_the_dark.db.faction = 'karith'
light_in_the_dark.db.faction_reward = 20
objective = { 'objective_name': 'Kill 10 creatures within the marshlands', 'counter': 0, 'threshold': 10, 'completed': False, 'type': 'kill_marshlands' }
light_in_the_dark.add_objective(objective)

kill_synesh = create.create_object(Quest, key="A Terrible Menace", location=storage)
kill_synesh.short_description = 'Kill Synesh Algreense'
kill_synesh.aliases = ['kill_synesh algreense', 'a terrible menace', 'A TERRIBLE MENACE']
kill_synesh.set_description("%s/quests/a_terrible_menace.txt" % copy_dir)
kill_synesh.db.prereq = 'Light In The Dark'
kill_synesh.db.gold_reward = 125
kill_synesh.db.level = 5
kill_synesh.db.exclusions = "deity:slyth"
kill_synesh.db.exp_reward = 450
kill_synesh.db.faction = 'warden'
kill_synesh.db.faction_reward = 40
objective = {'objective_name': 'Kill Synesh Algreense', 'counter': 0, 'threshold': 1, 'completed': False, 'type': 'kill_synesh algreense',}
kill_synesh.add_objective(objective)

deity_seal = create.create_object(Quest, key="Seal Of Seals", location=storage)
deity_seal.short_description = 'Find the Deity Seal'
deity_seal.aliases = ['seal of seals', 'SEAL OF SEALS']
deity_seal.set_description("%s/quests/seal_of_seals.txt" % copy_dir)
deity_seal.gold_reward = 20
deity_seal.db.exp_reward = 75
deity_seal.db.exclusions = "none:none"
deity_seal.db.faction = [ 'warden', 'slyth', "karith", 'kaylynne' ]
deity_seal.db.faction_reward = 25
objective = {'objective_name': 'Find the deity Seal.', 'counter': 0, 'threshold': 1, 'completed': False, 'type': 'gather_deity seal'}
deity_seal.add_objective(objective)

dark_places = create.create_object(Quest, key="Dark Places", location=storage)
dark_places.short_descrption = 'Kill the Unnatural'
dark_places.aliases = ['dark places', 'DARK PLACES']
dark_places.set_description("%s/quests/dark_places.txt" % copy_dir)
dark_places.db.gold_reward = 100
dark_places.db.exclusions = "none:none"
dark_places.db.exp_reward = 200
dark_places.db.faction = 'karith'
dark_places.db.faction_reward = 50
objective = {'objective_name': 'Kill 3 Dungeon Creatures', 'counter': 0, 'threshold': 3, 'completed': False, 'type': 'kill_crypt_mobs kill_ruins_mobs' }
dark_places.add_objective(objective)
objective2 = {'objective_name': 'Kill the Leader of the Enclave', 'counter': 0, 'threshold': 1, 'completed': False, 'type': 'kill_boss_mob' }
dark_places.add_objective(objective2)

unnatural_things = create.create_object(Quest, key="Unnatural Things", location=storage)
unnatural_things.short_description = "Kill the unnatural"
unnatural_things.aliases = ['unnatural things']
unnatural_things.set_description('%s/quests/unnatural_things.txt' % copy_dir)
unnatural_things.db.prereq = 'Dark Places'
unnatural_things.db.gold_reward = 150
unnatural_things.db.level = 2
unnatural_things.db.exclusions = "none:none"
unnatural_things.db.repeatable = True
unnatural_things.db.exp_reward = 250
unnatural_things.db.faction = 'karith'
unnatural_things.db.faction_reward = 65
objective = {'objective_name': 'Kill 10 Unnatural Beings in a dungeon', 'counter': 0, 'threshold': 10, 'completed': False, 'type': 'kill_dungeon_mobs'}
unnatural_things.add_objective(objective)

kill_heroes = create.create_object(Quest, key="A Few Good Men", location=storage)
kill_heroes.short_description = 'Kill 3 Boss mobs.'
kill_heroes.aliases = ['few good men']
kill_heroes.set_description('%squests/a_few_good_men.txt' % copy_dir)
kill_heroes.db.prereq = 'Dark Places'
kill_heroes.db.gold_reward = 65
kill_heroes.db.level = 2
kill_heroes.db.exclusions = "none:none"
kill_heroes.db.exp_reward = 300
kill_heroes.db.faction = 'karith'
kill_heroes.db.faction_reward = 65
objective = {'objective_name': 'Kill 3 Boss Mobs', 'counter': 0, 'threshold': 3, 'completed': False, 'type': 'kill_boss_mob'}
kill_heroes.add_objective(objective)
objective = {'objective_name': 'Loot a Rare Weapon', 'counter': 0, 'threshold': 1, 'completed': False, 'type': 'loot_rare_item'}
kill_heroes.add_objective(objective)

structure_quest = create.create_object(Quest, key="Construct a Mine", location=storage)
structure_quest.short_description = 'Build a Mine.'
structure_quest.aliases = ['structure quest', 'STRUCTURE QUEST']
structure_quest.set_description("%squests/build_a_mine.txt" % copy_dir)
structure_quest.db.gold_reward = 25
structure_quest.db.prereq = 'Dark Places'
structure_quest.db.exp_reward = 165
structure_quest.db.exclusions = "none:none"
structure_quest.db.faction = ['warden', 'slyth', 'karith', 'kaylynne']
structure_quest.db.faction_reward = 50
objective = {'objective_name': 'Build a Gold Mine', 'counter': 0, 'threshold': 1, 'completed': False, 'type': 'build_gold_mine' }
structure_quest.add_objective(objective)

structure_quest = create.create_object(Quest, key="Construct a Training Grounds", location=storage)
structure_quest.short_description = "Build the Training Grounds"
structure_quest.aliases = ['structure quests']
structure_quest.set_description("%squests/build_training_grounds.txt" % copy_dir)
structure_quest.db.gold_reward = 50
structure_quest.db.prereq = 'Construct A Mine'
structure_quest.db.level = 2
structure_quest.db.exp_reward = 200
structure_quest.db.exclusions = "none:none"
structure_quest.db.faction = ['warden', 'slyth', 'karith', 'kaylynne']
structure_quest.db.faction_reward = 85
objective = {'objective_name': 'Build a Training Grounds', 'counter': 0, 'threshold': 1, 'completed': False, 'type': 'build_training_ground'}
structure_quest.add_objective(objective)

structure_quest = create.create_object(Quest, key="Improve Defenses", location=storage)
structure_quest.short_description = "Build Defenses and Fortifications"
structure_quest.aliases = ['structure quests']
structure_quest.set_description('%squests/build_defenses.txt' % copy_dir)
structure_quest.db.gold_reward = 75
structure_quest.db.prereq = 'Construct a Training Grounds'
structure_quest.db.exp_reward = 300
structure_quest.db.level = 2
structure_quest.db.exclusions = "none:none"
structure_quest.db.faction = ['warden', 'slyth', 'karith', 'kaylynne']
structure_quest.db.faction_reward = 110
objective = {'objective_name': 'Improve your defenses!', 'counter': 0, 'threshold': 1, 'completed': False, 'type': 'build_defenses' }
structure_quest.add_objective(objective)

structure_quest = create.create_object(Quest, key="Structures Need Love Too", location=storage)
structure_quest.short_description = "Level one of your structures."
structure_quest.aliases = ['structure quests']
structure_quest.set_description('%squests/structures_need_love.txt' % copy_dir)
structure_quest.db.gold_reward = 100
structure_quest.db.prereq = 'Construct a Training Grounds'
structure_quest.db.exp_reward = 400
structure_quest.db.level = 2
structure_quest.db.exclusions = "none:none"
structure_quest.db.faction = ['warden', 'slyth', 'karith', 'kaylynne']
structure_quest.db.faction_reward = 150
objective = {'objective_name': 'Level a structure!', 'counter': 0, 'threshold': 1, 'completed': False, 'type': 'level_structure' }
structure_quest.add_objective(objective)

tut_speak = create.create_object(Quest, key="Speak And Be Heard", location=storage)
tut_speak.short_description = "Speak in OOC chat."
tut_speak.aliases = ['tutorial quests']
tut_speak.set_description('%squests/speak_and_be_heard.txt' % copy_dir)
tut_speak.db.gold_reward = 100
tut_speak.db.exp_reward = 100
tut_speak.db.exclusions = "none:none"
tut_speak.db.faction = ['warden', 'slyth', 'karith', 'kaylynne']
tut_speak.db.faction_reward = 100
objective = {'objective_name': 'Use the ooc command to speak in the global public channel', 'counter': 0, 'threshold': 3, 'completed': False, 'type': 'use_public'}
tut_speak.add_objective(objective)

tut_skills = create.create_object(Quest, key="Learning New Skills", location=storage)
tut_skills.short_description = "Learn a new Skill."
tut_skills.aliases = ['tutorial quests']
tut_skills.set_description('%squests/learn_a_new_skill.txt' % copy_dir)
tut_skills.db.gold_reward = 115
tut_skills.db.exp_reward = 100
tut_skills.db.exclusions = "none:none"
tut_skills.db.faction = ['warden', 'slyth', 'karith', 'kaylynne']
tut_skills.db.faction_reward = 100
objective = {'objective_name': 'Use a training book to learn a new skill.', 'counter': 0, 'threshold': 1, 'completed': False, 'type': 'use_use training manual'}
tut_skills.add_objective(objective)

tut_lspells = create.create_object(Quest, key="Learning Spells", location=storage)
tut_lspells.short_description = "Learn a new Spell."
tut_lspells.aliases = ["tutorial quests"]
tut_lspells.set_description('%squests/learn_a_spell.txt' % copy_dir)
tut_lspells.db.gold_reward = 100
tut_lspells.db.exp_reward = 125
tut_lspells.db.exclusions = "none:none"
tut_lspells.db.faction = ["warden", "slyth", "karith", "kaylynne"]
tut_lspells.db.faction_reward = 150
objective = {'objective_name': 'Use a spell tome to learn a spell.', 'counter': 0, 'threshold': 1, 'completed': False, 'type': 'use_use spell tome'}
tut_lspells.add_objective(objective)

tut_iskills = create.create_object(Quest, key="Increasing Skills", location=storage)
tut_iskills.short_description = "Use the 'skills' command to increaase a skill"
tut_iskills.aliases = ['tutorial quests']
tut_iskills.set_description("%squests/increasing_skills.txt" % copy_dir)
tut_iskills.db.gold_reward = 100
tut_iskills.db.exp_reward = 100
tut_iskills.db.exclusions = "none:none"
tut_iskills.db.faction = ['warden', 'slyth', 'karith', 'kaylynne']
tut_iskills.db.faction_reward = 150
objective = {'objective_name': 'Use the \'skills\' command to increase a skill', 'counter': 0, 'threshold': 1, 'completed': False, 'type': 'use_skills'}
tut_iskills.add_objective(objective)

tut_battle = create.create_object(Quest, key="Battle On!", location=storage)
tut_battle.short_description = "Kill the Battle Dummy!"
tut_battle.aliases = ['tutorial quests']
tut_battle.set_description("%squests/battle_on.txt" % copy_dir)
tut_battle.db.gold_reward = 100
tut_battle.db.exp_reward = 100
tut_battle.db.exclusions = "none:none"
tut_battle.db.faction = ['warden', 'slyth', 'karith', 'kaylynne']
tut_battle.db.faction_reward = 150
objective = {'objective_name': 'Kill the Battle Dummy', 'counter': 0, 'threshold': 1, 'completed': False, 'type': 'kill_battle dummy'}
tut_battle.add_objective(objective)
