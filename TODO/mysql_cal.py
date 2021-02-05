from TODO import MySqlCustom


if __name__ == '__main__':

    # 登陆信息
    host = '10.16.56.6'
    dbname = 'jiangsu_water'
    user = 'root'
    pwd = '123456'
    port = 3306
    login = {'host': host, 'dbname': dbname, 'user': user, 'pwd': pwd, 'port': port}

    sql_formula = 'SELECT * FROM t_admin WHERE 1=1;'
    sql_data = {}
    sql_str = MySqlCustom.SQLStringInterface(sql_formula, sql_data)
    sql_res = MySqlCustom.executeSql(login, sql_str)

    print('Finish')
