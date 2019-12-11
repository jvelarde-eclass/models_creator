import sys
import inflection
import mysql.connector
from mysql.connector import Error

def dataTypes(valor):
  _valor = valor.split("(")
  otros = ["datetime","date", "text", "longtext"]
  if(_valor[0] not in otros):
    switcher = {
      'int': 'INTEGER('+_valor[1],
      'varchar': 'STRING('+_valor[1],
      'tinyint': 'INTEGER('+_valor[1],
      'text': 'TEXT',
      'smallint': 'INTEGER(1)'
    }
    return switcher.get(_valor[0],"nada")
  elif(_valor[0] == "datetime"):
    return 'DATE'
  elif(valor == 'date'):
    return 'DATEONLY'
  elif(valor == 'text'):
    return 'TEXT'
  else:
    print(_valor[0])
    return 'STRING'


def dataTypesTS(valor):
  _valor = valor.split("(")
  otros = ["datetime", "date", "text"]
  if(_valor[0] not in otros):
    switcher = {
        'int': 'number',
        'varchar': 'string',
        'tinyint': 'number',
        'smallint': 'number'
    }
    return switcher.get(_valor[0], "nada")
  elif(_valor[0] == 'datetime' or _valor[0] == 'date'):
    return 'Date'
  else:
    return 'string'


def defaultValue(valor):
  otros = ["datetime", "date", "text"]
  if(valor not in otros):
    switcher = {
        'int': '0',
        'varchar': "''",
        'tinyint': '0',
        'smallint': '0'
    }
    return switcher.get(valor, "''")
  elif(valor == 'datetime'):
    return 'DataTypes.NOW'
  elif(valor == 'date'):
    return 'sequelize.literal('"0000-00-00"')'
  else:
    return "''"

def renameId(valor):
  arreglo = valor.split("_")
  primero = True
  salida = ''
  final = ''
  cuenta = 1
  for x in arreglo: 
    x = inflection.singularize(x)
    print(x)
    if(x == "id_user"):
      print("si po")
      return 'modifiedUserId'
    if(x == "id"):
      final = x
    else:
      if(primero):
        primero = False
        salida = salida + x
      else:
        salida = salida + x.capitalize()
      
      if(cuenta == len(arreglo)):
        salida = salida + final.capitalize()
    cuenta += 1
  return(salida)

def makeJs(results):
  file = open(sys.argv[2]+".js", "w")
  file.write("'use strict'\r\r")
  file.write("const sequelizeSoftDelete = require('sequelize-soft-delete')\r")
  file.write("const sequelizePaginate = require('sequelize-paginate')\r\r")
  file.write("module.exports = (sequelize, DataTypes) => {\r")
  file.write("  const "+sys.argv[2]+" = sequelize.define(\r")
  file.write("    '"+sys.argv[2]+"',\r    {\r")
  total = len(results)
  cuenta = 1
  for llave, valor, tipo in results:
    if(llave == 'id'):
      file.write("      "+llave+": {\r")
      file.write(
          "        type: DataTypes.Integer(10),\r        allowNull: false,\r        primaryKey: true,\r        autoIncrement: true\r      },\r")
    else:
      file.write("      "+renameId(llave)+":{\r")
      file.write("        field: '"+llave+"',\r")
      file.write("        type:DataTypes."+dataTypes(valor)+",\r")
      file.write("        allowNull: false,\r")
      file.write("        defaultValue: "+defaultValue(tipo)+",\r")
      if(cuenta != total):
        file.write("      },\r")
      else:
        file.write("      }\r")
    cuenta += 1
  file.write("    },\r    {\r")
  file.write("      tableName: '"+sys.argv[1]+"',\r")
  file.write("      timestamps: false,\r      defaultScope: {\r")
  file.write("        where: {\r          deleted: 0\r        }\r      }\r    }\r  )\r\r")
  file.write("  "+sys.argv[2]+".addHook('beforeUpdate', doc => {\r")
  file.write("    doc.modified = new Date()\r")
  file.write("  })\r")
  file.write("  sequelizeSoftDelete.softDelete("+sys.argv[2]+", {\r")
  file.write("    field: 'deleted',\r")
  file.write("    deleted: 1\r")
  file.write("  })\r")
  file.write("  sequelizePaginate.paginate("+sys.argv[2]+")\r\r")
  file.write("  return "+sys.argv[2]+"\r")
  file.write("}")
  file.close()

def makeTs(results):
  file = open(sys.argv[2]+".ts", "w")
  file.write("import * as Sequelize from 'sequelize'\r")
  file.write(
      "import {\r  SequelizeInstanceExtras,\r  SequelizeModelExtras,\r  SoftDelete\r} from './Extras'")
  file.write("\r\rexport interface " +sys.argv[2]+"Attributes\r  extends SequelizeInstanceExtras {\r")
  for llave, valor, tipo in results:
    if(llave == "id"):
      file.write("      "+llave+"?: "+dataTypesTS(tipo)+"\r")
    else:
      file.write("      "+renameId(llave)+"?: "+dataTypesTS(tipo)+"\r")
  file.write("}\r\rexport interface " +
             sys.argv[2]+"Instance\r  extends Sequelize.Instance<"+sys.argv[2]+"Attributes>,\r    "+sys.argv[2]+"Attributes,\r    SequelizeInstanceExtras {}")
  file.write("\r\rexport type "+sys.argv[2]+" = Sequelize.Model<\r  "+sys.argv[2]+"Instance,\r  "+sys.argv[2]+"Attributes")
  file.write("\r> &\r  SequelizeModelExtras &\r  SoftDelete<"+sys.argv[2]+"Instance, "+sys.argv[2]+"Attributes>")
  file.close()

def conectar():
  mydb = mysql.connector.connect(
    host="192.168.10.13",
    database="eclass_33",
    user="jvelarde",
    password="ApzCKTZwtXttw6Lx"
  )
  return mydb
        
try:
  db = conectar()
  cursor = db.cursor()
  cursor.execute("SELECT DISTINCT (COLUMN_NAME), COLUMN_TYPE, DATA_TYPE FROM information_schema.COLUMNS WHERE TABLE_NAME = '"+sys.argv[1]+"'")
  results = cursor.fetchall()
  makeJs(results)
  makeTs(results)
except Error as e:
    print("a",e)
finally:
  if (db.is_connected()):
    cursor.close()
    db.close()
    print("cerrado")



