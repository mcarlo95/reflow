import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('sqlite://', echo=False)

df = pd.DataFrame({'name' : ['User 1', 'User 2', 'User 3']})
df

df.to_sql(name='users', con=engine, if_exists='append')

from sqlalchemy import text
with engine.connect() as conn:
   conn.execute(text("SELECT * FROM users")).fetchall()

