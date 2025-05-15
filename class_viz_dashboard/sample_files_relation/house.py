from typing import List, final


@final
class Room:
    """Part-of House (composition relationship)"""

    def __init__(self, room_type: str):
        self.room_type = room_type


@final
class House:
    """Owns Room objects (composition relationship)"""

    def __init__(self, address: str):
        self.address = address
        self.__rooms: List[Room] = []  # Strong ownership

    def add_room(self, room_type: str) -> None:
        """Composition method (creates and owns Room)"""
        self.__rooms.append(Room(room_type))

    def destroy(self) -> None:
        """Demonstrates composition lifecycle"""
        print(f"House at {self.address} destroyed - all rooms gone")
        self.__rooms.clear()

    @property
    def rooms(self) -> List[Room]:
        return self.__rooms.copy()