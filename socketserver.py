import socket
import mysql.connector

# create an INET, STREAMing socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port
sock.bind(('', 8700))
# become a server socket
sock.listen(5)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #can reuse the port

while True:
    (conn, address) = sock.accept()
    print('Connected by:',address)
    data = conn.recv(1024)
    info = data.decode('utf-8')
    print(info)
    info = info.split(",")
    check = info[0][1:]

    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      passwd="a321478965",
      database="iot_competition"
    )
    mycursor = mydb.cursor()

    if(check=='sensor'):  #insert sensor info
      sql_cmd = "INSERT INTO `sensor`(`temp`, `moisture`, `time`) VALUES ('"+info[1]+"','"+info[2]+"','"+info[3][:-1]+"')"
      mycursor.execute(sql_cmd)
      mydb.commit()
      print('upload sensor value:'+info[1]+','+info[2]+','+info[3][:-1])

    elif(check=='medicine_open'):  #update medicine in DB when fill medicine test:(medicine_open,普拿疼,100)
      sql_cmd = "SELECT amount FROM medicine where name ='"+info[1]+"'"
      mycursor.execute(sql_cmd)
      myresult = mycursor.fetchall()
      myresult = str(myresult[0]).split(',')

      num_indb = int(myresult[0][1:])
      num = num_indb + int(info[2][:-1])

      sql_cmd = "UPDATE medicine SET amount ="+str(num)+" WHERE name ='"+info[1]+"'"
      mycursor.execute(sql_cmd)
      mydb.commit()
      print('add '+str(info[2][:-1])+' to '+info[1])

    elif(check=='medicine_distribute'): #INSERT INTO `patient`(`visit_time`, `number`, `name`, `reason`, `medicine`, `quantity`) VALUES (CURRENT_TIMESTAMP(),'00006','Dennis','帥','四物丸',5) test:(medicine_distribute,00005)
      sql_cmd = "SELECT medicine,quantity FROM patient WHERE number ='"+info[1][:-1]+"' ORDER BY visit_time DESC"
      mycursor.execute(sql_cmd)
      myresult = mycursor.fetchone()
      print(myresult)

      #send medicine and quantity
      send_medicine = str(myresult[0]).replace(',','-')
      send_quantity = str(myresult[1]).replace(',','-')
      send_text = '(medicine_distribute,'+send_medicine+','+send_quantity+')'
      conn.send(send_text.encode('utf-8'))
      print('send:'+send_text)

      medicine = myresult[0].split(',')
      quantity = myresult[1].split(',')

      for i in range(len(medicine)):
        mydb = mysql.connector.connect(
          host="localhost",
          user="root",
          passwd="a321478965",
          database="iot_competition"
        )
        mycursor = mydb.cursor()
        print(medicine[i])
        sql_cmd = "SELECT amount FROM medicine where name ='"+medicine[i]+"'"
        mycursor.execute(sql_cmd)
        myresult = mycursor.fetchone()
        num_indb = int(myresult[0])
        num = num_indb - int(quantity[i])

        sql_cmd = "UPDATE medicine SET amount ="+str(num)+" WHERE name ='"+medicine[i]+"'"
        print('add '+str(quantity[i])+' to '+medicine[i])
        mycursor.execute(sql_cmd)
        mydb.commit()
        



