# Overview #

Quests in Avaloria are quite easy to develop and create, provided you use a quest archtype that is readily known by the objective parser.  If it is not, then you will need to add logic to the parser so it knows to look for what you want it to look for.  Currently the following archtypes are supported (for the most part).

  * Gather items
  * Kill (Specific npc's, mob types, mob names, mob deity etc etc)
  * Build Structure (Build a specific structure within the character lair)

Archtypes to be added:

  * Exploration
  * Delivery (FedEx)
  * Escort

As development progresses, largely any type of quest that can be dreamed up can be added in.


### Quest Objects ###

Quest objects are what the Quest Manager object manages.  This object holds a dictionary of quest objectives that it checks when called to do so.  The quest object also holds the experience award, gold award and physical loot reward for the particular quest.  Quests are designed to be able to be repeatable, thus allowing for daily quests. Exclusions can also be defined on the quest object (ex: deity restrictions).

The quest system heavily, heavily utilizes the underlying alias system used baked into the evennia server.  The alias system allows you to define aliases on an object, so that you can effectively tag things.  So for example if you have a quest with a type of 'kill\_undead', then you would want to set an alias on every undead mob of 'kill\_undead'.  The quest system checks to see if the mob killed, item picked up, building built (whatever the trigger is) is what the objective in the quest is looking for.  If it is, it increments the count on the objective.  If the count is equal to the threshold, then the objective is marked as completed.

Quests can have as many objectives as you the developer want it to have.  The only thing to keep in mind is that when the quest manager fires off its logic checks, it does check every objective in every quest.  While this is typically very fast, it is something that one needs to be aware of while coding.

The general workflow for building a quest is as follows:

  1. First, pull down the latest release of code and open up gamesrc/world/quests.py
    * This is the batchcode file that generates the back end quest objects for the world.  The game code then copies these master objects when a quest is given out.  Now its time to define your quest object.
  1. Add the quest to an npc (or create a new npc for the specific quest) in the gamesrc/world/backend\_npcs.py batchcode file.
    * This largely follows the same form as generating the quest object.  Just follow from previous npc's in the file.
  1. Make sure that whatever items, or mobs you need to have trigger the quest are tagged properly in their aliases.


Once the following is done, as long as you don't need to add any logic to the objective parser, you should be ready to test your quest out.  On your development machine wipe the avaloria data, and re-initialize.  Follow this [guide](WipeAvaloriaDev.md) to setup an easy way to purge and re-initialize the game world.

If anything fails, evennia will be pretty damn loud about it and you should be able to figure out where you went wrong pretty easily.


Example:

```
find_necklace = create.create_object(Quest, key="An Item Of Importance", location=storage)
find_necklace.db.short_description = 'Find the Family heirloom.'
find_necklace.set_description('%s/quests/item_of_importance.txt' % copy_dir)
find_necklace.db.gold_reward = 100
find_necklace.db.prereq = 'Have You Met The Slythain?;Have You Met The Green Warden?'
find_necklace.db.exp_reward = 300
find_necklace.db.faction = ['karith', 'warden', 'kaylynne', 'slyth']
find_necklace.db.faction_reward = 45
find_necklace.db.exclusions = "none:none"
objective = { 'objective_name': 'Find Julianne\'s Family Heirloom', 'counter': 0, 'threshold': 1, 'completed': False, 'type': 'gather_family heirloom'}
find_necklace.add_objective(objective)
```

A couple things about the above code:
  * The location is set to storage, which is the backend room that holds a ton of different things for the entire world.  when adding the quest object in this file, always set the location to storage.
  * The objective declaration above should always be used when describing objectives.
  * The part that triggers whether the quest objective is tracked is the 'type' piece.  This should be the same as the alias used on the in game objects for the particular quest, i.e. mobs for kill quests, items for gather quests, etc etc.