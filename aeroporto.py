import random
import math
import simpy

ITERACOES = 5

RANDOM_SEED = 42    
NUM_PISTAS = 3         # NUMERO DE PISTAS 
NUM_FINGERS = 9        # NUMERO DE FINGERS
TAXIAMENTO = 1         # TEMPO DE DESOCUPAÇÃO DA PISTA
DESEMBARQUE = [8,16]   # TEMPO MIN DE DESEMBARQUE
ABASTECIMENTO = [3,15]  # TEMPO MIN DE ABASTECIMENTO(OPCIONAL)
T_INTER = 2            # CRIA UM AVIÃO A CADA T_INTER MINUTOS
SIM_TIME = 60          # TEMPO DE SIMULAÇÃO EM 

MEDIA_NUM_ARRIVALS = []
MEDIA_NUM_COMPLET = []
MEDIA_TAXA_CHEGADAS = []
MEDIA_TAXA_DECOL = []
MEDIA_TEMPO_SERVICO = []
MEDIA_ESPERA = []
MEDIA_PORCENTAGEM_ATENDIDOS = []
MEDIA_AVIOES_NA_FILA = []

class Stats():
    """ Mantem as principais estatisticas da simulacao em curso
	"""
    def __init__(self):
        self.num_arrivals = 0
        self.num_complet = 0
		
    def new_arrival(self):
        self.num_arrivals+=1
			
    def new_completion(self):
        self.num_complet+=1
		
    def report(self):
        print ('\n*** SimPy Relatório de Simulação ***\n')
        print ('Tempo Total de Simulação: %.4f' % SIM_TIME)
        print ('Chegadas Totais: %d' % self.num_arrivals)
        print ('Decolagens Totais: %d' % self.num_complet)

class Aeroporto(object):
    def __init__(self, env, num_pistas,num_fingers,taxiamento):
        self.env = env
        self.finger = simpy.Resource(env,num_fingers)
        self.pista = simpy.Resource(env, num_pistas)
        self.taxiamento = taxiamento
    
    #Processo de taxiar a aeronave, no pouso e na decolagem
    def taxiar(self,aviao):
        yield self.env.timeout(TAXIAMENTO)
    
    #Processo de embarcar/desembarcar passageiros + abastecer(opcional)
    def desembarcar(self,aviao):
        t_desembarque = random.randint(*DESEMBARQUE)
        t_abastecimento = 0
        n = random.randint(0,1) #Se for abastecer ou não(0 ou 1)
        if(n==1): #Se abastecer
            #print("%s abastecendo" %aviao)
            t_abastecimento = random.randint(*ABASTECIMENTO)
        yield self.env.timeout(t_desembarque+t_abastecimento)


#Cada avião tem um 'nome' e chega no aeroporto requerindo uma pista e um finger
def aviao(env,name,aer):
    stat.new_arrival()

    #print('%s está preparando para pousar em %.2f.' % (name, env.now))
    
    #Entra na fila da pista para pousar
    with aer.pista.request() as request:
        yield request

        AVIOES_NA_FILA.append(1)
        #print('%s pousou e está taxiando em %.2f.' % (name, env.now))
        t_taxiar = env.now + TAXIAMENTO
        yield env.process(aer.taxiar(name))
    
    #Entra na fila do finger
    with aer.finger.request() as request:
        yield request
        espera = env.now-t_taxiar
        TOTAL_ESPERA.append(espera)
        #print('%s está desembarcando em %.2f Espera %.2f.' % (name, env.now, espera))
        yield env.process(aer.desembarcar(name))
    
    #Entra na fila da pista para decolar
    with aer.pista.request() as request:
        yield request

        #print('%s está decolando em %.2f.' % (name, env.now))
        yield env.process(aer.taxiar(name))
        AVIOES_NA_FILA.pop()
        stat.new_completion()

#Setup do ambiente, cria um aeroporto, aviões iniciais e mais aviões como decorrer do tempo
def setup(env, num_pistas,num_fingers,t_taxiamento,t_inter):
    aeroporto = Aeroporto(env, num_pistas,num_fingers,t_taxiamento)

    #Cria os dois primeiros aviões
    for i in range(2):
        env.process(aviao(env, 'Avião %d' % i, aeroporto))
    
    #Cria os aviões enquanto a simulação roda
    while True:
        yield env.timeout(random.randint(t_inter - 2, t_inter + 2))
        i+=1
        env.process(aviao(env, 'Avião %d' %i, aeroporto))

#Calcular desvio padrão
def desvio_padrao(vet_valores):    
    ni = 0
    media = sum(vet_valores)/ITERACOES 
    for x in range(len(vet_valores)):
        ni += pow(media - vet_valores[x],2) #soma o quadrado da diferença entre a media e o valor
    dp = math.sqrt(ni/len(vet_valores)) #tira a raiz do resultado da soma sobre o numero de valores
    return dp


