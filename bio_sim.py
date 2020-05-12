"""

Biological system simulation using Simpy.

Stefano Mangini, UniPv, 2020.

"""
import simpy
import random
import statistics
import numpy as np

NUM_BLOB = 100 # Number of Blobs (the living creature poppulating the Environment).
TIME_TO_EAT = 120 # Average time to find food.
TIME_AFTER_EAT = 20 # Time interval for a blob to be hungry again, and go search for food.

INITIAL_FOOD = 70 # starting food availability in the environment
FODD_RATE_PRODUCTION = 70 # each day 100 more food is produced by the environment

DAY = 1440 # minutes in a day
DAYLIGHT = DAY/2 # time period during which blobs are active
NIGHTTIME = DAY - DAYLIGHT # blobs sleep during night
NUM_DAYS = 2 # Number of days of simulation

def time_to_food():
    """Return the time spent until a food item is found ."""
    #return max(int(random.normalvariate(TIME_TO_EAT, TIME_TO_EAT/2)),0)
    return random.randint(1, int(DAYLIGHT))

class Forest:
    """
    The Forest is the natural environment where the Blobs live.
    The each day in the simulation is divided in two: Daylight and Nighttime.
    The Forest starts with a limited food supply that the Blobs eat during Daylight in order to survive.
    At nightime, the blobs goes to sleep and the Forest grows new food.

    """
    def __init__(self, env):
         self.food = simpy.Container(env, init=INITIAL_FOOD) # capacity=100*INITIAL_FOOD
         self.time_proc = env.process(self.day_cycle(env))

    # Define the day to night cycle, and prints when they occur
    def day_cycle(self, env):
         while True:
             day = int(env.now/DAY)
             print(f'\nSTART OF DAY {day} (sim. time {env.now})')
             print(f' > Forest food level: {self.food.level} \n')
             yield env.timeout(DAYLIGHT) # Wait for the sun to set.

             print(f'\nNIGHTTIME STARTS at {env.now}')
             print(f' > Survived Blobs: {count_alive_blobs(Blob_list)}')
             yield env.process(self.food_growth(env)) # Food grows
             yield env.timeout(NIGHTTIME) # Wait for the sun to rise

    # New food is added to the Forest
    def food_growth(self, env):
            print(f' > Forest food level: {self.food.level}\n')
            new_food = FODD_RATE_PRODUCTION
            yield self.food.put(new_food)


class Blob:
    """
    A Blob is a living creature poppulating the Forest.
    Each blob can be either alive or dead, depending on its ability to search for food.
    If a Blob eats enough food during a day, it survives to the next day. Otherwise, it dies.

    The Blob only search for food during Daylight. When the nighttime arrives, it goes to sleep.


    """
    def __init__(self, env, forest, name):
        self.env = env
        self.name = name # Name of the blob

        self.alive = True # Denotes the Blob's state: alive or dead
        self.isHunting = True # Denotes if the Blob is searching for food
        self.food_requirements = 1 # Minimum food to eat per day to survive
        self.food_eaten = 0 # Amount of food eaten during the current day

        self.sleep_proc = env.process(self.sleep(env))
        self.hunt_proc = env.process(self.hunt(env))


    def sleep(self, env):
        """
        This method defines when the Blob goes to sleep, that is during Nighttime.
        It waits for the Nighttime to come, and then set the Blob to sleep.
        If the Blob is hunting while Nighttime starts, the hunting process is interrupted and the Blob
        goes to sleep.

        """
        while self.alive: # Execute only if the Blob is still alive
            yield env.timeout(DAYLIGHT) # Wait for the night to pass
            if self.isHunting: # If the Blob is hunting, interrupt it and set to NOT hunting.
                self.hunt_proc.interrupt()
                self.isHunting = False
                if self.food_eaten < self.food_requirements: # If the Blob hasn't eaten enough, it dies.
                    self.alive = False
                # print(f'{self.name} is now sleeping: {env.now}, and is alive: {self.alive}')
                self.food_eaten = 0 # Reset to zero the food eaten for the next day


    def hunt(self, env):
        """
        This method defines when the Blob goes searching fo food.

        """
        while self.alive: # Execute only if the Blob is still alive
            try:
                self.isHunting = True # Blob goes searching for food
                print(f'{self.name} starts hunting at time {env.now}')
                yield env.timeout(time_to_food()) # Some time is spent searching some fodd
                if forest.food.level > 0:
                    yield forest.food.get(1) # A food item is gathered from the Forest
                    self.food_eaten += 1 # The Blob has eaten a food
                    # print(f'{self.name} has finsihed eating at time {env.now}, and has energy {self.food_eaten}')
                    yield env.timeout(TIME_AFTER_EAT) # The blob takes a nap before searching for food again
                else:
                    # print('Forest is depleted')
                    pass
            except simpy.Interrupt: # Nighttime has come
                self.isHunting = False
                yield env.timeout(NIGHTTIME) # Wait for the night to pass


def count_alive_blobs(Blob_list):
    num_alive = 0
    for Blob in Blob_list:
        if Blob.alive:
            num_alive +=1
    return num_alive

def check_alive(env, Blob_list):
    while True:
        yield env.timeout(DAYLIGHT)
        print(f'Living Blobs: {count_alive_blobs(Blob_list)}')
        yield env.timeout(NIGHTTIME)

# Declaration of the Simpy Environment, Forest and Blobs
env = simpy.Environment()
forest = Forest(env)
Blob_list = [Blob(env, forest, f'Blob {i}') for i in range (NUM_BLOB)]
# Start the simulation
env.run(until=NUM_DAYS*1440)

# Results
print("\n")
print("SIMULATION RESULTS")
num_alive = 0
for Blob in Blob_list:
    if Blob.alive:
        num_alive +=1
print(
    f"{'Initial Blob:':<15}{NUM_BLOB:>10}",
    f"\n{'Blob survived:':<15}{num_alive:>10}",
    f"\n{'Initial food:':<15}{INITIAL_FOOD:>10}",
    f"\n{'Food growth:':<15}{FODD_RATE_PRODUCTION:>10}",
    f"\n{'Number of days:':<15}{NUM_DAYS:>10}",
    "\n"
)