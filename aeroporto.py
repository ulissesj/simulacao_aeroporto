import random

import simpy


RANDOM_SEED = 42    
NUM_PISTAS = 1    # NUMERO DE PISTAS 
NUM_FINGERS = 2   # NUMERO DE FINGERS
TAXIAMENTO = 1    # TEMPO DE DESOCUPAÇÃO DA PISTA
DESEMBARQUE = 8   # TEMPO DE DESEMBARQUE
CAMINHOES = 2     # CAMINHÕES DE ABASTECIMENTO
ABASTECIMENTO = 5 # TEMPO DE ABASTECIMENTO(OPCIONAL)
T_INTER = 15      # CRIA UM AVIÃO A CADA 15 MINUTOS
SIM_TIME = 60     # TEMPO DE SIMULAÇÃO EM MINUTOS

class Aeroporto(object):
    def __init__(self, env, num_pistas,num_fingers,desembarque,taxiamento,abastecimento, n_caminhoes):
        self.env = env
        self.finger = simpy.Resource(env,num_fingers)
        self.pista = simpy.Resource(env, num_pistas)
        self.caminhoes = simpy.Resource(env, n_caminhoes)
        self.desembarque = desembarque
        self.taxiamento = taxiamento
        self.abastecimento = abastecimento
    
    #Processo de taxiar a aeronave, no pouso e na decolagem
    def taxiar(self,aviao):
        yield self.env.timeout(TAXIAMENTO)
    
    #Processo de embarcar/desembarcar passageiros
    def desembarcar(self,aviao):
        n = random.randint(0,1)
        if(n==1):
            print("%s abastecendo..." %(aviao))
            yield self.env.timeout(DESEMBARQUE+ABASTECIMENTO)
        else:
            yield self.env.timeout(DESEMBARQUE)

    #Processo de abastecer a aeronave
    def abastecer(self,aviao):
        yield self.env.timeout(ABASTECIMENTO)

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
    
    #Entra na fila de abastecimento
    """with aer.caminhoes.request() as request:
        yield request

        print('%s está abastecendo em %.2f.' % (name, env.now))
        yield env.process(aer.abastecer(name))"""
    
    #Entra na fila da pista para decolar
    with aer.pista.request() as request:
        yield request

        print('%s está decolando em %.2f.' % (name, env.now))
        yield env.process(aer.taxiar(name))

#Setup do ambiente, cria um aeroporto, aviões iniciais e mais aviões como decorrer do tempo
def setup(env, num_pistas,num_fingers,t_taxiamento, t_desembarque, t_abastecimento, n_caminhoes, t_inter):
    aeroporto = Aeroporto(env, num_pistas,num_fingers,t_desembarque,t_taxiamento,t_abastecimento,n_caminhoes)

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
env.process(setup(env, NUM_PISTAS, NUM_FINGERS, TAXIAMENTO, DESEMBARQUE,ABASTECIMENTO,CAMINHOES,T_INTER))

#Executa
env.run(until=SIM_TIME)
