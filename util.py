import re   
  
def userExist(conn, email):   
  q = f"""
    SELECT id from users where email = '{email}'
  """
  cursor = conn.cursor()
  cursor.execute(q) 

  if not len(cursor.fetchall()) is 0:
    cursor.close()
    return True

  cursor.close()
  return False

def checkEmail(email):   
  regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$' 
  if(re.search(regex,email)):   
      return True   
  
  return False

