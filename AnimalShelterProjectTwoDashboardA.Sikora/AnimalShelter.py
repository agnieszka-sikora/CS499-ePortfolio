from pymongo import MongoClient
from bson.objectid import ObjectId

class AnimalShelter(object):
    def __init__(self):
        
        #Connection variables
        USER = 'aacuser'
        PASS = 'SNHU1234'
        HOST = 'nv-desktop-services.apporto.com'
        PORT = 31515
        DB = 'AAC'
        COL = 'animals'
        
        #Initialize connection
       
        self.client = MongoClient('mongodb://%s:%s@%s:%d' % (USER,PASS,HOST,PORT))
        self.database = self.client['%s' % (DB)]
        self.collection = self.database['%s' % (COL)]

        #Create method to implement C in CRUD
    def create(self, data):
        if data is not None:
            createData = self.database.animals.insert_one(data)
            print(data)
            if createData != 0:
                print("Success")
                return True
            else:
                return False
        else:
            raise Exception("Nothing to save, because data parameter is empty")
     
        #Read method to implement R in CRUD
    def read(self, searchData):
        if searchData is not None:
            data = self.database.animals.find(searchData)
            return data
        else:
            raise Exception("Nothing to find")
        
    
        #Update method to implement U in CRUD
    def update(self, searchData, updateData):
        if searchData is not None:
            search_result = self.database.animals.update_many(searchData, {"$set": updateData})
            updated = search_result.raw_result
            print("Data updated succesfully")
            return updated
        else:
            raise Exception("Nothing to update")
            
        #Delete method to implement D in CRUD
    def delete(self, deleteData):
        if deleteData is not None:
            delete_result = self.database.animals.delete_many(deleteData)
            deleted = delete_result.raw_result
            print("Data deleted")
            return deleted
        else:
            raise Exception("Nothing to delete")
            
        
    
if __name__ == "__main__":
    USER = 'aacuser'
    PASS = 'SNHU1234'
    HOST = 'nv-desktop-services.apporto.com'
    PORT = 31515
    DB = 'AAC'
    COL = 'animals'
    
    animal = AnimalShelter(USER, PASS, HOST, PORT, DB, COL)
    

