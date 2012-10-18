#HEADER
from src.utils import create, search

#CODE (Potions)
location = search.objects("storage")[0]
small_hp_potion = create.create_object("game.gamesrc.objects.world.items.Potion", location=location, aliases=['storage_potions'])
small_hp_potion.db.level = 1
small_hp_potion.db.effect = "healing"
small_hp_potion.db.attribute_affected = "hp"
small_hp_potion.db.value = 10
small_hp_potion.generate_item_stats()
medium_hp_potion = create.create_object("game.gamesrc.objects.world.items.Potion", location=location, aliases=['storage_potions'])
medium_hp_potion.db.level = 10
medium_hp_potion.db.effect = "healing"
medium_hp_potion.db.attribute_affected = "hp"
medium_hp_potion.db.value = 35
medium_hp_potion.generate_item_stats()
large_hp_potion = create.create_object("game.gamesrc.objects.world.items.Potion", location=location, aliases=['storage_potions'])
large_hp_potion.db.level = 20
large_hp_potion.db.effect = "healing"
large_hp_potion.db.attribute_affected = "hp"
large_hp_potion.db.value = 60
large_hp_potion.generate_item_stats()
strike = create.create_object("game.gamesrc.objects.world.skills.TrainingBook", location=location, aliases=['storage_skills'], key="Training Manual: Strike")
strike.db.desc = "A thick training manual which details the use and learning of a certain skill, granting the reader the ability to use said skill."
strike.db.skill = 'strike'
strike.db.value = 100
rend = create.create_object("game.gamesrc.objects.world.skills.TrainingBook", location=location, aliases=['storage_skills'], key="Training Manual: Rend")
rend.db.skill = 'rend'
rend.db.desc = "A thick training manual which details the use and learning of a certain skill, granting the reader the ability to use said skill."
rend.db.value = 150
brawling = create.create_object("game.gamesrc.objects.world.skills.TrainingBook", location=location, aliases=['storage_skills'], key="Training Manual: Brawling")
brawling.db.skill = 'brawling'
brawling.db.desc = "A thick training manual which details the use and learning of a certain skill, granting the reader the ability to use said skill."
brawling.db.value = 75
spellweaving = create.create_object("game.gamesrc.objects.world.skills.TrainingBook", location=location, aliases=['storage_skills'], key="Training Manual: Spellweaving")
spellweaving.db.skill = 'spellweaving'
spellweaving.db.desc = "A thick training manual which details the use and learning of a certain skill, granting the reader the ability to use said skill."
spellweaving.db.value = 175
toughness = create.create_object("game.gamesrc.objects.world.skills.TrainingBook", location=location, aliases=['storage_skills'], key="Training Manual: Toughness")
toughness.db.skill = 'toughness'
toughness.db.desc = "A thick training manual which details the use and learning of a certain skill, granting the reader the ability to use said skill."
toughness.db.value = 250
cripple = create.create_object("game.gamesrc.objects.world.skills.TrainingBook", location=location, aliases=['storage_skills'], key="Training Manual: Crippling Strike")
cripple.db.skill = 'cripple'
cripple.db.desc = "A thick training manual which details the use and learning of a certain skill, granting the reader the ability to use said skill."
cripple.db.value = 300
sb = create.create_object("game.gamesrc.objects.world.skills.TrainingBook", location=location, aliases=['storage_skills'], key="Training Manual: Shield Bash")
sb.db.skill = 'shield bash'
sb.db.desc = "A thick training manual which details the use and learning of a certain skill, granting the reader the ability to use said skill."
sb.db.value = 150
deity_seal = create.create_object("game.gamesrc.objects.world.items.Item", location=location, aliases=['deity seal', 'DEITY SEAL', 'starter_quests_items'], key="Deity Seal")
deity_seal.db.quest_item = True
deity_seal.db.desc = "A Red-Gold medallion with the known seal of your deity engraved on the face."
deity_seal.db.quest = "Seal Of Seals"
family_heirloom = create.create_object("game.gamesrc.objects.world.items.Item", location=location, aliases=['family heirloom', 'FAMILY HEIRLOOM'], key="Family Heirloom")
family_heirloom.desc = "A very bright gold necklace with a Large Karithian ruby set in the center of it."
family_heirloom.db.quest_item = True
family_heirloom.db.quest = "An Item Of Importance"
training_book = rend.copy()
training_book.name = "Training Manual"
training_book.db.quest_item = True
training_book.db.quest = "Learning New Skills"
spellbook = create.create_object("game.gamesrc.objects.world.spells.SpellBook", location=location, key="Spell Tome")
spellbook.db.quest_item = True
spellbook.db.spell = "mageshield"
spellbook.db.quest = "Learning Spells"


