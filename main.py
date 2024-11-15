from fastapi import FastAPI, APIRouter


app = FastAPI()

ai_router = APIRouter(
    prefix='/ai',
    tags = ['AI'],
    responses={404: {"description": "Not found"}},
)


@ai_router.get('/healthcheck')
def healthcheck():
    return {'status': 'ok'}

app.include_router(ai_router)

if __name__ == '__main__':
    import uvicorn
    
    uvicorn.run(app, host='0.0.0.0', port=8000)
