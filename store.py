from pickle import dump, load

file_name = 'store'

def _ensure_file():
    try:
        with open(file_name, 'rb') as dbfile:
            pass
    except FileNotFoundError:
        with open(file_name, 'wb') as dbfile:
            dump({}, dbfile)
        print(f"Created new store file: {file_name}")

class Store:
    def __init__(self):
        _ensure_file()

        with open(file_name, 'rb') as dbfile:
            self.data = load(dbfile)

        print("Store loaded with data:", self.data)

    def save(self):
        with open(file_name, 'wb') as dbfile:
            dump(self.data, dbfile)                    

        print("Store saved with data:", self.data)

    def exists(self, id: str) -> bool:
        return id in self.data
    
    def add(self, id: str, match: int | None):        
        self.data[id] = match
        
        print(f"Added ID {id} with match {match} to store.")