for i in range(ITERACOES):
    #print("Simulando aeroporto....")
    TOTAL_ESPERA = []
    AVIOES_NA_FILA = []
    random.seed(RANDOM_SEED+i+7) #Ajuda a reproduzir os resultados

    stat = Stats() #Cria o objeto de status

    #Cria um ambiente e começa o processo de setup
    env = simpy.Environment()
    env.process(setup(env, NUM_PISTAS, NUM_FINGERS, TAXIAMENTO,T_INTER))

    #Executa até o tempo total de simulação
    env.run(until=SIM_TIME)

    #Status

    MEDIA_NUM_ARRIVALS.append(stat.num_arrivals)
    MEDIA_NUM_COMPLET.append(stat.num_complet)
    MEDIA_TAXA_CHEGADAS.append(stat.num_arrivals/(env.now/60))
    MEDIA_TAXA_DECOL.append(stat.num_complet/(env.now/60))
    MEDIA_TEMPO_SERVICO.append(env.now/stat.num_complet)
    MEDIA_ESPERA.append(sum(TOTAL_ESPERA)/stat.num_arrivals)
    MEDIA_PORCENTAGEM_ATENDIDOS.append((stat.num_complet*100)/stat.num_arrivals)
    MEDIA_AVIOES_NA_FILA.append(len(AVIOES_NA_FILA))

print("Simulando aeroporto....")
print ('\n*** SimPy Relatório de Simulação ***')
print ('\n*** VALORES MÉDIOS PARA %d ITERACOES ***\n' % ITERACOES)
print ('Tempo Total de Simulação: %.2f' % SIM_TIME)
print ('Chegadas Totais: %d' % (sum(MEDIA_NUM_ARRIVALS)/ITERACOES))
print ('Decolagens Totais: %d' % (sum(MEDIA_NUM_COMPLET)/ITERACOES))
print ('Taxa de Chegadas: %.2f aviões por hora' % (sum(MEDIA_TAXA_CHEGADAS)/ITERACOES))
print ('Taxa de Decolagens (Throughput): %.2f aviões por hora' % (sum(MEDIA_TAXA_DECOL)/ITERACOES))
print ('Tempo Médio de Serviço: %.2f minutos' % (sum(MEDIA_TEMPO_SERVICO)/ITERACOES))
print ('Tempo Médio de espera: %.2f minutos' % (sum(MEDIA_ESPERA)/ITERACOES))
print ('-->%.2f%% dos aviões atendidos' % (sum(MEDIA_PORCENTAGEM_ATENDIDOS)/ITERACOES))
print ('-->%d aviões na fila' % (sum(MEDIA_AVIOES_NA_FILA)/ITERACOES))

#Stats espera
dp_espera = desvio_padrao(MEDIA_ESPERA)
inferior_espera = sum(MEDIA_ESPERA)/ITERACOES - 2.776*(dp_espera/math.sqrt(ITERACOES))
superior_espera = sum(MEDIA_ESPERA)/ITERACOES + 2.776*(dp_espera/math.sqrt(ITERACOES))
print ('\nDesvio padrão de espera: %.2f minutos' %dp_espera )
print("Intervalo de confiança 95% entre", inferior_espera, " e ", superior_espera)

#Stats serviço
dp_servico = desvio_padrao(MEDIA_TEMPO_SERVICO)
inferior_servico = sum(MEDIA_TEMPO_SERVICO)/ITERACOES - 2.776*(dp_servico/math.sqrt(ITERACOES))
superior_servico = sum(MEDIA_TEMPO_SERVICO)/ITERACOES + 2.776*(dp_servico/math.sqrt(ITERACOES))
print ('\nDesvio padrão de serviço: %.2f minutos' %dp_servico )
print("Intervalo de confiança 95% entre", inferior_servico, " e ", superior_servico)

#Stats decolagens
dp_decolagens = desvio_padrao(MEDIA_TAXA_DECOL)
inferior_decolagens = sum(MEDIA_TAXA_DECOL)/ITERACOES - 2.776*(dp_decolagens/math.sqrt(ITERACOES))
superior_decolagens = sum(MEDIA_TAXA_DECOL)/ITERACOES + 2.776*(dp_decolagens/math.sqrt(ITERACOES))
print ('\nDesvio padrão de decolagens: %.2f' %dp_decolagens )
print("Intervalo de confiança 95% entre", inferior_decolagens, " e ", superior_decolagens)

#Stats aviões atendidos
dp_avioes_atendidos = desvio_padrao(MEDIA_PORCENTAGEM_ATENDIDOS)
inferior_avat = sum(MEDIA_PORCENTAGEM_ATENDIDOS)/ITERACOES - 2.776*(dp_avioes_atendidos/math.sqrt(ITERACOES))
superior_avat = sum(MEDIA_PORCENTAGEM_ATENDIDOS)/ITERACOES + 2.776*(dp_avioes_atendidos/math.sqrt(ITERACOES))
print ('\nDesvio padrão de %% aviões atendidos: %.2f' %dp_avioes_atendidos )
print("Intervalo de confiança 95% entre", inferior_avat, " e ", superior_avat)
