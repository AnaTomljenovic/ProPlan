from enum import Enum

class Availability(str, Enum):
    FREE = "Free"
    BUSY = "Busy"

class Role(str, Enum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    WORKER = "Worker"

class ProjectStatus(str, Enum):
    STARTED = "Started"
    ONGOING = "Ongoing"
    FINISHED = "Finished"

class TaskStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    DONE = "Done"

class DayOffType(str, Enum):
    HOLIDAY = "Holiday"
    SICK_LEAVE = "Sick Leave"
    DAY_OFF = "Day Off"
