from fastapi import FastAPI,Path,HTTPException,Query # type: ignore
from fastapi.responses import JSONResponse #type: ignore
import json
from pydantic import BaseModel,Field,computed_field# type: ignore
from typing import Annotated,Literal,Optional

def load_data():
    with open('patients.json','r') as f:
        data=json.load(f)

    return data 

def save_model(data):
    with open('patients.json','w') as f:
        json.dump(data,f)


app = FastAPI()

class Patient(BaseModel):

    id: Annotated[str,Field(...,description='Id of the patient',examples=['P001'])]
    name:Annotated[str,Field(...,description='Name of the patient')]
    city:Annotated[str,Field(...,description='City where the patient is living')]
    age:Annotated[int,Field(...,gt=0,lt=120,description='Age of the patient',example='39')]
    gender:Annotated[Literal['male','female'],Field(...,description='Gender of the patient')]
    height:Annotated[float,Field(...,gt=0,description='Height of the patient in meters')]
    weight:Annotated[float,Field(...,gt=0,description='Weight of the patient in kilograms')]


class PatientUpdate(BaseModel):
    name:Annotated[Optional[str],Field(...,description='Name of the patient')]
    city:Annotated[Optional[str],Field(...,description='City where the patient is living')]
    age:Annotated[Optional[int],Field(...,gt=0,lt=120,description='Age of the patient',example='39')]
    gender:Annotated[Optional[Literal['male','female']],Field(...,description='Gender of the patient')]
    height:Annotated[Optional[float],Field(...,gt=0,description='Height of the patient in meters')]
    weight:Annotated[Optional[float],Field(...,gt=0,description='Weight of the patient in kilograms')]


    @computed_field
    @property
    def bmi(self) ->float:
        bmi= self.weight/(self.height**2)

        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi<18.5:
            return 'underweight'
        elif self.bmi<25:
            return 'normal'
        else:
            return 'obesse'


@app.get("/")
def hello():
    return {"message":"Paitent data management system"}

@app.get("/about")
def greet():
    return {"message":"This is a api for paitent data management"}

@app.get('/view')
def view():
    data=load_data()

    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(...,description="ID of the patient",example="P001")):
    data=load_data()

    if patient_id in data:
        return data[patient_id]
    
    raise HTTPException(status_code=404,detail='paitent id is not valid')
    

@app.get('/sort')
def sort_values(sort_by: str = Query(...,description='sort the paitent data by the given field'),order: str = Query('asc',description='sort in asc or desc order')):

    data=load_data()

    fields=['height','weight','bmi']

    if sort_by not in fields:
        raise HTTPException(status_code=400,detail=f'you need to select{fields}')

    if order not in ["asc","desc"]:
        raise HTTPException(status_code=400,detail='you need to select asc or desc')
    
    sort_check= True if order=='desc' else False
    
    sorted_data= sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sort_check)

    return sorted_data

@app.post('/create')
def create_patient(patient: Patient):

    data=load_data()

    if patient.id in data:
        raise HTTPException(status_code=400,detail="already exists")
    

    data[patient.id]=patient.model_dump(exclude=['id'])

    save_model(data)

    return JSONResponse(status_code=201,content={'message':"new record created successfully"})


@app.put('/edit/{patient_id}')
def update_patient(patient_id: str , patient_update:PatientUpdate):

    data=load_data()

    if patient_id not in data:
        raise HTTPException(status_code=400,detail='not found')
    
    existing_data=data[patient_id]
    updated_info=patient_update.model_dump(exclude_unset=True)

    for key,value in updated_info.items():
        existing_data[key]=value

    existing_data['id']=patient_id
    updated_pydantic_model=Patient(**existing_data)
    existing_data=updated_pydantic_model.model_dump(exclude='id')

    data[patient_id]=existing_data

    save_model(data)

    return JSONResponse(status_code=200,content={'message':'updated successfully'})


@app.delete('/delete/{patient_id}')
def delete(patient_id:str):
    data=load_data()
    if patient_id not in data:
        raise HTTPException(status_code=400,detail='not found')
    
    del data[patient_id]
    save_model(data)

    return JSONResponse(status_code=200,content='deleted successfully')