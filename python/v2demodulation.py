import numpy as np  # Importa a biblioteca numpy para operações numéricas
import matlab.engine  # Importa a biblioteca para interagir com o MATLAB a partir do Python
from gnuradio import gr  # Importa o módulo gr do GNU Radio para criar blocos

class blk(gr.basic_block):  # Definição da classe do bloco de demodulação
    def __init__(self, M=4):  # Inicializa o bloco, M é a ordem da modulação (ex: 4 para QPSK)
        # Chama o construtor da classe base do GNU Radio
        gr.basic_block.__init__(self,
            name='Demodulation (MATLAB)',  # Nome do bloco, que aparecerá no GRC
            in_sig=[np.csingle],  # Tipo do sinal de entrada: número complexo (single)
            out_sig=[np.byte]  # Tipo do sinal de saída: byte
        )
        
        self.M = M  # Atribui a ordem da modulação (ex: 4 para QPSK)

        self.demod_message = None  # Variável para armazenar a mensagem demodulada
        self.sent_count = 0  # Contador de bits enviados

        # Inicializa o ambiente MATLAB
        self.eng = matlab.engine.start_matlab()
        # Altera o diretório de trabalho do MATLAB para o especificado
        self.eng.cd(r"G:\Meu Drive\UFRGS\PD\MATLABcodes\MATLABcoder")

    def demodulate(self, message):  # Função que realiza a demodulação utilizando MATLAB
        message = np.reshape(message, (-1, 1))  # Transforma a mensagem em um vetor coluna
        message = matlab.single(message, is_complex=True)  # Converte a mensagem para o tipo complexo do MATLAB
        # Chama a função de demodulação no MATLAB
        rxdemod = self.eng.demodulate(message, self.M)
        # Converte o resultado do MATLAB de volta para um array numpy e remodela
        rxdemod = np.asarray(rxdemod, dtype=np.byte).reshape(-1)
        return rxdemod  # Retorna a mensagem demodulada

    def general_work(self, input_items, output_items):  # Função principal de processamento
        in0 = input_items[0]  # Referência ao sinal de entrada (sinal modulado)
        out = output_items[0]  # Referência ao sinal de saída (sinal demodulado)

        # Se ainda não começou a enviar os bits demodulados
        if self.sent_count == 0:
            self.message_len = len(in0)  # Armazena o comprimento da mensagem
            self.demod_message = self.demodulate(in0)  # Demodula a mensagem recebida
        
        # Se ainda há mais bits a enviar da mensagem demodulada
        if self.sent_count + len(out) < len(self.demod_message):
            out[:] = self.demod_message[self.sent_count:self.sent_count + len(out)]  # Envia os bits
            out_len = len(out)
        else:
            to_send = self.demod_message[self.sent_count:]  # Envia os bits restantes
            out_len = len(to_send)
            out[:out_len] = to_send
        
        # Atualiza o contador de bits enviados
        self.sent_count += out_len

        # Se todos os bits da mensagem já foram enviados
        if self.sent_count >= len(self.demod_message):
            self.sent_count = 0  # Reseta o contador de bits enviados
            self.demod_message = None  # Limpa a mensagem demodulada
            # Consome os bits recebidos, já que a transmissão foi concluída
            self.consume(0, self.message_len)
            self.message_len = 0  # Reseta o comprimento da mensagem

        return out_len  # Retorna a quantidade de bits enviados
