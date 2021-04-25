import random

import simpy


RANDOM_SEED = 42    
NUM_PISTAS = 1         # NUMERO DE PISTAS 
NUM_FINGERS = 2        # NUMERO DE FINGERS
TAXIAMENTO = 1         # TEMPO DE DESOCUPAÇÃO DA PISTA
DESEMBARQUE = [8,16]   # TEMPO MIN DE DESEMBARQUE
ABASTECIMENTO = [1,5]  # TEMPO MIN DE ABASTECIMENTO(OPCIONAL)
T_INTER = 10            # CRIA UM AVIÃO A CADA 10 MINUTOS
SIM_TIME = 60          # TEMPO DE SIMULAÇÃO EM 

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
        stat.new_completion()

for i in range(5):
    print("Simuando aeroporto....")
    TOTAL_ESPERA = []
    random.seed(RANDOM_SEED+i+7) #Ajuda a reproduzir os resultados

    stat = Stats() #Cria o objeto de status

    #Cria um ambiente e começa o processo de setup
    env = simpy.Environment()
    env.process(setup(env, NUM_PISTAS, NUM_FINGERS, TAXIAMENTO,T_INTER))

    #Executa até o tempo total de simulação
    env.run(until=SIM_TIME)

    #Status
    stat.report()
    print ('Taxa de Chegadas: %.2f aviões por hora' % (stat.num_arrivals/(env.now/60)))
    print ('Taxa de Decolagens (Throughput): %.2f aviões por hora' % (stat.num_complet/(env.now/60)))
    print ('Tempo Médio de Serviço: %.2f minutos' % (env.now/stat.num_complet))
    print ('Tempo Médio de espera: %.2f minutos' % (sum(TOTAL_ESPERA)/stat.num_arrivals))
    print ('--> %.2f%% dos aviões atendidos' % ((stat.num_complet*100)/stat.num_arrivals))
