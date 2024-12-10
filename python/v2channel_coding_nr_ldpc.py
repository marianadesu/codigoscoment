import numpy as np  # Importa a biblioteca numpy para operações numéricas
import matlab.engine  # Importa a biblioteca para executar o MATLAB a partir do Python
from gnuradio import gr  # Importa o módulo gr do GNU Radio para criar blocos

class blk(gr.basic_block):

    def __init__(self, F=0.0, bgn=2.0):  
        
        self.F = F  # Filler (preenchimento) bits, com valor padrão de 0
        self.bgn = bgn  # Número do gráfico base (padrão 2)

        self.coded_message = None  # Variável para armazenar a mensagem codificada
        self.sent_count = 0  # Contador de bits enviados

        # Chama o construtor da classe base do GNU Radio
        gr.basic_block.__init__(self,
            name="Channel Coding (MATLAB)",  # Nome do bloco no GRC
            in_sig=[np.byte],  # O bloco recebe um sinal de entrada do tipo byte
            out_sig=[np.byte])  # O bloco tem uma saída do tipo byte

        # Inicializa o ambiente MATLAB
        self.eng = matlab.engine.start_matlab()
        # Altera o diretório de trabalho do MATLAB para a pasta especificada
        self.eng.cd(r"G:\Meu Drive\UFRGS\PD\MATLABcodes\MATLABcoder")

    def encode(self, message):
        
        message = np.reshape(message, (-1, 1))  # Transforma a mensagem em uma coluna (vetor)
        message = matlab.int8(message)  # Converte a mensagem para o tipo int8 do MATLAB
        # Chama a função MATLAB para codificar a mensagem com parâmetros F e bgn
        txcoded = self.eng.ch_coder(message, self.F, self.bgn)
        # Converte o resultado do MATLAB para um array do numpy e o remodela
        txcoded = np.asarray(txcoded, dtype=np.byte).reshape(-1)
        return txcoded

    def general_work(self, input_items, output_items):
      
        
        in0 = input_items[0]  # Referência ao sinal de entrada
        out = output_items[0]  # Referência ao sinal de saída

        # Exibe os primeiros 10 bits de entrada (para depuração)
        print(f'bits in: {in0[:10]}')

        # Se não há mensagem para enviar ou se já terminou de enviar a mensagem
        if self.sent_count == 0:
            # Codifica a mensagem e deixa ela pronta para ser enviada
            self.message_len = len(in0)  # Armazena o tamanho da mensagem
            self.coded_message = self.encode(in0)  # Codifica a mensagem

        # Se ainda há mais bits da mensagem para enviar
        if self.sent_count + len(out) < len(self.coded_message):
            # Envia 'len(out)' bits
            out[:] = self.coded_message[self.sent_count:self.sent_count + len(out)]
            out_len = len(out)  # Armazena a quantidade de bits enviados
        else:
            # Se restam entre 0 e len(out) bits (últimos bits da mensagem), envia os que restam
            to_send = self.coded_message[self.sent_count:]  # Pega os bits restantes
            out_len = len(to_send)  # Define a quantidade de bits a ser enviada
            out[:out_len] = to_send  # Envia os bits restantes

        # Atualiza o contador de bits enviados
        self.sent_count += out_len

        # Se todos os bits da mensagem foram enviados
        if self.sent_count >= len(self.coded_message):
            # Reseta o contador de bits enviados
            self.sent_count = 0
            self.coded_message = None  # Limpa a mensagem codificada
            print(f'Consuming {self.message_len} uncoded bits...')
            # Tira a mensagem da fila de entrada apenas agora
            self.consume(0, self.message_len)
            self.message_len = 0
        
        # Exibe os primeiros 10 bits de saída (para depuração)
        print(f'bits out: {out[:10]}')
        print(f'Sending {out_len} coded bits...')
        # Retorna a quantidade de bits enviados
        return out_len
