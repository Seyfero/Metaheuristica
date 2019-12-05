import os
import sys
import time
from random import randint

#############################################################################################################
#Classe que receberá os itens, propriamente o Pacote                                                        #
#   -Capacidade Total que o pacote possui                                                                   #
#   -Capacidade Restante que o pacote possuo                                                                #
#   -Lista de restrições que o pacote possui                                                                #
#   -Propriamente os itens que estão dentro dele                                                            #
#############################################################################################################
class Box:
    def __init__(self, capacidade, listaRestricoes = None, listaItens = None):
        self.capacidadeTotal = int(capacidade)
        self.capacidadeAtual = int(capacidade)
        self.listaRestricoes = []
        self.itens = []


    def getCapacidadeTotal(self):
        return self.capacidadeTotal


    def getCapacidadeAtual(self):
        return self.capacidadeAtual


    def getListaRestricoes(self):
        return self.listaRestricoes.copy()


    def getItens(self):
        return self.itens.copy()

    #Função que pega somente os IDs dos itens
    def getItensSaida(self):
        saida = []
        for i in self.itens:
            saida.append(i.id)
        return saida

    #Função que copia o pacote com todos itens dentro dele
    def getBox(self):
        aux1 = Box(str(self.getCapacidadeTotal()))
        aux1.listaRestricoes = self.getListaRestricoes()
        aux1.capacidadeTotal = self.getCapacidadeTotal()
        aux1.capacidadeAtual = self.getCapacidadeAtual()
        aux1.itens = self.getItens()
        return aux1


#############################################################################################################
#Classe que será os itens                                                                                   #
#   -ID do item                                                                                             #
#   -Peso dele                                                                                              #
#   -Lista de itens que possui incompatibilidade com ele                                                    #
#                                                                                                           #
#############################################################################################################
class Item():
    def __init__(self, id, peso, conflitos):
        self.id = id
        self.peso = int(peso)
        self.conflitos = conflitos



