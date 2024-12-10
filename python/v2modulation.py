import numpy as np  # Importa a biblioteca numpy para manipulação de dados numéricos
import matlab.engine  # Permite chamar funções do MATLAB diretamente do Python
from gnuradio import gr  # Importa o módulo do GNU Radio para criação de blocos de processamento de sinal

class blk(gr.basic_block):  # Definindo o bloco de modulação no GNU Radio
    def __init__(self, M=1):  # Parâmetro M define a ordem da modulação (por exemplo, M=1 para BPSK)
        
        # Inicializa a classe base gr.basic_block com o nome do bloco e os tipos de entrada e saída
        gr.basic_block.__init__(self,
            name='Modulation (MATLAB)',  # Nome do bloco, aparecerá no GRC
            in_sig=[np.byte],  # Entrada: tipo byte (dados binários)
            out_sig=[np.csingle]  # Saída: tipo complexo (single)
        )
        
        self.M = M  # Ordem da modulação (pode ser usado para diferentes esquemas como BPSK, QPSK etc.)

        self.mod_message = None  # Variável para armazenar a mensagem modulada
        self.sent_count = 0  # Contador de bits enviados até o momento

        # Inicia uma sessão do MATLAB e define o diretório de trabalho
        self.eng = matlab.engine.start_matlab()
        self.eng.cd(r"G:\Meu Drive\UFRGS\PD\MATLABcodes\MATLABcoder")

    def modulate(self, message):  # Função que chama a modulação MATLAB
        # Reshape da mensagem para garantir que seja um vetor coluna
        message = np.reshape(message, (-1, 1))  
        message = matlab.int8(message)  # Converte a mensagem para o tipo inteiro de 8 bits do MATLAB
        # Chama a função de modulação MATLAB
        txmod = self.eng.modulate(message, self.M)
        # Converte o resultado de volta para um array numpy e remodela para uma dimensão 1D
        txmod = np.asarray(txmod, dtype=np.csingle).reshape(-1)
        return txmod  # Retorna a mensagem modulada

    def general_work(self, input_items, output_items):  # Função principal que processa os dados
        in0 = input_items[0]  # Sinal de entrada (mensagem a ser modulada)
        out = output_items[0]  # Sinal de saída (mensagem modulada)

        # Se for a primeira vez que está enviando dados (sent_count == 0)
        if self.sent_count == 0:
            self.message_len = len(in0)  # Armazena o comprimento da mensagem
            # Modula a mensagem de entrada
            self.mod_message = self.modulate(np.reshape(in0, (-1, 1)))
        
        # Se ainda houver bits para enviar
        if self.sent_count + len(out) < len(self.mod_message):
            out[:] = self.mod_message[self.sent_count:self.sent_count + len(out)]  # Preenche a saída com os bits
            out_len = len(out)  # Quantidade de bits enviados
        else:
            # Envia os bits restantes
            to_send = self.mod_message[self.sent_count:]
            out_len = len(to_send)
            out[:out_len] = to_send  # Preenche a saída com os bits restantes
        
        self.sent_count += out_len  # Atualiza o contador de bits enviados

        # Se todos os bits foram enviados
        if self.sent_count >= len(self.mod_message):
            self.sent_count = 0  # Reseta o contador de bits enviados
            self.mod_message = None  # Limpa a mensagem modulada
            print(f'Consuming {self.message_len} coded bits...')  # Informa que os bits foram consumidos
            self.consume(0, self.message_len)  # Consome os bits, já que a modulação foi concluída
            self.message_len = 0  # Reseta o comprimento da mensagem

        print(f'Sending {out_len} modulated bits...')  # Informa a quantidade de bits modulados enviados
        
        return out_len  # Retorna o número de bits enviados
