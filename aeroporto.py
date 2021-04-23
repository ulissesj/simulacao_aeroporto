import random

import simpy


RANDOM_SEED = 42    
NUM_PISTAS = 1         # NUMERO DE PISTAS 
NUM_FINGERS = 2        # NUMERO DE FINGERS
TAXIAMENTO = 1         # TEMPO DE DESOCUPAÇÃO DA PISTA
DESEMBARQUE = [8,16]   # TEMPO MIN DE DESEMBARQUE
ABASTECIMENTO = [1,5]  # TEMPO MIN DE ABASTECIMENTO(OPCIONAL)
T_INTER = 10           # CRIA UM AVIÃO A CADA 10 MINUTOS
SIM_TIME = 60          # TEMPO DE SIMULAÇÃO EM MINUTOS

class Aeroporto(object):
    def __init__(self, env, num_pistas,num_fingers,taxiamento,):
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
            print("%s abastecendo" %aviao)
            t_abastecimento = random.randint(*ABASTECIMENTO)
        yield self.env.timeout(t_desembarque+t_abastecimento)

#Cada avião tem um 'nome' e chega no aeroporto requerindo uma pista e um finger
def aviao(env,name,aer):
    print('%s está preparando para pousar em %.2f.' % (name, env.now))
    
    #Entra na fila da pista para pousar
    with aer.pista.request() as request:
        yield request

        print('%s pousou e está taxiando em %.2f.' % (name, env.now))
        yield env.process(aer.taxiar(name))
    
    #Entra na fila do finger
    with aer.finger.request() as request:
        yield request

        print('%s está desembarcando em %.2f.' % (name, env.now))
        yield env.process(aer.desembarcar(name))
    
    
    #Entra na fila da pista para decolar
    with aer.pista.request() as request:
        yield request

        print('%s está decolando em %.2f.' % (name, env.now))
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

print("Simuando aeroporto....")
random.seed(RANDOM_SEED) #Ajuda a reproduzir os resultados

#Cria um ambiente e começa o processo de setup
env = simpy.Environment()
env.process(setup(env, NUM_PISTAS, NUM_FINGERS, TAXIAMENTO,T_INTER))

#Executa até o tempo total de simulação
env.run(until=SIM_TIME)
