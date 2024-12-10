%=================%
%    PARÂMETROS   %
%=================% 
% Parâmetros de codificação
bgn = 1;    
K = 2640;   )
F = 0;      

% Parâmetros do canal
EbNo = linspace(-2, 18, 21);  % Intervalo de Eb/No (relação sinal-ruído em dB)

% Parâmetros do decodificador
itrMax = 6;  

% Inicialização da taxa de erro de bits (BER)
Nblocks = 10^2;  

% Matrizes para armazenar as contagens de erros de bits e de blocos para os cenários codificados e não codificados
Nbiterrs = zeros(4,length(EbNo));   
Nblkerrs = zeros(4,length(EbNo));    

Nbiterrs_uncoded = zeros(4,length(EbNo)); 
Nblkerrs_uncoded = zeros(4,length(EbNo));  

%=================%
%    SIMULAÇÃO    %
%=================%
tic  % Inicia o cronômetro para medir o tempo da simulação

% Loop sobre os diferentes tipos de modulação (QPSK, 16-QAM, 64-QAM, 256-QAM)
for mod = 1:4  
    M = 4^mod;  
    alphabet = qammod(0:M-1,M,'UnitAveragePower',true);  
    sigpwr = pow2db(mean(abs(alphabet).^2));  
    
    % Loop sobre os blocos de dados a serem transmitidos
    for block = 1:Nblocks
        %=================%
        %  CODIFICADOR DO CANAL  %
        %=================% 
        txcbs = randi([0 1],K-F, 1); % Geração de segmentos de blocos de código (dados binários aleatórios)
        txcodedcbs = nrLDPCEncode(txcbs, bgn);  % Codificação LDPC do bloco de código
        
        %=================%
        %    MODULAÇÃO    %
        %=================%
        % Preparação dos dados para modulação
        databit = txcodedcbs;  % Dados codificados a serem modulados
    
        % Modulação QAM dos dados codificados
        txmodcbs = qammod(databit,M,'InputType','bit','UnitAveragePower',true);  
        txmodcbs_uncoded = qammod(txcbs,M,'InputType','bit','UnitAveragePower',true);  % Modulação dos dados não codificados
        
        % Loop sobre os diferentes valores de Eb/No (para simulação do canal AWGN)
        for n = 1:length(EbNo)
            %=================%
            %  CANAL AWGN    %
            %=================%
            awgn_ch = comm.AWGNChannel('EbNo',EbNo(n),'BitsPerSymbol',log2(M));  % Canal AWGN com Eb/No
            rxsig = awgn_ch(txmodcbs);  % Sinal recebido com ruído AWGN para sinais codificados
            rxsig_uncoded = awgn_ch(txmodcbs_uncoded);  % Sinal recebido com ruído AWGN para sinais não codificados
    
            %=================%
            %   DEMODULAÇÃO   %
            %=================%
            rxdemod = qamdemod(rxsig,M,'OutputType','bit','UnitAveragePower',true);  % Demodulação QAM do sinal recebido codificado
            rxdemod_uncoded = qamdemod(rxsig_uncoded,M,'OutputType','bit','UnitAveragePower',true);  % Demodulação QAM do sinal recebido não codificado
             
            %=================%
            % DECODIFICADOR DO CANAL %
            %=================%
            rxdecod = double(1-2*rxdemod);    % Conversão para bits suaves (soft bits)
            [rxcbs, actualitr] = nrLDPCDecode(rxdecod,bgn,itrMax);  % Decodificação LDPC do sinal recebido
    
            %=================%
            %     ANÁLISE    %
            %=================%
            % Cálculo dos erros de bit e de bloco para sinais codificados
            Nerrs = sum(rxcbs ~= txcbs);  
            if Nerrs > 0
                Nbiterrs(mod,n) = Nbiterrs(mod,n) + Nerrs;  % Acumula os erros de bit
                Nblkerrs(mod,n) = Nblkerrs(mod,n) + 1;  % Acumula os erros de bloco
            end
    
            % Cálculo dos erros de bit e de bloco para sinais não codificados
            Nerrs = sum(rxdemod_uncoded ~= txcbs);  
            if Nerrs > 0
                Nbiterrs_uncoded(mod,n) = Nbiterrs_uncoded(mod,n) + Nerrs;  % Acumula os erros de bit
                Nblkerrs_uncoded(mod,n) = Nblkerrs_uncoded(mod,n) + 1;  % Acumula os erros de bloco
            end
        end
        
        % Exibe o progresso da simulação para o bloco atual (50% do progresso)
        if rem(block,Nblocks/2) == 0
            fprintf('%d %.0f%% ', mod, block/Nblocks*100)
        end
    end    

    % Cálculo da taxa de erro de bit (BER) para sinais codificados e não codificados
    %BER_uncod(mod,:) = berawgn(SNR-log2(M),'qam',M); 
    %BER_uncod(mod,:) = berawgn(SNR,'qam',M);   
end

toc  % Finaliza o cronômetro

% Cálculo do BER para sinais codificados e não codificados
BER = Nbiterrs./((K-F)*Nblocks);
BER_uncoded = Nbiterrs_uncoded./((K-F)*Nblocks);

% Geração do gráfico de BER versus Eb/No
f = figure;
semilogy(EbNo,BER_uncoded(1,:),'--','color','#0072BD','LineWidth',0.6);  % QPSK não codificado
hold on
semilogy(EbNo,BER(1,:),'*-','color','#0072BD','LineWidth',1.3);  % QPSK codificado

semilogy(EbNo,BER_uncoded(2,:),'--','color','#D95319','LineWidth',0.6);  % 16-QAM não codificado
semilogy(EbNo,BER(2,:),'*-','color','#D95319','LineWidth',1.3);  % 16-QAM codificado

semilogy(EbNo,BER_uncoded(3,:),'--','color','#EDB120','LineWidth',0.6);  % 64-QAM não codificado
semilogy(EbNo,BER(3,:),'*-','color','#EDB120','LineWidth',1.3);  % 64-QAM codificado

semilogy(EbNo,BER_uncoded(4,:),'--','color','#7E2F8E','LineWidth',0.6);  % 256-QAM não codificado
semilogy(EbNo,BER(4,:),'*-','color','#7E2F8E','LineWidth',1.3);  % 256-QAM codificado

hold off  % Finaliza a adição de gráficos

% Adiciona rótulos e legenda ao gráfico
xlabel("Eb/No (dB)");  % Rótulo do eixo x
ylabel("BER");  % Rótulo do eixo y
ylim([10^(-5) 10^(0.1)]);  % Limites do eixo y
xlim([min(EbNo) max(EbNo)]);  % Limites do eixo x
grid on;  % Ativa a grade do gráfico
legend("Uncoded QPSK","NR-LDPC QPSK","Uncoded 16-QAM","NR-LDPC 16-QAM","Uncoded 64-QAM","NR-LDPC 64-QAM","Uncoded 256-QAM","NR-LDPC 256-QAM");  % Legenda
