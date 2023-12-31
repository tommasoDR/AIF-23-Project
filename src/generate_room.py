import gym
import minihack
import numpy as np
import sys
from .utils import *
from .data import *


def read_des_file(des_file: str) -> str:
    """
    Reads the des file and returns the map.

    :param des_file: the path of the des file
    :return: the map as a string
    """
    try:
        with open(des_file, 'r') as file:
            content = file.read()

        start_index = content.find('MAP')
        end_index = content.find('ENDMAP')

        if start_index != -1 and end_index != -1 and start_index < end_index:
            map_content = content[start_index + len('MAP'):end_index]
        else:
            raise Exception("MAP and ENDMAP not found in des file")
    except Exception as e:
        print("Error reading des file")
        print(str(e), file=sys.stderr)
        sys.exit(1)
    return map_content


def random_room_type() -> int:
    """
    Returns a random room type.

    :return: a random room type as an integer
    """
    return np.random.randint(0, num_rooms)


def random_pattern_file(pattern=-1) -> str:
    """
    Returns a random pattern file path

    :return: a random pattern file path as a string
    """
    if pattern == -1:
        pattern = np.random.randint(1, num_patterns + 1)
    return room_pattern_path.format(pattern)


def build_goals_info(goal_objects, room_type):
    """
    Builds the goals info.

    :param room_type: an integer representing the room type
    :param goal_objects: the list of goal objects
    :return: the goals info
    """
    goals_info = []
    for i in range(len(goal_objects)):
        (object_name, object_symbol, color) = goal_objects[i]
        goals_info.append((object_name, object_symbol, color, "uncursed" if i == room_type else "cursed"))
    return goals_info
    

def add_goal_objects(levelgen, goal_objects, room_type):
    """
    Adds the goal objects to the level generator.

    :param levelgen: the MiniHack level generator
    :param goal_objects: the list of goal objects
    :param room_type: the type of the room
    """
   
    if len(goal_objects) != num_rooms:
        print("Number of goal objects must be equal to number of rooms")
        sys.exit(1)
    
    goals_info = build_goals_info(goal_objects, room_type)
    # print(goals_info)
    for (object_name, object_symbol, _, curse_state) in goals_info:
        if curse_state == "uncursed":
            (object_name_g, object_symbol_g, _, curse_state_g) = (object_name, object_symbol, _, curse_state)
            continue
        levelgen.add_object(name=object_name, symbol=object_symbol, place=None, cursestate=curse_state)
    # Avoid bug of overwrite objects
    levelgen.add_object(name=object_name_g, symbol=object_symbol_g, place=None, cursestate=curse_state_g)
    return goals_info


def add_random_objects(levelgen, object_info, room_type):
    """
    Adds random objects to the level generator.

    :param levelgen: the MiniHack level generator
    :param object_info: the list of objects
    :param room_type: the type of the room
    """
    for _ in range(num_generations_spins):
        np.random.shuffle(object_info)
        for i in range(len(object_info)):
            (object_name, object_symbol, _, _, spawn_probability) = object_info[i]
            p = np.random.uniform()
            if p <= spawn_probability[room_type]:
                levelgen.add_object(name=object_name, symbol=object_symbol, place=None, cursestate=None)


def generate_env(pattern=-1):
    """
    Generates a random MiniHack environment, with goal objects and random objects.
    Objects are defined and taken from the object file.
    The room type is randomly chosen.
    The room pattern is randomly chosen.

    :return: the MiniHack environment (type: gym.Env)
    """
    room_pattern_file = random_pattern_file(pattern)
    levelgen = minihack.LevelGenerator(map=read_des_file(room_pattern_file), lit=True, flags=("premapped",))
    room_type = random_room_type()
    # room_type = 2
    clue_objects, goal_objects = read_object_file(object_file_path)
    add_random_objects(levelgen, clue_objects, room_type)
    goals_info = add_goal_objects(levelgen, goal_objects, room_type)
    # print(levelgen.get_des())
    env = gym.make("MiniHack-Skill-Custom-v0",
                   observation_keys=("screen_descriptions_crop", "chars", "colors", "pixel"), obs_crop_h=3,
                   obs_crop_w=3, max_episode_steps=10000, autopickup=False, des_file=levelgen.get_des())

    return env, goals_info


# To run: python3 -m src.generate_room
if __name__ == "__main__":
    np.set_printoptions(threshold=sys.maxsize)
    env, goals_info = generate_env()
    print_level(env.reset())