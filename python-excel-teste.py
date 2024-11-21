import mysql.connector
import pandas as pd


def criarconexao():
    try:
        conexao = mysql.connector.connect(host='localhost', database='univap', user='root')
        if conexao.is_connected():
            return conexao
        else:
            return None
    except Exception as erro:
        print(f"Erro na conexão: {erro}")
        return None


def def_planilha1(conexao, codigo_professor):
    # Consulta para a Planilha 1
    query_planilha1 = f"""
    SELECT dxp.codigodisciplinanocurso, dxp.coddisciplina, dxp.codprofessor, dxp.curso, dxp.cargahoraria, dxp.anoletivo
    FROM disciplinasxprofessores dxp
    WHERE dxp.codprofessor = {codigo_professor} AND dxp.anoletivo = 2021
    """

    try:
        cursor = conexao.cursor()
        cursor.execute(query_planilha1)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        cursor.close()

        df_planilha1 = pd.DataFrame(data, columns=columns)

        # Calcular o total de horas aulas que o professor dará
        total_horas_aulas = df_planilha1['cargahoraria'].sum()

        # Adicionar uma linha com o total de horas aulas ao final do DataFrame
        total_row = {'codigodisciplinanocurso': 'Total Horas Aulas', 'coddisciplina': '', 'codprofessor': '',
                     'curso': '', 'cargahoraria': total_horas_aulas, 'anoletivo': ''}
        df_planilha1 = pd.concat([df_planilha1, pd.DataFrame([total_row])], ignore_index=True)

        return df_planilha1
    except Exception as erro:
        print(f"Erro na consulta da Planilha 1: {erro}")
        return None


def def_planilha2(conexao):
    # Consulta para a Planilha 2
    query_planilha2 = f"""
    SELECT dxp.curso, p.nomeprof
    FROM disciplinasxprofessores dxp
    JOIN professores p ON dxp.codprofessor = p.registro
    JOIN disciplinas d ON dxp.coddisciplina = d.codigodisc
    WHERE dxp.anoletivo = 2021
    """

    try:
        cursor = conexao.cursor()
        cursor.execute(query_planilha2)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        cursor.close()

        df_planilha2 = pd.DataFrame(data, columns=columns)

        # Adicionar uma linha ao final da tabela com o total de professores
        total_geral = df_planilha2['nomeprof'].nunique()
        total_row = pd.DataFrame([[None, None]], columns=['curso', 'nomeprof'])
        df_planilha2 = pd.concat([df_planilha2, total_row], ignore_index=True)
        df_planilha2.iloc[-1, 0] = 'Total de Professores'
        df_planilha2.iloc[-1, 1] = total_geral

        return df_planilha2
    except Exception as erro:
        print(f"Erro na consulta da Planilha 2: {erro}")
        return None


def def_planilha3(conexao):
    # Consulta para a Planilha 3
    query_planilha3 = f"""
    SELECT dxp.curso, d.nomedisc, dxp.cargahoraria
    FROM disciplinasxprofessores dxp
    JOIN disciplinas d ON dxp.coddisciplina = d.codigodisc
    WHERE dxp.anoletivo = 2021
    """

    try:
        cursor = conexao.cursor()
        cursor.execute(query_planilha3)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        cursor.close()

        df_planilha3 = pd.DataFrame(data, columns=columns)

        # Calcular o total de carga horária
        total_carga_horaria = df_planilha3['cargahoraria'].sum()

        # Adicionar uma linha ao final da tabela com o total de carga horária
        total_row = pd.DataFrame([[None, 'Total Carga Horária', total_carga_horaria]],
                                 columns=['curso', 'nomedisc', 'cargahoraria'])
        df_planilha3 = pd.concat([df_planilha3, total_row], ignore_index=True)

        return df_planilha3
    except Exception as erro:
        print(f"Erro na consulta da Planilha 3: {erro}")
        return None


# Solicitar ao usuário o código do professor
codigo_professor = input("Digite o código do professor: ")

# Criar a conexão
conexao = criarconexao()

if conexao:
    # Chamar as funções para obter as Planilhas
    df_planilha1 = def_planilha1(conexao, codigo_professor)
    df_planilha2 = def_planilha2(conexao)
    df_planilha3 = def_planilha3(conexao)

    # Salvar os dados em uma planilha Excel
    with pd.ExcelWriter('teste123.xlsx', engine='openpyxl') as writer:
        df_planilha1.to_excel(writer, sheet_name='Planilha1', index=False)
        df_planilha2.to_excel(writer, sheet_name='Planilha2', index=False)
        df_planilha3.to_excel(writer, sheet_name='Planilha3', index=False)

    print("Arquivo Excel gerado com sucesso!")

    # Fechar a conexão
    conexao.close()
else:
    print("Não foi possível estabelecer a conexão.")