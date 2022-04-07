import util

def controller_signup(cnn, userObj):
  result = {}
  try:
    # validations
    if util.userExist(cnn, userObj.email): 
      result['processOk'] = False
      result['msgErro'] = 'Já existe um usuário cadastrado com esse email'
      return result
    
    if not util.checkEmail(userObj.email):
      result['processOk'] = False
      result['msgErro'] = 'Email inválido'
      return 'Email inválido'

    if (len(userObj.nome) or len(userObj.sobrenome)) > 25:
      result['processOk'] = False
      result['msgErro'] = 'Tamanho "Nome" ou "Sobrenome" fora dos padrões estabelecidos'
      return result
    
    if len(userObj.genero) > 1:
      result['processOk'] = False
      result['msgErro'] = 'Genero fora do padrão estabelecido'
      return result

    cursor = cnn.cursor()
    #evitar query assim para nao sql injection
    cursor.execute(f"""INSERT INTO users
      (name, email, last_name, password, birth_date, genre, approved, role)
      values ('{userObj.nome}', '{userObj.email}', '{userObj.sobrenome}', '{userObj.senha}','{userObj.data_nascimento}', '{userObj.genero}', 0, 'common')
      """)
    cnn.commit()
    cursor.close()

    result['processOk'] = True
    result['msgErro'] = None
  except Exception as e:
    result['processOk'] = False
    result['msgErro'] = str(e)

  return result

def verifyUser(cnn, bearer, role):
  if(bearer == None):
    raise Exception('Você não tem permissão para essa solicitação')
  token = bearer.replace('Bearer ', '')
  cursor = cnn.cursor()
  cursor.execute(f"SELECT * FROM users WHERE token = '{token}'")
  find = cursor.fetchall()
  if len(find) == 0:
    raise Exception('Você não tem permissão para essa solicitação')
  user = find[0]
  if not user[7] in role:
    raise Exception('Você não tem permissão para essa solicitação')
  return user[0]
  
  