#############################################################################################################
#Classe da Metaheurística                                                                                   #
#   -Lista com todos pacotes usados                                                                         #
#   -Lista de todos itens                                                                                   #                                                                                                           #
#                                                                                                           #
#############################################################################################################
class VNS:

    def __init__(self):
        self.pacotes = []
        self.listaItens = []

    #Função que copia todos os pacotes da lista de pacotes
    def copia(self, pacotes):
        auxPacotes = []
        for i in pacotes:
            aux = Box.getBox(i)
            auxPacotes.append(aux)
        return auxPacotes


    def lerArquivo(self):
        # leitura do arquivo passado como primeiro parametro
        arquivo = open(sys.argv[1], 'r')
        info = arquivo.readline()
        graph = arquivo.readlines()
        arquivo.close()
        # armazenamento das informacoes
        info = info.split()
        self.capacidadePacote = info[1]
        # preenchimento dos dados dos itens
        itens = []
        for i in graph:
            token = i.split()
            if token:
                aux = Item(token[0], token[1], token[2:])
                itens.append(aux)
        self.listaItens = itens

    #Função que verifica a compatibilidade de dado item e um pacote
    #Caso o item posso entrar no pacote respeitando restrições e capacidades retornará True
    def verificaRestricao(self, pacoteAtual, item):
        if item.id in pacoteAtual.listaRestricoes:
            return False

        for i in pacoteAtual.itens:
            if i.id in item.conflitos:
                return False

        if pacoteAtual.capacidadeAtual - item.peso < 0:
            return False

        return True

    #Função que insere item dentro de pacote e atualiza os valores do pacote atual
    def insereItemPacote(self, pacote, item):
        pacote.capacidadeAtual -= item.peso
        pacote.listaRestricoes += item.conflitos
        pacote.itens.append(item)
        return pacote

    #Solução inicial que, com os itens ordenados de forma crescente pelo peso, faza a alocação de forma gulosa
    def geraSolucao(self, listaItensAtual, pacotes):
        pacoteAtual = Box(self.capacidadePacote)
        auxListaItens = listaItensAtual.copy()
        i = 0
        while auxListaItens != []:
            if i >= len(auxListaItens) or pacoteAtual.capacidadeAtual == 0:
                i = 0
                pacoteAtual.itens = sorted(pacoteAtual.itens, key=lambda  Item: Item.peso)
                pacotes.append(pacoteAtual)
                pacoteAtual = Box(self.capacidadePacote)
            elif auxListaItens[i].peso < int(pacoteAtual.capacidadeAtual):
                if self.verificaRestricao(pacoteAtual, auxListaItens[i]):
                    pacoteAtual.capacidadeAtual -= auxListaItens[i].peso
                    pacoteAtual.itens.append(auxListaItens[i])
                    pacoteAtual.listaRestricoes += auxListaItens[i].conflitos
                    auxListaItens.pop(i)
                else:
                    i+=1
            else:
                i += 1

        pacoteAtual.itens = sorted(pacoteAtual.itens, key=lambda Item: Item.peso)
        pacotes.append(pacoteAtual)
        self.listaItens = []
        return pacotes

    #Função que atualiza dados do pacote após a remoção de algum item
    def atualizaPacote(self, pacote, item):
        pacote.capacidadeAtual += item.peso
        for i in item.conflitos:
            if i in pacote.listaRestricoes:
                pacote.listaRestricoes.remove(i)
        return pacote

    #Função que verifica a existencia de pacotes vazios e caso exista, são removidos
    def verificaPacoteVazio(self):
        cond = True
        i = 0
        while cond:
            if i==len(self.pacotes):
                cond = False
                continue
            if self.pacotes[i].itens == []:
                self.pacotes.pop(i)
                i = 0
                continue
            i+=1

    #Função que seleciona dois pacotes de forma aleatória, não totalmente cheios,  passando para a função Troca 1v1
    #Sendo o primeiro o mais pesado
    #São feitas duas troca, assim aprensentou melhores resultados que apenas com uma em geral
    def troca11(self):
        controle = 0
        pacote1 = 0
        pacote2 = 0
        while controle == 0:
            pacote1 = randint(0, len(self.pacotes)-1)
            if self.pacotes[pacote1].capacidadeAtual != 0:
                controle = 1
        controle = 0
        while controle == 0:
            pacote2 = randint(0, len(self.pacotes) - 1)
            if self.pacotes[pacote2].capacidadeAtual != 0 and pacote1 != pacote2:
                controle = 1
        if self.pacotes[pacote1].capacidadeAtual > self.pacotes[pacote2].capacidadeAtual:
            self.troca1(pacote1, pacote2)
            self.troca1(pacote1, pacote2)
        else:
            self.troca1(pacote2, pacote1)
            self.troca1(pacote2, pacote1)

    #Dados os pacotes selecionandos na função troca11, pega o item mais leve do pacote mais pesado e o item mais pesado do pacote maiis leve
    #Tenta-se fazer a troca dos itens respeitando todas restrições, caso nao seja possivel tenta-se o item j+1
    #Caso todos itens sejam testados e nenhuma troca feita, tenta-se com i-1 e todas combinações de J
    #Isso até alçguma troca occorer ou serem testadas todas possibilidades
    def troca1(self, pacote1, pacote2):
        i = len(self.pacotes[pacote1].itens) - 1
        j = 0
        while True:
            #pacote 1 mais leve
            #pacote 2 Mais pesado
            #É feita a trica em um pacote auxiliar
            maiorItem = self.pacotes[pacote1].itens[i]
            menorItem = self.pacotes[pacote2].itens[j]
            aux1 = Box.getBox(self.pacotes[pacote1])
            aux1.itens.remove(maiorItem)
            aux1 = self.atualizaPacote(aux1, maiorItem)
            aux2 = Box.getBox(self.pacotes[pacote2])
            aux2.itens.remove(menorItem)
            aux2 = self.atualizaPacote(aux2, menorItem)
            #Caso atenda todas restrições atualiza-se o vetor original com os novos dados
            if self.verificaRestricao(aux1, menorItem):
                if self.verificaRestricao(aux2, maiorItem):
                    self.pacotes[pacote1].itens.remove(maiorItem)
                    self.pacotes[pacote2].itens.remove(menorItem)
                    self.atualizaPacote(self.pacotes[pacote1], maiorItem)
                    self.atualizaPacote(self.pacotes[pacote2], menorItem)
                    self.insereItemPacote(self.pacotes[pacote1], menorItem)
                    self.insereItemPacote(self.pacotes[pacote2], maiorItem)
                    return
            j+=1
            if j > len(self.pacotes[pacote2].itens) - 1:
                j = 0
                i -=1
            if i == -1:
                return

    #função auxiliar
    def troca21A(self, pacote1, pacote2):
        self.troca2(pacote1, pacote2)


    def troca2(self, pacote1, pacote2):
        #Pacote1 menos pesado, pega uma carga
        #Pacote2 mais pesado, pega uma carga
        if len(self.pacotes[pacote1].itens) <= 2:
            return

        j = 0
        k = 1
        i = len(self.pacotes[pacote2].itens) - 1
        while True:
            item1 = self.pacotes[pacote1].itens[j]
            item2 = self.pacotes[pacote1].itens[k]
            item3 = self.pacotes[pacote2].itens[i]
            #conferir essa parte
            aux1 = Box.getBox(self.pacotes[pacote1])
            aux1.itens.remove(item1)
            aux1.itens.remove(item2)
            self.atualizaPacote(aux1, item1)
            self.atualizaPacote(aux1, item2)
            aux2 = Box.getBox(self.pacotes[pacote2])
            aux2.itens.remove(item3)
            self.atualizaPacote(aux2, item3)
            if item3.peso >= item1.peso + item2.peso:
                if aux1.capacidadeAtual  >= item3.peso:
                    if self.verificaRestricao(aux1, item3):
                        if self.verificaRestricao(aux2, item2):
                            if self.verificaRestricao(aux2, item1):
                                self.pacotes[pacote1].itens.remove(item1)
                                self.pacotes[pacote1].itens.remove(item2)
                                self.pacotes[pacote2].itens.remove(item3)
                                self.atualizaPacote(self.pacotes[pacote1], item1)
                                self.atualizaPacote(self.pacotes[pacote1], item2)
                                self.atualizaPacote(self.pacotes[pacote2], item3)
                                self.insereItemPacote(self.pacotes[pacote1], item3)
                                self.insereItemPacote(self.pacotes[pacote2], item2)
                                self.insereItemPacote(self.pacotes[pacote2], item1)
                                j = 0
                                k = 1
                                i = len(self.pacotes[pacote2].itens) - 1
                                continue
            k+=1
            if k > len(self.pacotes[pacote1].itens)-1:
                j += 1
                k = j + 1
                if k > len(self.pacotes[pacote1].itens) - 1:
                    i = -1
            if i<0:
                self.pacotes[pacote1].itens = sorted(self.pacotes[pacote1].itens, key=lambda Item: Item.peso)
                self.pacotes[pacote2].itens = sorted(self.pacotes[pacote2].itens, key=lambda Item: Item.peso)
                self.pacotes = sorted(self.pacotes, key=lambda Box: Box.capacidadeAtual)
                return

    #Função que seleciona dois pacotes para fazer a troca 2v1
    #Caso for a troca 2v1-A pega, dentre todos pacotes totalmente cheios, um para fazer a troca, caso nao tenha
        #pega um pacote entre os pacotes, exceto os 30% dos pacotes mais leves. Para J pega-se um dos ultimos
    # Caso for a troca 2v1-B pega, dentre todos pacotes totalmente cheios, caso nao tenha cheios, pega um
        # um aleatorio para fazer a troca, para o J peva-se smepre o mais vazio
    def pegaPacote21(self, valor):
        if valor == 1:
            pacotes = []
            cond = True
            i = 0
            while cond:
                if self.pacotes[i].capacidadeAtual == 0:
                    pacotes.append(i)
                    i+=1
                else:
                    cond = False
            if pacotes == []:
                #Random entre valor 0 - (Tamanho_dos_Pacotes-30%doValor) para o I
                #Caso nao exita nenhum pacote totalmente cheio
                pacotes.append(randint(0, int(round(len(self.pacotes)*0.3,0))))
                i = pacotes[i]
            else:
                i = randint(0, len(pacotes)-1)
                i = pacotes[i]
            j = randint(1, 2)
            return [i,-j]
        else:
            pacotes = []
            cond = True
            i = 0
            while cond:
                if self.pacotes[i].capacidadeAtual == 0:
                    pacotes.append(i)
                    i += 1
                else:
                    cond = False
            if pacotes == []:
                pacotes.append(randint(0, len(self.pacotes)-1))
                i = pacotes[i]
            else:
                i = randint(0, len(pacotes) - 1)
                i = pacotes[i]
            #tenta pegar um aletorio entres os ultimos, caso de erro pega-se o ultimo
            try:
                j = randint(pacotes[-1]+1, len(self.pacotes)-1)
            except:
                j = len(self.pacotes)-1
            return [i, j]

    #Na função Eliminação desaloca-se todos itens dos pacotes que não estão totalmente cheios
    #Em sequencia aloca-se de volta usando a heuristica inicial
    def eliminacao(self):
        saida = []
        for i in range(len(self.pacotes)):
            if self.pacotes[i].capacidadeAtual != 0:
                saida.append(i)

        itens = []
        for i in saida:
            aux = Box.getBox(self.pacotes[i])
            itens += self.pacotes[i].itens
            self.pacotes[i].itens = []
        self.listaItens = itens
        self.verificaPacoteVazio()
        self.geraSolucao(self.listaItens, self.pacotes)
        self.pacotes = sorted(self.pacotes, key=lambda Box: Box.capacidadeAtual)

    # Na função Pertubação desaloca-se todos itens dos pacotes que estão totalmente cheios
    # Em sequencia aloca-se de volta usando a heuristica inicial
    def pertubacao(self):
        saida = []
        for i in range(len(self.pacotes)):
            if self.pacotes[i].capacidadeAtual == 0:
                saida.append(i)

        if saida == []:
            return
        itens = []
        valor = randint(0, len(saida)-1)
        itens += self.pacotes[saida[valor]].itens
        self.pacotes[saida[valor]].itens = []
        self.listaItens = itens
        self.verificaPacoteVazio()
        self.geraSolucao(self.listaItens, self.pacotes)
        self.pacotes = sorted(self.pacotes, key=lambda Box: Box.capacidadeAtual)

    #A busca em vizinhaça consiste em fazer:
    # trocas 1v1 trocas 1v1
    #Troca 2v1-A Troca 1v1
    #Troca 2v1-B Troca 2v1-B Troca 1v1
    #Eliminacao
    #Perturbação
    def buscaVizinhos(self,valor):
        if valor == 1:
            self.troca11()
            self.troca11()
            #self.buscaLocal()
        elif valor == 2:
            aux = self.pegaPacote21(1)
            self.troca21A(aux[0], aux[1])
            self.troca11()
            #self.buscaLocal()
        elif valor == 3:
            aux = self.pegaPacote21(2)
            self.troca21A(aux[0], aux[1])
            self.troca21A(aux[0], aux[1])
            self.troca11()
           #self.buscaLocal()
        elif valor == 4:
            self.eliminacao()
        elif valor == 5:
            self.pertubacao()


    #Função de escrita em arquivos, serão escritos os resultados
    def saida(self, nomeArq, instancia, parametro, runtime, objetivo, Iteracao, Quantidade_de_Pacotes):
        dir = f'{nomeArq}.out'
        if os.path.isfile(f'{dir}'):
            opcao = 'a'
        else:
            opcao = 'w'
            with open(dir, opcao) as arq:
                arq.writelines(f'Instancia\tParametro\tRuntime\tObjetivo\tIteração\tQuantidade de Pacotes\n')
            opcao = 'a'
        with open(dir, opcao) as arq:
            arq.write(f'{instancia}\t{parametro}\t{"{0:.2f}".format(runtime)}s\t{objetivo}\t{Iteracao}\t{Quantidade_de_Pacotes}\n')

    #Função que verifica a integridade dos itens e pacotes na solução, ou seja, se nenhuma regra foi quebrada
    def validaDados(self):
        valida = False
        qtdeItens = 0
        for i in self.pacotes:
            qtdeItens += len(i.itens)
            for j in i.itens:
                if j.id in i.listaRestricoes:
                    valida = False
                    print(valida)
                    return

        print(True)
        print(qtdeItens+len(self.listaItens))

    #A execução do VNS segue iterando 7000 vezes, a cada iteração ele executa as seis busca em vizinhaça, caso encontre uma
    #solução melhor que a ja existente é salvado  então
    def executaVNS(self):
        self.lerArquivo()
        inicio = time.time()
        #Inicialmente é ordenado de forma crescente a lista de itens
        self.listaItens = sorted(self.listaItens, key=lambda  Item : Item.peso, reverse=True)
        self.listaItensSeguranca = self.listaItens.copy()
        self.pacotes = []
        #Então gera-se a solução inicial
        self.geraSolucao(self.listaItens, self.pacotes)
        print("\nQuantidade inicial ", len(self.pacotes))
        print("\n")
        self.pacotes = sorted(self.pacotes, key=lambda Box: Box.capacidadeAtual)
        cont = 0
        auxPacotes = self.copia(self.pacotes)
        fim = time.time()
        tempo = fim - inicio
        #Lembrando que o quinto parametro é o LB da instancia
        self.saida('solverVNSLog', sys.argv[1], '-', tempo, 48, cont, len(auxPacotes))
        while cont <= 7000:
            k = 1
            while k < 6:
                self.buscaVizinhos(k)
                if len(self.pacotes) < len(auxPacotes):
                    auxPacotes = self.copia(self.pacotes)
                    print("atualiza na iteração:" + str(cont) + " numero de pacotes:" + str(len(auxPacotes)))
                    fim = time.time()
                    tempo = fim - inicio
                    #Lembrando que o quinto parametro é o LB da instancia
                    self.saida('solverVNSLog', sys.argv[1], '-', tempo, 48, cont, len(auxPacotes))
                k += 1
            cont += 1
            #print(cont)
        fim = time.time()
        tempo = fim - inicio
        self.saida('solverVNSFinal', sys.argv[1], '-', tempo, 48, cont, len(auxPacotes))
        print(f'Devem ser utilizados *{len(auxPacotes)}* pacotes para essa instancia!\n')

if __name__ == '__main__':
    vns = VNS()
    for i in range(100):
        vns.executaVNS()
