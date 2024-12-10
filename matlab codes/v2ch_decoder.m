function [rxcbs] = ch_decoder(rxdemod, F, bgn, itrMax)
% Função para realizar a decodificação LDPC em um bloco recebido.

    % Converte os bits recebidos para valores soft (de -1 a +1)
    rxdecod = double(1 - 2 * rxdemod);  % Conversão: 0 -> +1, 1 -> -1

    % Realiza a decodificação LDPC com os parâmetros fornecidos
    [rxcbs, actualitr] = nrLDPCDecode(rxdecod, bgn, itrMax);
    % `actualitr` contém o número real de iterações realizadas (não usado aqui)

end
