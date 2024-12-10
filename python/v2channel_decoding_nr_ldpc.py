import numpy as np  # Importa a biblioteca numpy para operações numéricas
import matlab.engine  # Importa a biblioteca para executar o MATLAB a partir do Python
from gnuradio import gr  # Importa o módulo gr do GNU Radio para criar blocos

class blk(gr.basic_block):
  

    def __init__(self, F=0.0, bgn=2.0, itrMax=8, out_msgLen=2560):  
       
        self.F = F  # Fator de codificação, pode ser ajustado conforme a necessidade
        self.bgn = bgn  # Tipo de codificação (geralmente relacionado ao tipo de código usado)
        self.itrMax = itrMax  # Número máximo de iterações para o algoritmo de decodificação
        
        # Define coeficientes baseados no tipo de codificação
        if self.bgn == 1:
            self.coef = 2  # Para bgn=1, o coeficiente é 2
        elif self.bgn == 2:
            self.coef = 5  # Para bgn=2, o coeficiente é 5

        self.received_count = 0  # Contador de bits recebidos
        self.sent_count = 0  # Contador de bits enviados

        # Calcula o comprimento da mensagem de acordo com o coeficiente
        self.msg_len = out_msgLen * self.coef  
        # Buffer para armazenar os bits recebidos (mensagem codificada)
        self.buffer_out = np.zeros(out_msgLen * self.coef, dtype=np.byte)
        # Buffer para armazenar a mensagem decodificada
        self.decoded_msg = np.zeros(out_msgLen, dtype=np.byte)

        # Chama o construtor da classe base do GNU Radio
        gr.basic_block.__init__(self,
            name="Channel Decoding (MATLAB)",  # Nome do bloco no GRC
            in_sig=[np.byte],  # O bloco recebe um sinal de entrada do tipo byte
            out_sig=[np.byte])  # O bloco tem uma saída do tipo byte

        # Inicializa o ambiente MATLAB
        self.eng = matlab.engine.start_matlab()
        # Altera o diretório de trabalho do MATLAB para a pasta especificada
        self.eng.cd(r"G:\Meu Drive\UFRGS\PD\MATLABcodes\MATLABcoder")
        #print('matlab ok')

    def decode(self, message):
       
        message = np.reshape(message, (-1, 1))  # Transforma a mensagem em uma coluna (vetor)
        message = matlab.int8(message)  # Converte a mensagem para o tipo int8 do MATLAB
        # Chama a função MATLAB para decodificar a mensagem
        rxdecod = self.eng.ch_decoder(message, self.F, self.bgn, self.itrMax)
        # Converte o resultado do MATLAB para um array do numpy e o remodela
        rxdecod = np.asarray(rxdecod, dtype=np.byte).reshape(-1)
        return rxdecod

    def general_work(self, input_items, output_items):
   
        
        in0 = input_items[0]  # Referência ao sinal de entrada
        out = output_items[0]  # Referência ao sinal de saída

        # Se ainda não começou a enviar o 'out'
        if self.sent_count == 0:
            # Se ainda há mais bytes para receber
            if self.received_count + len(in0) <= self.msg_len:
                # Popula o buffer com os bits recebidos
                self.buffer_out[self.received_count:self.received_count+len(in0)] = in0[:]
                # Incrementa o contador de bytes recebidos
                self.received_count += len(in0)
            
            if self.received_count != self.msg_len:
                # Consome os bits recebidos, pois ainda não completou a mensagem
                self.consume(0, len(in0))
            
            # Se já recebeu todos os bytes necessários, realiza a decodificação
            if self.received_count == self.msg_len:
                self.received_count = 0
                # Decodifica a mensagem e começa a transmissão dos bits decodificados
                self.decoded_msg[:] = self.decode(self.buffer_out)

                out[:] = self.decoded_msg[:len(out)]  # Preenche a saída com os bits decodificados
                self.sent_count += len(out)  # Atualiza o contador de bits enviados

                return len(out)  # Retorna a quantidade de bits enviados
            else:
                return 0  # Retorna 0 se ainda não completou a mensagem para decodificar

        # Se a transmissão já foi iniciada (sent_count != 0)
        else:
            # Se ainda há mais bits para enviar
            if self.sent_count + len(out) < len(self.decoded_msg):
                out[:] = self.decoded_msg[self.sent_count : self.sent_count + len(out)]  # Envia os bits
                self.sent_count += len(out)  # Atualiza o contador de bits enviados
            # Se o número de bits a ser enviado é maior que os bits restantes
            else:
                # Envia o restante da mensagem decodificada
                out[:len(self.decoded_msg)-self.sent_count] = self.decoded_msg[self.sent_count:]
                self.sent_count += len(self.decoded_msg) - self.sent_count  # Atualiza o contador

            # Se todos os bits da mensagem foram enviados
            if self.sent_count == len(self.decoded_msg):
                # Consome os bits recebidos do buffer
                self.consume(0, len(in0))

            return len(out)  # Retorna a quantidade de bits enviados
