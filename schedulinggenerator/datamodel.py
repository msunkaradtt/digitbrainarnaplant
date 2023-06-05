from dataclasses import dataclass

@dataclass
class Task:
    UID: str = ""
    secondsPerProduct: int = 0
    toolCode: str = ""
    toolSize: str = ""
    dueDate: str = ""
    qtyTotal: int = 0
    c_dueDate: str = ""

@dataclass
class Machine:
    id: int = 0
    secondsPerProduct: int = 0
    name: str = ""
    machines_name: str = ""

@dataclass
class Tool:
    toolSize: str = ""
    toolCode: str = ""
    total: int = 0
    available: int = 0
