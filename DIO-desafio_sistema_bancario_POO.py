from abc import ABC, abstractmethod
from datetime import datetime
import textwrap

class Transacao(ABC):

    @property
    @abstractmethod
    def valor(self):
        pass

    @classmethod
    @abstractmethod
    def registrar(self, conta):
        pass

class Deposito(Transacao):
    
    def __init__(self, valor = None):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        if(conta.depositar(self.valor)):
            conta.historico.adicionar_transacao(self)

class Saque(Transacao):
    def __init__(self, valor = None):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        
        if(conta.sacar(self.valor)):
            conta.historico.adicionar_transacao(self)
        
class Historico():

    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            }
        )

class Conta():
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()


    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico


    @classmethod
    def nova_conta(cls, numero, cliente):
        return cls(numero, cliente)

    def sacar(self, valor):

        saldo = self._saldo

        if valor <= 0:
            print("Valor do saque deve ser positivo.")

        elif valor > saldo:
            print("Saldo insuficiente.")

        else:
            self._saldo -= valor
            
            #extrato += f'Saque     -------------    R$ {valor:.2f}\n'
            print(f'Saque realizado no valor de R$ {valor:.2f}')
            return True
        
        return False

    def depositar(self, valor):

        if(valor <= 0):
            print("Valor do deposito deve ser positivo.")
            return False
        
        else:
            self._saldo += valor
            print(f"Depositado valor de R$ {valor:.2f} na conta.")
            return True
        
class Conta_Corrente(Conta):
    def __init__(self, numero, cliente, valor_limite_saque = 500, limite_saques_diarios = 3):
        super().__init__(numero, cliente)
        self.valor_limite_saque = valor_limite_saque
        self.limite_saques_diarios = limite_saques_diarios

    def sacar(self, valor):

        numero_saques = len([transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__])

        saldo = self._saldo

        if valor > self.valor_limite_saque:
            print("Valor solicitado esta acima do valor limite por saque.")

        elif numero_saques >= self.limite_saques_diarios:
          print("Limite de saques diarios atingido")

        else:
            return super().sacar(valor)
        
        return False
    
    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}"""

class Cliente():

    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class Pessoa_fisica(Cliente):
    
    def __init__(self, endereco, cpf, nome, data_nascimento):
        super().__init__(endereco)
        self._cpf = cpf
        self._nome = nome
        self._data_nascimento = data_nascimento

    @property
    def cpf(self):
        return self._cpf
    
    @property
    def nome(self):
        return self._nome
    
    @property
    def data_nascimento(self):
        return self._data_nascimento

def menu():
    return input("""
Escolha a sua operacao desejada:

[d] = depositar
[s] = sacar
[e] = extrato
[u] = criar novo usuario
[c] = criar nova conta corrente
[l] = listar contas existentes
[q] = sair
""")

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n Cliente nao possui conta")
        return
    
    return cliente.contas[0]

def depositar(clientes):
    cpf = input("informe o cpf do cliente:")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Cliente nao encontrado na base de dados")
        return

    valor = float(input("Digite o valor a ser depositado:"))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):

    cpf = input("informe o cpf do cliente:")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Cliente nao encontrado na base de dados")
        return

    valor = float(input("Digite o valor a ser sacado:"))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)
    
def exibir_extrato(clientes):
    cpf = input("informe o cpf do cliente:")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Cliente nao encontrado na base de dados")
        return
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n______________EXTRATO______________")
    print("___________________________________")
        
    transacoes = conta.historico.transacoes
    extrato = ""
    if not transacoes:
        print("Nao foram realizadas movimentacoes")
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:   \t-------------\tR${transacao['valor']:.2f}"

    print(extrato)
    print(f'Saldo:\t-------------\t\tR$ {conta.saldo:.2f}')
    print("___________________________________\n")
    
def criar_cliente(clientes):
    cpf = input("informe o cpf do cliente:")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("Cliente já possui cadastro")
        return
    
    nome = input("Digite o nome completo:")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa):")
    endereco = input("Informe o endereço(logradouro - nro - bairro - cidade/sigla do estado)")

    cliente = Pessoa_fisica(endereco = endereco, nome = nome, cpf = cpf, data_nascimento = data_nascimento)

    clientes.append(cliente)

    print("\n Cadastro do cliente realizado com sucesso!")

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

def criar_conta(numero_conta, clientes, contas):
    cpf = input("informe o cpf do cliente:")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Cliente nao encontrado na base de dados")
        return
    
    conta = Conta_Corrente(numero = numero_conta, cliente = cliente)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n Conta criada co sucesso!")

def main():

    clientes = []
    contas = []


    while(True):
        
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":        
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)
 
        elif opcao == "u":
            criar_cliente(clientes)

        elif opcao == "c":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "l":
            listar_contas(contas)

        elif opcao == "q":
            print("Opcao sair selecionada.")
            break        

        else:
            print("Opcao selecionada e invalida. Por favor, selecione novamente a operacao desejada.")

main()