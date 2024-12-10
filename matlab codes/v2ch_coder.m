function [txcoded] = ch_coder(txcbs, F, bgn)

    % Gera os bits de preenchimento (fillers), que são -1
    fillers = -1 * ones(F, 1);

    % Adiciona os fillers no final dos blocos de entrada
    txcbs = [txcbs; fillers];

    % Realiza a codificação LDPC usando o MATLAB (bgn especifica o grafo base)
    txcoded = nrLDPCEncode(txcbs, bgn);

    % Remove os bits de preenchimento do bloco codificado
    locs = (txcoded == -1);  % Localiza as posições onde os bits são -1
    txcoded(locs) = [];      % Remove esses bits
end
