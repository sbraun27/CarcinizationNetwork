# Carcinization Network
**Activate the virtual environment** 

```
source venv/Scripts/activate
```

** Install all packages **

```
pip install -r requirements.txt
```

**Run the tests**

Make sure to activate the venv.

```
python -m pytests backend/tests
```

**Run the application and API**
Make sure to activate the virtual environment.

```
python -m backend.app
```

**Run a peer instance**
Make sure to activate the virtual environment.

```
export PEER=True ** python -m backend.app
```

**Run the frontend**
In the fronternd directory, run ```npm run start``` in the frontend directory.

**Seed the backend with data**
Ensure the virtual environment is activated.
```python -m backend.app```