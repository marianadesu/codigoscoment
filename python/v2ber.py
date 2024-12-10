import numpy as np  # Importa a biblioteca numpy para operações numéricas
from gnuradio import gr  # Importa o módulo gr do GNU Radio para criar blocos

class blk(gr.basic_block):  # Define a classe 'blk', que herda de 'gr.basic_block'
  
    def __init__(self):  # Construtor, inicializa o bloco e seus parâmetros
        gr.basic_block.__init__(
            self,  # Chama o construtor da classe base
            name='Coded BER (PYTHON)',  # Nome do bloco que aparecerá no GRC
            in_sig=[np.byte, np.byte],  # Especifica que o bloco recebe dois sinais de entrada de tipo byte
            out_sig=[np.float32]  # Especifica que o bloco tem uma saída do tipo float32
        )

        self.bit_count = 0  # Inicializa o contador de bits processados
        self.error_count = 0  # Inicializa o contador de erros

    def general_work(self, input_items, output_items):  # Função principal de processamento do bloco
        # Referência aos buffers de entrada e saída
        print('====== BER ======')  # Exibe uma mensagem indicando que o cálculo do BER começou
        in0 = input_items[0]  # Primeiro sinal de entrada (dados originais)
        in1 = input_items[1]  # Segundo sinal de entrada (dados recebidos)
        out = output_items[0]  # Saída do bloco

        # Exibe o tamanho dos sinais de entrada
        print(f'(BER) Tamanho original: {len(in0)}, Tamanho recebido: {len(in1)}')

        inlen = min([len(in0), len(in1)])  # Define o comprimento mínimo entre os dois sinais para compará-los

        # Seleciona os dados até o comprimento mínimo calculado
        in0_use = in0[:inlen]
        in1_use = in1[:inlen]

        # Atualiza os contadores de bits e erros
        self.bit_count += inlen  # Incrementa o número de bits processados
        self.error_count += np.sum(in0_use^in1_use)  # Incrementa o número de erros (XOR entre os bits de in0 e in1)

        # Exibe a quantidade de erros encontrados
        print(f'{self.error_count} erros em {self.bit_count} bits...')

        # Consome as amostras dos sinais de entrada
        self.consume(0, inlen)
        self.consume(1, inlen)

        # Calcula a Taxa de Erro de Bits (BER)
        out[0] = self.error_count / self.bit_count  # O valor do BER é a razão entre erros e total de bits

        # Exibe o BER calculado
        print(f'BER codificado: {out[0]*100:.6f}%')

        return 1  # Retorna 1 indicando que o processamento foi bem-sucedido
