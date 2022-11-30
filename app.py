import os
from fastapi import FastAPI, Body, HTTPException, status 
from fastapi.responses import Response, JSONResponse 
from fastapi.encoders import jsonable_encoder 
from pydantic import BaseModel, Field, EmailStr 
from bson import ObjectId 
from typing import Optional, List 
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#MONGODB_URL ='mongodb+srv://diegoreyesmosquera:<contraseña>@cluster0.zvacvnc.mongodb.net/test'

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.ventaviajes


class PyObjectId(ObjectId):
    @classmethod 
    def __get_validators__(cls):
        yield cls.validate 
          
    @classmethod 
    def validate(cls, v): 
        if not ObjectId.is_valid(v): 
            raise ValueError("Invalid objectid") 
        return ObjectId(v)

    @classmethod 
    def __modify_schema__(cls, field_schema): 
        field_schema.update(type="string")

class viajeModel(BaseModel):
   id: PyObjectId = Field(default_factory=PyObjectId, alias="_id") 
   destino: str = Field("...")
   ida: str = Field("...") 
   regreso: str = Field("...") 
   
   class Config: 
       allow_population_by_field_name = True 
       arbitrary_types_allowed = True 
       json_encoders = {ObjectId: str} 
       schema_extra = { 
           "example": { 
                "destino": "Jane Doe",
                "ida": "jdoe@example.com",
                "regreso": "Desarrollo de aplicaciones Web"
           } 
        } 

class UpdateviajeModel(BaseModel): 
   destino: Optional[str]
   ida: Optional[str] 
   regreso: Optional[str] 
   
   class Config: 
       arbitrary_types_allowed = True 
       json_encoders = {ObjectId: str} 
       schema_extra = {
           "example": { 
                "destino": "Jane Doe", 
                "ida": "jdoe@example.com", 
                "regreso": "Desarrollo de aplicaciones Web"
           }  
        }       

@app.post("/", response_description="Add new viaje",response_model=viajeModel) 
async def create_viaje(viaje: viajeModel = Body(...)): 
   viaje = jsonable_encoder(viaje) 
   new_viaje = await db["sitios"].insert_one(viaje) 
   created_viaje = await db["sitios"].find_one({"_id": new_viaje.inserted_id}) 
   return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_viaje)

@app.get("/", response_description="List all viajes",response_model=List[viajeModel] )
async def list_viajes(): 
   viajes = await db["sitios"].find().to_list(1000) 
   return viajes

@app.get("/{id}", response_description="Get a single viaje",response_model=viajeModel ) 
async def show_viaje(id: str): 
    if (viaje := await db["sitios"].find_one({"_id": id})) is not None: 
        return viaje

    raise HTTPException(status_code=404, detail=f"viaje {id} not found")

@app.put("/{id}", response_description="Update a viaje", response_model=viajeModel) 
async def update_viaje(id: str, viaje: UpdateviajeModel = Body(...)): 
    viaje = {k: v for k, v in viaje.dict().items() if v is not None}

    if len(viaje) >= 1: 
     update_result = await db["sitios"].update_one({"_id": id}, {"$set": viaje})
     
     if update_result.modified_count == 1: 
            if (
                updated_viaje := await db["sitios"].find_one({"_id": id})
            ) is not None:
                return updated_viaje
        
    if (existing_viaje := await db["sitios"].find_one({"_id": id})) is not None:
         return existing_viaje
    
    raise HTTPException(status_code=404, detail=f"viaje {id} not found")

@app.delete("/{id}", response_description="Delete a viaje") 
async def delete_viaje(id: str): 
    delete_result = await db["sitios"].delete_one({"_id": id}) 
    
    if delete_result.deleted_count == 1: 
        return Response(status_code=status.HTTP_204_NO_CONTENT) 
    raise HTTPException(status_code=404, detail=f"viaje {id} not found")    





