from typing import List

class Room:
    pass

class House:
    def __init__(self):
        self.__rooms: List[Room] = []  # Strong composition

    def add_room(self, room: Room):
        self.__rooms.append(room)