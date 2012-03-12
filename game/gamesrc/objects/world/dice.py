import random
from src.game.gamesrc.objects.baseobjects import Object


class Dice(Object):
	"Creates a dice objects with a given number of sides"
	self.sides = None
	
	def at_object_creation(self):
		self.db.desc = "Dice"

	def roll(self):
		roll = random.randrange(1, self.sides)	
		return roll
	
	def roll_x_times(self, times_to_roll):
		results = []
		for i in range(0,times_to_roll):
			roll = random.randrange(1, self.sides)
			results.add(roll)
		return results

