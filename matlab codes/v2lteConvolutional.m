%=================% 
%    PARAMETERS   % 
%=================% 

% Definindo o comprimento do bloco de código
K = 2400;  % Tamanho do bloco de código (número de bits)

% Definindo a relação Eb/No (dB) para avaliação
EbNo = linspace(-2, 18, 21);  % Variação de Eb/No (de -2 a 18 dB)

% Número de blocos de dados simulados
Nblocks = 10^2;

% Inicializando variáveis para armazenar o número de erros de bits e blocos
Nbiterrs = zeros(4, length(EbNo));  % Erros de bit por modulação e EbNo
Nblkerrs = zeros(4, length(EbNo));  % Erros de bloco por modulação e EbNo

% Inicializando variáveis para erros sem codificação
Nbiterrs_uncoded = zeros(4, length(EbNo));  % Erros de bit sem codificação
Nblkerrs_uncoded = zeros(4, length(EbNo));  % Erros de bloco sem codificação

%=================% 
%    SIMULATION   % 
%=================% 

tic  % Inicia o cronômetro para medir o tempo de execução

% Laço para simular diferentes modulações: 1: QPSK, 2: 16QAM, 3: 64QAM, 4: 256QAM
for mod = 1:4
    % Definindo a ordem da modulação QAM (M) com base no valor de 'mod'
    M = 4^mod;  % M é a ordem da modulação (4, 16, 64, 256)
    
    % Gerando a constelação QAM com M símbolos e normalizando a potência média
    alphabet = qammod(0:M-1, M, 'UnitAveragePower', true);
    sigpwr = pow2db(mean(abs(alphabet).^2));  % Potência média dos símbolos

    % Laço para simular a transmissão de Nblocks blocos de dados
    for block = 1:Nblocks
        %=================% 
        %  CHANNEL CODER  % 
        %=================% 
        % Gerando uma sequência de bits aleatórios para o bloco de dados
        txcbs = randi([0 1], K, 1);  % Bloco de código aleatório
        txcodedcbs = lteConvolutionalEncode(txcbs);  % Codificação convolucional LTE
    
        %=================% 
        %    MODULATION   % 
        %=================% 
        % Modulação QAM dos bits codificados
        txmodcbs = qammod(txcodedcbs, M, 'InputType', 'bit', 'UnitAveragePower', true);
        % Modulação QAM dos bits não codificados (para comparação)
        txmodcbs_uncoded = qammod(txcbs, M, 'InputType', 'bit', 'UnitAveragePower', true);
        
        % Laço para testar diferentes valores de Eb/No
        for n = 1:length(EbNo)
            %=================% 
            %  AWGN CHANNEL   % 
            %=================% 
            % Definindo o canal AWGN (Ruído Branco Aditivo Gaussiano)
            awgn_ch = comm.AWGNChannel('EbNo', EbNo(n), 'BitsPerSymbol', log2(M));
            % Gerando o sinal recebido com ruído AWGN
            rxsig = awgn_ch(txmodcbs);  % Sinal com codificação
            rxsig_uncoded = awgn_ch(txmodcbs_uncoded);  % Sinal sem codificação
         
            %=================% 
            %   DEMODULATION  % 
            %=================% 
            % Demodulação dos sinais recebidos (soft bits)
            rxdemod = qamdemod(rxsig, M, 'OutputType', 'bit', 'UnitAveragePower', true);
            rxdemod_uncoded = qamdemod(rxsig_uncoded, M, 'OutputType', 'bit', 'UnitAveragePower', true);
            
            %=================% 
            % CHANNEL DECODER % 
            %=================% 
            % Converte os bits demodulados para soft bits (para decodificação)
            rxdecod = double(2*rxdemod - 1);  % Converte para valores [-1, 1] (soft bits)
            % Decodificação convolucional dos bits recebidos
            rxcbs = lteConvolutionalDecode(rxdecod);
        
            %=================% 
            %     ANALYSIS    % 
            %=================% 
            % Conta os erros de bit (comparando bits decodificados com os bits transmitidos)
            Nerrs = sum(double(rxcbs) ~= txcbs);
            if Nerrs > 0
                Nbiterrs(mod, n) = Nbiterrs(mod, n) + Nerrs;  % Soma erros de bit
                Nblkerrs(mod, n) = Nblkerrs(mod, n) + 1;  % Soma erros de bloco
            end
    
            % Erros de bit e bloco para o caso sem codificação
            Nerrs = sum(rxdemod_uncoded ~= txcbs);
            if Nerrs > 0
                Nbiterrs_uncoded(mod, n) = Nbiterrs_uncoded(mod, n) + Nerrs;
                Nblkerrs_uncoded(mod, n) = Nblkerrs_uncoded(mod, n) + 1;
            end
        end
        
        % Exibe o progresso da simulação a cada metade dos blocos
        if rem(block, Nblocks/2) == 0
            fprintf('%d %.0f%% ', mod, block/Nblocks*100)
        end
    end
end

toc  % Finaliza o cronômetro

% Calculando a Taxa de Erro de Bit (BER) para cada esquema de modulação
BER = Nbiterrs ./ (K * Nblocks);
BER_uncoded = Nbiterrs_uncoded ./ (K * Nblocks);

% Plotando os resultados
f = figure;
semilogy(EbNo, BER_uncoded(1, :), '--', 'color', '#0072BD', 'LineWidth', 0.6);  % Curva para QPSK sem codificação
hold on
semilogy(EbNo, BER(1, :), '*-', 'color', '#0072BD', 'LineWidth', 1.3);  % Curva para QPSK com codificação

semilogy(EbNo, BER_uncoded(2, :), '--', 'color', '#D95319', 'LineWidth', 0.6);  % Curva para 16-QAM sem codificação
semilogy(EbNo, BER(2, :), '*-', 'color', '#D95319', 'LineWidth', 1.3);  % Curva para 16-QAM com codificação

semilogy(EbNo, BER_uncoded(3, :), '--', 'color', '#EDB120', 'LineWidth', 0.6);  % Curva para 64-QAM sem codificação
semilogy(EbNo, BER(3, :), '*-', 'color', '#EDB120', 'LineWidth', 1.3);  % Curva para 64-QAM com codificação

semilogy(EbNo, BER_uncoded(4, :), '--', 'color', '#7E2F8E', 'LineWidth', 0.6);  % Curva para 256-QAM sem codificação
semilogy(EbNo, BER(4, :), '*-', 'color', '#7E2F8E', 'LineWidth', 1.3);  % Curva para 256-QAM com codificação
hold off

% Adicionando rótulos ao gráfico
xlabel("Eb/No (dB)");
ylabel("BER");
ylim([10^(-5) 10^(0.1)]);  % Definindo o limite do eixo y
xlim([min(EbNo) max(EbNo)]);  % Definindo o limite do eixo x
grid on;  % Adicionando grade ao gráfico

% Adicionando legenda
legend("Uncoded QPSK", "LTE-Conv. QPSK", "Uncoded 16-QAM", "LTE-Conv. 16-QAM", ...
       "Uncoded 64-QAM", "LTE-Conv. 64-QAM", "Uncoded 256-QAM", "LTE-Conv. 256-QAM");
